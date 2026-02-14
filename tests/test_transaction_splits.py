"""Tests for transaction split tools."""
# pylint: disable=missing-function-docstring

import json

from monarch_mcp_server.server import get_transaction_splits, update_transaction_splits


SAMPLE_SPLITS = {
    "getTransaction": {
        "id": "txn-1",
        "splitTransactions": [
            {"id": "split-1", "amount": -60.0, "merchant": {"name": "Store A"}},
            {"id": "split-2", "amount": -40.0, "merchant": {"name": "Store B"}},
        ],
    }
}


# ===================================================================
# get_transaction_splits
# ===================================================================


def test_get_splits_happy(mock_monarch_client):
    mock_monarch_client.get_transaction_splits.return_value = SAMPLE_SPLITS

    result = json.loads(get_transaction_splits(transaction_id="txn-1"))

    splits = result["getTransaction"]["splitTransactions"]
    assert len(splits) == 2
    mock_monarch_client.get_transaction_splits.assert_called_once_with("txn-1")


def test_get_splits_empty(mock_monarch_client):
    mock_monarch_client.get_transaction_splits.return_value = {
        "getTransaction": {"id": "txn-1", "splitTransactions": []}
    }

    result = json.loads(get_transaction_splits(transaction_id="txn-1"))

    assert result["getTransaction"]["splitTransactions"] == []


def test_get_splits_error(mock_monarch_client):
    mock_monarch_client.get_transaction_splits.side_effect = Exception(
        "Transaction not found"
    )

    result = get_transaction_splits(transaction_id="bad-id")

    assert "Error" in result


# ===================================================================
# update_transaction_splits
# ===================================================================


def test_update_splits_happy(mock_monarch_client):
    mock_monarch_client.update_transaction_splits.return_value = {
        "updateTransactionSplits": {"id": "txn-1"}
    }

    split_data = [
        {"merchantName": "Store A", "amount": -60.0, "categoryId": "cat-1"},
        {"merchantName": "Store B", "amount": -40.0, "categoryId": "cat-2"},
    ]
    result = json.loads(
        update_transaction_splits(transaction_id="txn-1", split_data=split_data)
    )

    assert "updateTransactionSplits" in result
    mock_monarch_client.update_transaction_splits.assert_called_once_with(
        "txn-1", split_data
    )


def test_update_splits_remove_all(mock_monarch_client):
    mock_monarch_client.update_transaction_splits.return_value = {
        "updateTransactionSplits": {"id": "txn-1"}
    }

    result = json.loads(
        update_transaction_splits(transaction_id="txn-1", split_data=[])
    )

    assert "updateTransactionSplits" in result
    mock_monarch_client.update_transaction_splits.assert_called_once_with("txn-1", [])


def test_update_splits_error(mock_monarch_client):
    mock_monarch_client.update_transaction_splits.side_effect = Exception(
        "Split amounts don't match"
    )

    result = update_transaction_splits(
        transaction_id="txn-1",
        split_data=[{"merchantName": "X", "amount": -50.0, "categoryId": "cat-1"}],
    )

    assert "Error" in result
