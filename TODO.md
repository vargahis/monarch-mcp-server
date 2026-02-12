# TODO: Test and Fix MCP Tools

Track progress across sessions. Update checkboxes as work proceeds.

## Phase 1: Confirm Critical Crashes
- [ ] TEST 1.1 — `create_transaction` always fails (Bug A)
- [ ] TEST 1.2 — `refresh_accounts` always fails (Bug B)
- [ ] TEST 1.3 — `get_transaction_tags` returns empty (Bug C)
- [ ] TEST 1.4 — `get_budgets` returns empty (Bug D)

## Phase 2: Verify Working Read Operations
- [ ] TEST 2.1 — `get_accounts` happy path
- [ ] TEST 2.2 — `get_transactions` happy path (no filters)
- [ ] TEST 2.3 — `get_transactions` with date range
- [ ] TEST 2.4 — `get_cashflow` happy path
- [ ] TEST 2.5 — `get_account_holdings` happy path

## Phase 3: Confirm Conditional Failures
- [ ] TEST 3.1 — `get_transactions` with `account_id` filter (Bug E)
- [ ] TEST 3.2 — `get_transactions` with only `start_date` (Bug F)
- [ ] TEST 3.3 — `get_transactions` with only `end_date` (Bug F variant)
- [ ] TEST 3.4 — `get_cashflow` with only `start_date` (Bug G)

## Phase 4: Verify Write Operations
- [ ] TEST 4.1 — `update_transaction` — update notes
- [ ] TEST 4.2 — `update_transaction` — no-op
- [ ] TEST 4.3 — `update_transaction` — invalid transaction_id
- [ ] TEST 4.4 — `create_transaction_tag` — happy path
- [ ] TEST 4.5 — `create_transaction_tag` — bad color validation
- [ ] TEST 4.6 — `create_transaction_tag` — empty name validation
- [ ] TEST 4.7 — `set_transaction_tags` — apply tag
- [ ] TEST 4.8 — `set_transaction_tags` — remove all tags

## Phase 5: Edge Cases and Boundary Testing
- [ ] TEST 5.1 — Pagination: page 1 vs page 2
- [ ] TEST 5.2 — Pagination: very large offset
- [ ] TEST 5.3 — Limit boundary: limit=0
- [ ] TEST 5.4 — Invalid date format
- [ ] TEST 5.5 — Future dates (empty result)
- [ ] TEST 5.6 — Holdings for non-investment account
- [ ] TEST 5.7 — Holdings for invalid account_id
- [ ] TEST 5.8 — Tag validation: 3-digit hex
- [ ] TEST 5.9 — Tag validation: whitespace-only name
- [ ] TEST 5.10 — Duplicate tag name

## Phase 6: Authentication
- [ ] TEST 6.1 — `check_auth_status`
- [ ] TEST 6.2 — `debug_session_loading`
- [ ] TEST 6.3 — `setup_authentication`

## Cleanup
- [ ] Revert modified transactions
- [ ] Delete test tags via Monarch web UI
- [ ] Remove test tags from transactions

---

## Bug Fixes (after test confirmation)
- [ ] Fix Bug A — `create_transaction`: wrong params, missing required args
- [ ] Fix Bug B — `refresh_accounts`: missing required `account_ids` arg
- [ ] Fix Bug C — `get_transaction_tags`: wrong response key (`householdTransactionTags`)
- [ ] Fix Bug D — `get_budgets`: wrong response key + wrong data model
- [ ] Fix Bug E — `get_transactions` account filter: `account_id` -> `account_ids` (list)
- [ ] Fix Bug F — `get_transactions` single date: validate both dates required
- [ ] Fix Bug G — `get_cashflow` single date: validate both dates required
- [ ] Fix Bug H — `get_transactions` `is_pending`: field name `pending` not `isPending`
- [ ] Fix Bug I — `get_transactions` `description`: field doesn't exist in GraphQL response
- [ ] Fix Bug J — `create_transaction` vs `update_transaction` truthiness inconsistency
- [ ] Fix Bug K — Remove dead `MonarchConfig` class

## Unit Tests (after all fixes)
- [ ] Design unit test architecture (mocking strategy, fixtures)
- [ ] Write unit tests for all tools
- [ ] Verify tests pass
