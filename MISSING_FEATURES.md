# Missing Features in Monarch MCP Server

This document lists all features from the `monarchmoneycommunity` Python library that are **NOT** exposed in the MCP server, or are only partially exposed with missing parameters.

## Summary Statistics

- **Total library methods**: 48
- **MCP tools exposed**: 37 (includes 3 auth helper tools not from library)
- **Library methods exposed**: 34
- **Missing library methods**: 10
- **Partially exposed (missing parameters)**: 2
- **Overall library coverage**: ~71%

---

## 1. Completely Missing Methods

### Authentication & Session Management (3 methods)

❌ **`interactive_login()`**
- Interactive login for iPython environments

❌ **`save_session(filename: Optional[str] = None)`**
- Save session to file manually

❌ **`load_session(filename: Optional[str] = None)`**
- Load session from file manually

**Note**: `login()`, `multi_factor_authenticate()`, and `delete_session()` are used internally but not exposed as tools.

---

### Account Refresh (2 methods)

❌ **`is_accounts_refresh_complete(account_ids: Optional[List[str]] = None)`**
- Check if account refresh is complete

❌ **`request_accounts_refresh_and_wait(account_ids: Optional[List[str]] = None, timeout: int = 300, delay: int = 10)`**
- Request refresh and wait for completion with configurable timeout

**Note**: `refresh_accounts()` is exposed but does not accept an `account_ids` parameter.

---

### Transactions (1 method)

❌ **`upload_attachment(transaction_id: str, file_content: bytes, filename: str)`**
- Upload an attachment to a transaction

---

### Transaction Categories (1 method)

❌ **`delete_transaction_categories(category_ids: List[str])`**
- Batch delete multiple categories (single delete via `delete_transaction_category` is exposed)

---

### Other (3 methods)

❌ **`upload_account_balance_history(account_id: str, csv_content: List[BalanceHistoryRow], timeout: int = 300, delay: int = 10)`**
- Upload historical balance data via CSV

❌ **`gql_call(operation: str, graphql_query: DocumentNode, variables: Dict[str, Any] = {})`**
- Direct GraphQL query execution (advanced use)

❌ **`set_timeout(timeout_secs: int)`**
- Set request timeout

❌ **`set_token(token: str)`**
- Set authentication token directly

---

## 2. Partially Exposed (Missing Parameters)

### ⚠️ `refresh_accounts()` — Missing Parameter

**Missing (1)**:
- ❌ `account_ids` — list of specific account IDs to refresh

**Library signature**:
```python
request_accounts_refresh(account_ids: List[str]) -> bool
```

**Impact**: Cannot selectively refresh specific accounts; always refreshes all.

---

### ⚠️ `get_budgets()` — Missing Parameter

**Missing (1)**:
- ❌ `use_legacy_goals` — use legacy goals format

**Library signature**:
```python
get_budgets(start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            use_legacy_goals: Optional[bool] = False,
            use_v2_goals: Optional[bool] = True)
```
