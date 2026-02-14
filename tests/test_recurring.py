"""Tests for get_recurring_transactions tool."""
# pylint: disable=missing-function-docstring

import json

from monarch_mcp_server.server import get_recurring_transactions


SAMPLE_RECURRING = {
    "recurringTransactions": [
        {
            "id": "rec-1",
            "amount": -15.99,
            "merchant": {"name": "Netflix"},
            "frequency": "monthly",
            "account": {"displayName": "Checking"},
            "category": {"name": "Entertainment"},
        },
        {
            "id": "rec-2",
            "amount": -1200.00,
            "merchant": {"name": "Landlord"},
            "frequency": "monthly",
            "account": {"displayName": "Checking"},
            "category": {"name": "Housing"},
        },
    ]
}


def test_recurring_no_dates(mock_monarch_client):
    mock_monarch_client.get_recurring_transactions.return_value = SAMPLE_RECURRING

    result = json.loads(get_recurring_transactions())

    assert len(result["recurringTransactions"]) == 2
    mock_monarch_client.get_recurring_transactions.assert_called_once_with()


def test_recurring_with_dates(mock_monarch_client):
    mock_monarch_client.get_recurring_transactions.return_value = SAMPLE_RECURRING

    get_recurring_transactions(start_date="2025-01-01", end_date="2025-12-31")

    mock_monarch_client.get_recurring_transactions.assert_called_once_with(
        start_date="2025-01-01", end_date="2025-12-31"
    )


def test_recurring_only_start_error():
    result = json.loads(get_recurring_transactions(start_date="2025-01-01"))
    assert "error" in result


def test_recurring_only_end_error():
    result = json.loads(get_recurring_transactions(end_date="2025-12-31"))
    assert "error" in result


def test_recurring_empty(mock_monarch_client):
    mock_monarch_client.get_recurring_transactions.return_value = {
        "recurringTransactions": []
    }

    result = json.loads(get_recurring_transactions())

    assert result["recurringTransactions"] == []


def test_recurring_error(mock_monarch_client):
    mock_monarch_client.get_recurring_transactions.side_effect = Exception("API down")

    result = get_recurring_transactions()

    assert "Error" in result
