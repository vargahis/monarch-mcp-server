# Test Plan: Monarch Money MCP Server

## Context

This MCP server has no tests. Before writing unit tests, we execute a manual test plan against the live Monarch Money API to:
1. Discover bugs by testing real-world scenarios (not just confirming what the code does)
2. Fix all discovered issues
3. Then write unit tests to lock in correct behavior

Code review against the underlying `monarchmoney` library (v1.3.0, community fork) revealed **11 bugs**, including 4 critical ones where tools are completely broken.

## Bugs Discovered During Code Review

### CRITICAL — Tool completely broken on every call

| Bug | Tool | Root Cause | Server Line | Library Line |
|-----|------|-----------|-------------|-------------|
| **A** | `create_transaction` | Passes `description=` kwarg but library has no such param. Library requires `merchant_name` and `category_id` as mandatory positional args, but MCP treats them as optional. | server.py:401 | monarchmoney.py:1603-1612 |
| **B** | `refresh_accounts` | Calls `request_accounts_refresh()` with no args, but library requires `account_ids: List[str]` | server.py:487 | monarchmoney.py:671 |
| **C** | `get_transaction_tags` | Reads `tags.get("tags", [])` but API returns data under `householdTransactionTags` key | server.py:510 | monarchmoney.py:1951 |
| **D** | `get_budgets` | Reads `budgets.get("budgets", [])` but API returns under `budgetData` key with a completely different structure (monthly amounts by category, not flat budget list) | server.py:301 | monarchmoney.py:1206 |

### HIGH — Crashes under specific conditions

| Bug | Tool | Root Cause |
|-----|------|-----------|
| **E** | `get_transactions` with `account_id` | Passes `account_id=<str>` but library expects `account_ids=List[str]` (plural, list) |
| **F** | `get_transactions` with single date | Library requires both `start_date` AND `end_date` or neither |
| **G** | `get_cashflow` with single date | Same as F — library raises if only one date provided |

### MEDIUM — Incorrect data returned silently

| Bug | Tool | Root Cause |
|-----|------|-----------|
| **H** | `get_transactions` -> `is_pending` | Reads `txn.get("isPending")` but GraphQL field is `pending` — always returns `False` |
| **I** | `get_transactions` -> `description` | Reads `txn.get("description")` but no such field in GraphQL response — always returns `null` |
| **J** | `create_transaction` vs `update_transaction` | Create uses `if category_id:` (falsy check) while update uses `if category_id is not None:` (None check) — inconsistent handling of empty strings |

### LOW

| Bug | Notes |
|-----|-------|
| **K** | `MonarchConfig` class defined (server.py:67-74) but never used — dead code |

---

## Test Execution Plan

### Phase 1: Confirm Critical Crashes

Run these first to confirm the 4 completely broken tools.

**TEST 1.1 — `create_transaction` always fails (Bug A)**
```
create_transaction(
  account_id="<any valid account id>",
  amount=-25.99,
  description="Test purchase",
  date="2025-06-15",
  merchant_name="Test Merchant",
  category_id="<any valid category id>"
)
```
- Expected: Error containing "unexpected keyword argument 'description'"
- Confirms: Bug A

**TEST 1.2 — `refresh_accounts` always fails (Bug B)**
```
refresh_accounts()
```
- Expected: Error containing "missing 1 required positional argument: 'account_ids'"
- Confirms: Bug B

**TEST 1.3 — `get_transaction_tags` returns empty (Bug C)**
```
get_transaction_tags()
```
- Expected: Returns `[]` even if tags exist in Monarch web UI
- Confirm by: Checking Monarch web UI -> Settings -> Tags

**TEST 1.4 — `get_budgets` returns empty (Bug D)**
```
get_budgets()
```
- Expected: Returns `[]` even if budgets are configured in Monarch web UI
- Confirm by: Checking Monarch web UI -> Budget page

---

### Phase 2: Verify Working Read Operations

**TEST 2.1 — `get_accounts` happy path**
```
get_accounts()
```
- Verify: Valid JSON array returned, each with `id`, `name`, `type`, `balance`, `institution`, `is_active`
- Cross-check: Count matches Monarch web UI account count
- Cross-check: Balances match web UI (snapshot them at the same time)
- Cross-check: Account names match
- Check: Any account with `type: null` or `institution: null` — is this correct?
- Check: `is_active` is correct for any deactivated accounts

