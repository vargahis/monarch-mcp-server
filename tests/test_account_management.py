"""Tests for account management tools: create, update, delete, history, snapshots."""
# pylint: disable=missing-function-docstring

import json

from monarch_mcp_server.server import (
    create_manual_account,
    update_account,
    delete_account,
    get_account_history,
    get_recent_account_balances,
    get_account_snapshots_by_type,
    get_aggregate_snapshots,
    get_account_type_options,
    get_credit_history,
)


# ===================================================================
# create_manual_account
# ===================================================================


def test_create_account_happy(mock_monarch_client):
    mock_monarch_client.create_manual_account.return_value = {
        "createManualAccount": {"id": "acc-new", "displayName": "Savings"}
    }

    result = json.loads(
        create_manual_account(
            account_name="Savings",
            account_type="depository",
            account_sub_type="savings",
            is_in_net_worth=True,
            account_balance=1000.0,
        )
    )

    assert result["createManualAccount"]["id"] == "acc-new"
    mock_monarch_client.create_manual_account.assert_called_once_with(
        account_type="depository",
        account_sub_type="savings",
        is_in_net_worth=True,
        account_name="Savings",
        account_balance=1000.0,
    )


def test_create_account_default_balance(mock_monarch_client):
    mock_monarch_client.create_manual_account.return_value = {
        "createManualAccount": {"id": "acc-new"}
    }

    create_manual_account(
        account_name="Test",
        account_type="loan",
        account_sub_type="personal",
        is_in_net_worth=False,
    )

    call_kwargs = mock_monarch_client.create_manual_account.call_args[1]
    assert call_kwargs["account_balance"] == 0


def test_create_account_error(mock_monarch_client):
    mock_monarch_client.create_manual_account.side_effect = Exception(
        "Invalid type"
    )

    result = create_manual_account(
        account_name="Bad",
        account_type="invalid",
        account_sub_type="bad",
        is_in_net_worth=True,
    )

    assert "Error" in result


# ===================================================================
# update_account
# ===================================================================


def test_update_account_name(mock_monarch_client):
    mock_monarch_client.update_account.return_value = {
        "id": "acc-1",
        "displayName": "New Name",
    }

    result = json.loads(
        update_account(account_id="acc-1", account_name="New Name")
    )

    assert result["displayName"] == "New Name"
    call_kwargs = mock_monarch_client.update_account.call_args[1]
    assert call_kwargs["account_id"] == "acc-1"
    assert call_kwargs["account_name"] == "New Name"


def test_update_account_balance(mock_monarch_client):
    mock_monarch_client.update_account.return_value = {
        "id": "acc-1",
        "currentBalance": 5000.0,
    }

    result = json.loads(
        update_account(account_id="acc-1", account_balance=5000.0)
    )

    assert result["currentBalance"] == 5000.0


def test_update_account_noop(mock_monarch_client):
    mock_monarch_client.update_account.return_value = {"id": "acc-1"}

    result = json.loads(update_account(account_id="acc-1"))

    assert result["id"] == "acc-1"
    call_kwargs = mock_monarch_client.update_account.call_args[1]
    assert call_kwargs == {"account_id": "acc-1"}


def test_update_account_multi_field(mock_monarch_client):
    mock_monarch_client.update_account.return_value = {"id": "acc-1"}

    update_account(
        account_id="acc-1",
        account_name="Updated",
        include_in_net_worth=False,
        hide_from_summary_list=True,
    )

    call_kwargs = mock_monarch_client.update_account.call_args[1]
    assert call_kwargs["account_name"] == "Updated"
    assert call_kwargs["include_in_net_worth"] is False
    assert call_kwargs["hide_from_summary_list"] is True


def test_update_account_error(mock_monarch_client):
    mock_monarch_client.update_account.side_effect = Exception("Not found")

    result = update_account(account_id="bad-id", account_name="X")

    assert "Error" in result


# ===================================================================
# delete_account
# ===================================================================


def test_delete_account_happy(mock_monarch_client):
    mock_monarch_client.delete_account.return_value = None

    result = json.loads(delete_account(account_id="acc-1"))

    assert result["deleted"] is True
    assert result["account_id"] == "acc-1"
    mock_monarch_client.delete_account.assert_called_once_with("acc-1")


def test_delete_account_error(mock_monarch_client):
    mock_monarch_client.delete_account.side_effect = Exception("Account not found")

    result = delete_account(account_id="bad-id")

    assert "Error" in result


# ===================================================================
# get_account_history
# ===================================================================


