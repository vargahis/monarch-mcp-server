"""Tests for transaction category tools."""
# pylint: disable=missing-function-docstring

import json
from datetime import datetime

from monarch_mcp_server.server import (
    get_transaction_categories,
    get_transaction_category_groups,
    create_transaction_category,
    delete_transaction_category,
)


SAMPLE_CATEGORIES = {
    "categories": [
        {
            "id": "cat-1",
            "name": "Groceries",
            "order": 0,
            "isSystemCategory": False,
            "isDisabled": False,
            "group": {"id": "grp-1", "name": "Food & Drink", "type": "expense"},
        },
        {
            "id": "cat-2",
            "name": "Salary",
            "order": 0,
            "isSystemCategory": True,
            "isDisabled": False,
            "group": {"id": "grp-2", "name": "Income", "type": "income"},
        },
    ]
}

SAMPLE_GROUPS = {
    "categoryGroups": [
        {"id": "grp-1", "name": "Food & Drink", "order": 0, "type": "expense"},
        {"id": "grp-2", "name": "Income", "order": 1, "type": "income"},
    ]
}


# ===================================================================
# get_transaction_categories
# ===================================================================


def test_get_categories_happy(mock_monarch_client):
    mock_monarch_client.get_transaction_categories.return_value = SAMPLE_CATEGORIES

    result = json.loads(get_transaction_categories())

    assert len(result["categories"]) == 2
    assert result["categories"][0]["name"] == "Groceries"
    mock_monarch_client.get_transaction_categories.assert_called_once()


def test_get_categories_empty(mock_monarch_client):
    mock_monarch_client.get_transaction_categories.return_value = {"categories": []}

    result = json.loads(get_transaction_categories())

    assert result["categories"] == []


def test_get_categories_error(mock_monarch_client):
    mock_monarch_client.get_transaction_categories.side_effect = Exception("API down")

    result = get_transaction_categories()

    assert "Error" in result


# ===================================================================
# get_transaction_category_groups
# ===================================================================


def test_get_category_groups_happy(mock_monarch_client):
    mock_monarch_client.get_transaction_category_groups.return_value = SAMPLE_GROUPS

    result = json.loads(get_transaction_category_groups())

    assert len(result["categoryGroups"]) == 2
    mock_monarch_client.get_transaction_category_groups.assert_called_once()


def test_get_category_groups_empty(mock_monarch_client):
    mock_monarch_client.get_transaction_category_groups.return_value = {
        "categoryGroups": []
    }

    result = json.loads(get_transaction_category_groups())

    assert result["categoryGroups"] == []


# ===================================================================
# create_transaction_category
# ===================================================================


def test_create_category_happy(mock_monarch_client):
    mock_monarch_client.create_transaction_category.return_value = {
        "id": "cat-new",
        "name": "Coffee",
    }

    result = json.loads(create_transaction_category(group_id="grp-1", name="Coffee"))

    assert result["name"] == "Coffee"
    call_kwargs = mock_monarch_client.create_transaction_category.call_args[1]
    assert call_kwargs["group_id"] == "grp-1"
    assert call_kwargs["transaction_category_name"] == "Coffee"
    assert call_kwargs["icon"] == "\u2753"
    assert call_kwargs["rollover_enabled"] is False


def test_create_category_with_rollover(mock_monarch_client):
    mock_monarch_client.create_transaction_category.return_value = {
        "id": "cat-new",
        "name": "Rent",
    }

    result = json.loads(
        create_transaction_category(
            group_id="grp-1",
            name="Rent",
            rollover_enabled=True,
            rollover_start_month="2025-01-01",
        )
    )

    assert result["name"] == "Rent"
    call_kwargs = mock_monarch_client.create_transaction_category.call_args[1]
    assert call_kwargs["rollover_enabled"] is True
    assert call_kwargs["rollover_start_month"] == datetime(2025, 1, 1)


def test_create_category_custom_icon(mock_monarch_client):
    mock_monarch_client.create_transaction_category.return_value = {
        "id": "cat-new",
        "name": "Gaming",
    }

    create_transaction_category(group_id="grp-1", name="Gaming", icon="\U0001F3AE")

    call_kwargs = mock_monarch_client.create_transaction_category.call_args[1]
    assert call_kwargs["icon"] == "\U0001F3AE"


def test_create_category_error(mock_monarch_client):
    mock_monarch_client.create_transaction_category.side_effect = Exception(
        "Group not found"
    )

    result = create_transaction_category(group_id="bad-grp", name="Test")

    assert "Error" in result


# ===================================================================
# delete_transaction_category
# ===================================================================


def test_delete_category_happy(mock_monarch_client):
    mock_monarch_client.delete_transaction_category.return_value = True

    result = json.loads(delete_transaction_category(category_id="cat-1"))

    assert result["deleted"] is True
    assert result["category_id"] == "cat-1"
    mock_monarch_client.delete_transaction_category.assert_called_once_with("cat-1")


def test_delete_category_error(mock_monarch_client):
    mock_monarch_client.delete_transaction_category.side_effect = Exception(
        "Category not found"
    )

    result = delete_transaction_category(category_id="bad-cat")

    assert "Error" in result