**TEST 2.2 — `get_transactions` happy path (no filters)**
```
get_transactions(limit=10)
```
- Verify: Returns 10 transactions, each with required fields
- Cross-check: Compare the top 5 transactions against Monarch web UI -> Transactions page
- Check specifically: `amount`, `date`, `category`, `merchant`, `account` fields match web UI
- Check: `description` field — expect always `null` (Bug I)
- Check: `is_pending` — if any transaction is pending in web UI but shows `false` here (Bug H)

**TEST 2.3 — `get_transactions` with date range**
```
get_transactions(limit=100, start_date="2025-01-01", end_date="2025-01-31")
```
- Verify: All returned transactions have dates within Jan 2025
- Cross-check: Count against Monarch web UI filtered to Jan 2025

**TEST 2.4 — `get_cashflow` happy path**
```
get_cashflow(start_date="2025-01-01", end_date="2025-01-31")
```
- Verify: Returns JSON with `byCategory`, `byCategoryGroup`, `byMerchant`, `summary` keys
- Cross-check: `summary` -> `sumIncome` and `sumExpense` match Monarch web UI cashflow page for Jan 2025
- Note: This tool returns raw API response (no reformatting), unlike other tools

**TEST 2.5 — `get_account_holdings` happy path**
- Prerequisite: Find a brokerage/investment account from TEST 2.1
```
get_account_holdings(account_id="<brokerage_account_id>")
```
- Verify: Returns holdings data with tickers/values
- Cross-check: A few ticker symbols and values against web UI

---

### Phase 3: Confirm Conditional Failures

**TEST 3.1 — `get_transactions` with `account_id` filter (Bug E)**
- Use an account ID from TEST 2.1
```
get_transactions(limit=10, account_id="<valid_account_id>")
```
- Expected: Error — `account_id` is wrong kwarg name (library expects `account_ids` as a list)
- Confirms: Bug E

**TEST 3.2 — `get_transactions` with only `start_date` (Bug F)**
```
get_transactions(limit=10, start_date="2025-01-01")
```
- Expected: Error "You must specify both a startDate and endDate"
- Confirms: Bug F

**TEST 3.3 — `get_transactions` with only `end_date` (Bug F variant)**
```
get_transactions(limit=10, end_date="2025-12-31")
```
- Expected: Same error as 3.2

**TEST 3.4 — `get_cashflow` with only `start_date` (Bug G)**
```
get_cashflow(start_date="2025-01-01")
```
- Expected: Error "You must specify both a startDate and endDate"
- Confirms: Bug G

---

### Phase 4: Verify Write Operations

**TEST 4.1 — `update_transaction` — update notes (happy path)**
- Get a transaction ID from `get_transactions(limit=1)`
- Note original notes value
```
update_transaction(transaction_id="<txn_id>", notes="MCP test - will revert")
```
- Verify: Response includes updated notes
- Cross-check: Verify in web UI
- Cleanup: Revert with `update_transaction(transaction_id="<txn_id>", notes="<original_notes>")`

**TEST 4.2 — `update_transaction` — no-op (only transaction_id)**
```
update_transaction(transaction_id="<valid_txn_id>")
```
- Expected: Succeeds with no changes (documented library behavior)

**TEST 4.3 — `update_transaction` — invalid transaction_id**
```
update_transaction(transaction_id="nonexistent-id-12345", notes="should fail")
```
- Expected: Graceful error message

**TEST 4.4 — `create_transaction_tag` — happy path**
```
create_transaction_tag(name="MCP-Test-Tag", color="#FF5733")
```
- Expected: Returns created tag with `id`, `name`, `color`
- Cross-check: Verify tag appears in Monarch web UI -> Settings -> Tags
- Save the returned tag ID for TEST 4.7

**TEST 4.5 — `create_transaction_tag` — validation: bad color**
```
create_transaction_tag(name="Bad", color="red")
```
- Expected: `{"error": "Invalid color format..."}`

**TEST 4.6 — `create_transaction_tag` — validation: empty name**
```
create_transaction_tag(name="", color="#FF5733")
```
- Expected: `{"error": "Tag name cannot be empty"}`

