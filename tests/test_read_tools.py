"""Tests for simple read-only tools: summary, subscription, institutions, cashflow_summary."""
# pylint: disable=missing-function-docstring

import json

from monarch_mcp_server.server import (
    get_transactions_summary,
    get_subscription_details,
    get_institutions,
    get_cashflow_summary,
)


# ===================================================================
# get_transactions_summary
# ===================================================================


SAMPLE_SUMMARY = {
    "allTransactions": {
        "totalCount": 500,
        "results": [],
    },
    "transactionsSummary": {
        "avg": -45.50,
        "count": 500,
        "max": 5000.00,
        "maxExpense": -2500.00,
        "sum": -22750.00,
        "sumIncome": 12000.00,
        "sumExpense": -34750.00,
    },
}


def test_summary_happy(mock_monarch_client):
    mock_monarch_client.get_transactions_summary.return_value = SAMPLE_SUMMARY

    result = json.loads(get_transactions_summary())

    assert "transactionsSummary" in result
    mock_monarch_client.get_transactions_summary.assert_called_once()


def test_summary_error(mock_monarch_client):
    mock_monarch_client.get_transactions_summary.side_effect = Exception("API down")

    result = get_transactions_summary()

    assert "Error" in result


# ===================================================================
# get_subscription_details
# ===================================================================


SAMPLE_SUBSCRIPTION = {
    "subscription": {
        "id": "sub-1",
        "paymentSource": "stripe",
        "referralCode": "ABC123",
        "isOnFreeTrial": False,
        "hasPremiumEntitlement": True,
    }
}


def test_subscription_happy(mock_monarch_client):
    mock_monarch_client.get_subscription_details.return_value = SAMPLE_SUBSCRIPTION

    result = json.loads(get_subscription_details())

    assert result["subscription"]["hasPremiumEntitlement"] is True
    mock_monarch_client.get_subscription_details.assert_called_once()


def test_subscription_error(mock_monarch_client):
    mock_monarch_client.get_subscription_details.side_effect = Exception("API down")

    result = get_subscription_details()

    assert "Error" in result


# ===================================================================
# get_institutions
# ===================================================================


SAMPLE_INSTITUTIONS = {
    "credentials": [
        {
            "id": "cred-1",
            "institution": {"name": "Chase", "status": "GOOD"},
            "accounts": [
                {"id": "acc-1", "displayName": "Checking"},
            ],
        }
    ]
}


def test_institutions_happy(mock_monarch_client):
    mock_monarch_client.get_institutions.return_value = SAMPLE_INSTITUTIONS

    result = json.loads(get_institutions())

    assert len(result["credentials"]) == 1
    assert result["credentials"][0]["institution"]["name"] == "Chase"
    mock_monarch_client.get_institutions.assert_called_once()


def test_institutions_empty(mock_monarch_client):
    mock_monarch_client.get_institutions.return_value = {"credentials": []}

    result = json.loads(get_institutions())

    assert result["credentials"] == []


def test_institutions_error(mock_monarch_client):
    mock_monarch_client.get_institutions.side_effect = Exception("API down")

    result = get_institutions()

    assert "Error" in result


# ===================================================================
# get_cashflow_summary
# ===================================================================


SAMPLE_CASHFLOW_SUMMARY = {
    "summary": [
        {
            "summary": {
                "sumIncome": 6000,
                "sumExpense": -4000,
                "savings": 2000,
                "savingsRate": 0.33,
            }
        }
    ]
}


def test_cashflow_summary_no_dates(mock_monarch_client):
    mock_monarch_client.get_cashflow_summary.return_value = SAMPLE_CASHFLOW_SUMMARY

    result = json.loads(get_cashflow_summary())

    assert "summary" in result
    mock_monarch_client.get_cashflow_summary.assert_called_once_with(limit=100)


def test_cashflow_summary_with_dates(mock_monarch_client):
    mock_monarch_client.get_cashflow_summary.return_value = SAMPLE_CASHFLOW_SUMMARY

    get_cashflow_summary(start_date="2025-01-01", end_date="2025-01-31")

    mock_monarch_client.get_cashflow_summary.assert_called_once_with(
        limit=100, start_date="2025-01-01", end_date="2025-01-31"
    )


def test_cashflow_summary_custom_limit(mock_monarch_client):
    mock_monarch_client.get_cashflow_summary.return_value = SAMPLE_CASHFLOW_SUMMARY

    get_cashflow_summary(limit=50)

    mock_monarch_client.get_cashflow_summary.assert_called_once_with(limit=50)


def test_cashflow_summary_only_start_error():
    result = json.loads(get_cashflow_summary(start_date="2025-01-01"))
    assert "error" in result


def test_cashflow_summary_only_end_error():
    result = json.loads(get_cashflow_summary(end_date="2025-01-31"))
    assert "error" in result


def test_cashflow_summary_error(mock_monarch_client):
    mock_monarch_client.get_cashflow_summary.side_effect = Exception("API down")

    result = get_cashflow_summary()

    assert "Error" in result
