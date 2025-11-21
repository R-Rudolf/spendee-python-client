import pytest


def test_aggregate_transactions_category_filter_runs(firestore_client, sample_wallet_id):
    """Aggregate by category.

    Verifies the call completes and returns a float value.
    """
    total = firestore_client.aggregate_transactions(
        wallet_id=sample_wallet_id,
        start='2025-11-17T00:00:00Z',
        end='2025-11-17T23:59:59Z',
        filters={"category__eq": "Groceries"},
    )

    assert isinstance(total, float)
    assert total == -4.0


def test_aggregate_transactions_label_filter_runs(firestore_client, sample_wallet_id):
    """Aggregate by label.

    Verifies the call completes and returns a float value.
    """
    total = firestore_client.aggregate_transactions(
        wallet_id=sample_wallet_id,
        start='2025-11-17T00:00:00Z',
        end='2025-11-17T23:59:59Z',
        filters={"labels__contains": "Coffee ☕"},
    )

    assert isinstance(total, float)
    assert total == -4.0
