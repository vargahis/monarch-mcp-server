# Phase 12 — Analytics Tools (5 tests)

## 12.1 — get_credit_history: returns data or empty
Call `get_credit_history()`.
**Expected:** JSON response. May have empty `creditHistory` list if not configured, but should not error.

## 12.2 — get_transactions: search filter
Call `get_transactions(limit=5, search="test")`.
**Expected:** JSON array (may be empty). Verify the call succeeds without error.

## 12.3 — get_transactions: category_ids filter
Call `get_transactions(limit=5, category_ids=["{valid_category_id}"])`.
**Expected:** JSON array. All returned transactions should have the specified category.

## 12.4 — get_transactions: boolean filters
Call `get_transactions(limit=5, is_recurring=True)`.
**Expected:** JSON array. If any results, they should have `is_recurring: true`.

## 12.5 — get_transactions: account_id + account_ids conflict
Call `get_transactions(account_id="acc-1", account_ids=["acc-2"])`.
**Expected:** JSON with `error` key about not using both parameters.
