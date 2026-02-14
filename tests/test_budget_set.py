"""Tests for set_budget_amount tool."""
# pylint: disable=missing-function-docstring

import json

from monarch_mcp_server.server import set_budget_amount


def test_set_budget_with_category(mock_monarch_client):
    mock_monarch_client.set_budget_amount.return_value = {
        "updateOrCreateBudgetItem": {"id": "budget-1"}
    }

    result = json.loads(set_budget_amount(amount=500.0, category_id="cat-1"))

    assert "updateOrCreateBudgetItem" in result
    mock_monarch_client.set_budget_amount.assert_called_once_with(
        amount=500.0,
        timeframe="month",
        apply_to_future=False,
        category_id="cat-1",
    )


def test_set_budget_with_group(mock_monarch_client):
    mock_monarch_client.set_budget_amount.return_value = {
        "updateOrCreateBudgetItem": {"id": "budget-2"}
    }

    result = json.loads(set_budget_amount(amount=2000.0, category_group_id="grp-1"))

    assert "updateOrCreateBudgetItem" in result
    mock_monarch_client.set_budget_amount.assert_called_once_with(
        amount=2000.0,
        timeframe="month",
        apply_to_future=False,
        category_group_id="grp-1",
    )


def test_set_budget_both_ids_error():
    result = json.loads(
        set_budget_amount(amount=100.0, category_id="cat-1", category_group_id="grp-1")
    )
    assert "error" in result
    assert "exactly one" in result["error"].lower()


def test_set_budget_neither_id_error():
    result = json.loads(set_budget_amount(amount=100.0))
    assert "error" in result
    assert "exactly one" in result["error"].lower()


def test_set_budget_apply_to_future(mock_monarch_client):
    mock_monarch_client.set_budget_amount.return_value = {
        "updateOrCreateBudgetItem": {"id": "budget-1"}
    }

    set_budget_amount(amount=300.0, category_id="cat-1", apply_to_future=True)

    call_kwargs = mock_monarch_client.set_budget_amount.call_args[1]
    assert call_kwargs["apply_to_future"] is True


def test_set_budget_with_start_date(mock_monarch_client):
    mock_monarch_client.set_budget_amount.return_value = {
        "updateOrCreateBudgetItem": {"id": "budget-1"}
    }

    set_budget_amount(
        amount=400.0, category_id="cat-1", start_date="2025-02-01"
    )

    call_kwargs = mock_monarch_client.set_budget_amount.call_args[1]
    assert call_kwargs["start_date"] == "2025-02-01"


def test_set_budget_error(mock_monarch_client):
    mock_monarch_client.set_budget_amount.side_effect = Exception("Invalid category")

    result = set_budget_amount(amount=100.0, category_id="bad-cat")

    assert "Error" in result