def test_account_history_happy(mock_monarch_client):
    mock_monarch_client.get_account_history.return_value = {
        "accountHistory": [
            {"date": "2025-01-01", "balance": 1000},
            {"date": "2025-01-02", "balance": 1050},
        ]
    }

    result = json.loads(get_account_history(account_id="acc-1"))

    assert len(result["accountHistory"]) == 2
    mock_monarch_client.get_account_history.assert_called_once_with("acc-1")


def test_account_history_error(mock_monarch_client):
    mock_monarch_client.get_account_history.side_effect = Exception("Not found")

    result = get_account_history(account_id="bad-id")

    assert "Error" in result


# ===================================================================
# get_recent_account_balances
# ===================================================================


def test_recent_balances_no_date(mock_monarch_client):
    mock_monarch_client.get_recent_account_balances.return_value = {
        "recentAccountBalances": []
    }

    result = json.loads(get_recent_account_balances())

    mock_monarch_client.get_recent_account_balances.assert_called_once_with()


def test_recent_balances_with_date(mock_monarch_client):
    mock_monarch_client.get_recent_account_balances.return_value = {
        "recentAccountBalances": [{"date": "2025-01-01", "balance": 1000}]
    }

    get_recent_account_balances(start_date="2025-01-01")

    mock_monarch_client.get_recent_account_balances.assert_called_once_with(
        start_date="2025-01-01"
    )


# ===================================================================
# get_account_snapshots_by_type
# ===================================================================


def test_snapshots_by_type_month(mock_monarch_client):
    mock_monarch_client.get_account_snapshots_by_type.return_value = {
        "snapshots": []
    }

    result = json.loads(
        get_account_snapshots_by_type(start_date="2025-01-01", timeframe="month")
    )

    mock_monarch_client.get_account_snapshots_by_type.assert_called_once_with(
        "2025-01-01", "month"
    )


def test_snapshots_by_type_year(mock_monarch_client):
    mock_monarch_client.get_account_snapshots_by_type.return_value = {
        "snapshots": []
    }

    get_account_snapshots_by_type(start_date="2020-01-01", timeframe="year")

    mock_monarch_client.get_account_snapshots_by_type.assert_called_once_with(
        "2020-01-01", "year"
    )


def test_snapshots_by_type_invalid_timeframe():
    result = json.loads(
        get_account_snapshots_by_type(start_date="2025-01-01", timeframe="week")
    )
    assert "error" in result


# ===================================================================
# get_aggregate_snapshots
# ===================================================================


def test_aggregate_snapshots_no_params(mock_monarch_client):
    mock_monarch_client.get_aggregate_snapshots.return_value = {"snapshots": []}

    result = json.loads(get_aggregate_snapshots())

    mock_monarch_client.get_aggregate_snapshots.assert_called_once_with()


def test_aggregate_snapshots_with_dates(mock_monarch_client):
    mock_monarch_client.get_aggregate_snapshots.return_value = {"snapshots": []}

    get_aggregate_snapshots(start_date="2025-01-01", end_date="2025-12-31")

    from datetime import date
    mock_monarch_client.get_aggregate_snapshots.assert_called_once_with(
        start_date=date(2025, 1, 1), end_date=date(2025, 12, 31)
    )


def test_aggregate_snapshots_with_type(mock_monarch_client):
    mock_monarch_client.get_aggregate_snapshots.return_value = {"snapshots": []}

    get_aggregate_snapshots(account_type="depository")

    mock_monarch_client.get_aggregate_snapshots.assert_called_once_with(
        account_type="depository"
    )


# ===================================================================
# get_account_type_options
# ===================================================================


def test_account_type_options_happy(mock_monarch_client):
    mock_monarch_client.get_account_type_options.return_value = {
        "accountTypeOptions": [
            {"type": "depository", "subTypes": ["checking", "savings"]},
        ]
    }

    result = json.loads(get_account_type_options())

    assert len(result["accountTypeOptions"]) == 1
    mock_monarch_client.get_account_type_options.assert_called_once()


# ===================================================================
# get_credit_history
# ===================================================================


def test_credit_history_happy(mock_monarch_client):
    mock_monarch_client.get_credit_history.return_value = {
        "creditHistory": [{"date": "2025-01-01", "score": 750}]
    }

    result = json.loads(get_credit_history())

    assert result["creditHistory"][0]["score"] == 750
    mock_monarch_client.get_credit_history.assert_called_once()


def test_credit_history_empty(mock_monarch_client):
    mock_monarch_client.get_credit_history.return_value = {"creditHistory": []}

    result = json.loads(get_credit_history())

    assert result["creditHistory"] == []