**TEST 4.7 — `set_transaction_tags` — apply tag to transaction**
- Use tag ID from TEST 4.4 and a transaction ID
```
set_transaction_tags(transaction_id="<txn_id>", tag_ids=["<tag_id>"])
```
- Expected: Success
- Cross-check: Verify tag appears on transaction in web UI

**TEST 4.8 — `set_transaction_tags` — remove all tags**
```
set_transaction_tags(transaction_id="<txn_id>", tag_ids=[])
```
- Expected: All tags removed from the transaction
- Cross-check: Verify in web UI

---

### Phase 5: Edge Cases and Boundary Testing

**TEST 5.1 — Pagination: page 1 vs page 2**
```
get_transactions(limit=5, offset=0)
get_transactions(limit=5, offset=5)
```
- Verify: No overlapping transaction IDs between pages
- Verify: Page 2 dates are same or older than page 1

**TEST 5.2 — Pagination: very large offset**
```
get_transactions(limit=10, offset=999999)
```
- Expected: Empty array `[]`, no crash

**TEST 5.3 — Limit boundary: limit=0**
```
get_transactions(limit=0)
```
- Expected: Either empty array or API-defined behavior, no crash

**TEST 5.4 — Invalid date format**
```
get_transactions(limit=10, start_date="not-a-date", end_date="also-not")
```
- Expected: Error caught and returned as string, not server crash

**TEST 5.5 — Future dates (empty result)**
```
get_transactions(limit=10, start_date="2030-01-01", end_date="2030-12-31")
```
- Expected: Empty array `[]`

**TEST 5.6 — Holdings for non-investment account**
- Use a checking account ID from TEST 2.1
```
get_account_holdings(account_id="<checking_account_id>")
```
- Expected: Empty result or graceful error

**TEST 5.7 — Holdings for invalid account_id**
```
get_account_holdings(account_id="nonexistent-99999")
```
- Expected: Graceful error message

**TEST 5.8 — Tag validation: 3-digit hex**
```
create_transaction_tag(name="Short", color="#F00")
```
- Expected: Validation error (regex requires 6 hex digits)

**TEST 5.9 — Tag validation: whitespace-only name**
```
create_transaction_tag(name="   ", color="#FF5733")
```
- Expected: `{"error": "Tag name cannot be empty"}`

**TEST 5.10 — Duplicate tag name**
```
create_transaction_tag(name="MCP-Test-Tag", color="#00FF00")
```
- Observe: Does API allow duplicate names?

---

### Phase 6: Authentication

**TEST 6.1 — `check_auth_status`**
```
check_auth_status()
```
- Expected: "Authentication token found in secure keyring storage"

**TEST 6.2 — `debug_session_loading`**
```
debug_session_loading()
```
- Expected: "Token found in keyring (length: N)" with reasonable N

**TEST 6.3 — `setup_authentication`**
```
setup_authentication()
```
- Expected: Multi-line instruction string (pure text, no API call)

---

### Cleanup After Testing

1. Revert any modified transactions (notes, amounts, hide_from_reports)
2. Delete test tags ("MCP-Test-Tag" and any duplicates) via Monarch web UI
3. Remove any test tags from transactions

---

## Summary of Expected Results

| Tool | Status | Bugs |
|------|--------|------|
| `setup_authentication` | Working | -- |
| `check_auth_status` | Working | -- |
| `debug_session_loading` | Working | -- |
| `get_accounts` | Working | Minor: displayName fallback |
| `get_transactions` (no filter) | Partially working | H (is_pending always false), I (description always null) |
| `get_transactions` (account filter) | Broken | E (wrong param name) |
| `get_transactions` (single date) | Broken | F (must provide both dates) |
| `get_budgets` | Broken | D (wrong response key + wrong data model) |
| `get_cashflow` (both dates) | Working | -- |
| `get_cashflow` (single date) | Broken | G (must provide both dates) |
| `get_account_holdings` | Working | -- |
| `create_transaction` | Broken | A (wrong params, missing required args) |
| `update_transaction` | Working | J (minor inconsistency) |
| `refresh_accounts` | Broken | B (missing required arg) |
| `get_transaction_tags` | Broken | C (wrong response key) |
| `create_transaction_tag` | Working | -- |
| `set_transaction_tags` | Working | -- |

**5 tools completely broken, 1 partially broken, 8 working**
