# Phase 10 — Read-Only Tools (9 tests)

## 10.1 — get_transactions_summary: returns aggregate stats
Call `get_transactions_summary()`.
**Expected:** JSON response with summary data (count, sum, or similar aggregation fields).

## 10.2 — get_subscription_details: returns subscription info
Call `get_subscription_details()`.
**Expected:** JSON with subscription details including at least one of: `id`, `paymentSource`, `hasPremiumEntitlement`.

## 10.3 — get_institutions: returns connected institutions
Call `get_institutions()`.
**Expected:** JSON with institution/credential data. May have `credentials` key with a list.

## 10.4 — get_cashflow_summary: no dates
Call `get_cashflow_summary()`.
**Expected:** JSON with cashflow summary data.

## 10.5 — get_cashflow_summary: with dates
Call `get_cashflow_summary(start_date="2025-01-01", end_date="2025-01-31")`.
**Expected:** JSON with cashflow summary for the specified period.

## 10.6 — get_cashflow_summary: only start_date -> error
Call `get_cashflow_summary(start_date="2025-01-01")`.
**Expected:** JSON with `error` key about requiring both dates.

## 10.7 — get_recurring_transactions: no dates
Call `get_recurring_transactions()`.
**Expected:** JSON with recurring transaction data.

## 10.8 — get_recurring_transactions: with dates
Call `get_recurring_transactions(start_date="2025-01-01", end_date="2025-12-31")`.
**Expected:** JSON with recurring transaction data for the period.

## 10.9 — get_recurring_transactions: only end_date -> error
Call `get_recurring_transactions(end_date="2025-12-31")`.
**Expected:** JSON with `error` key.

