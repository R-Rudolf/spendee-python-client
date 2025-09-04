import pytest


def test_aggregate_transactions_category_filter_runs(firestore_client, sample_wallet_id):
    """Aggregate by category (matches the `run.py` example for "Étkezés").

    Verifies the call completes and returns a float value.
    """
    total = firestore_client.aggregate_transactions(
        wallet_id=sample_wallet_id,
        start='2025-08-01T00:00:00Z',
        end='2025-08-31T23:59:59Z',
        #filters=[{"field": "category", "op": "=", "value": "Étkezés"}],
        #filters=[TransactionFilter(field="category", op="=", value="Étkezés")],
        filters={"category__eq": "Étkezés"},
    )

    assert isinstance(total, float)
    assert total > -180000
    assert total < -3000


def test_aggregate_transactions_label_filter_runs(firestore_client, sample_wallet_id):
    """Aggregate by label (matches the `run.py` example for label `szigetspicc`).

    Verifies the call completes and returns a float value.
    """
    total = firestore_client.aggregate_transactions(
        wallet_id=sample_wallet_id,
        start='2025-08-01T00:00:00Z',
        end='2025-08-31T23:59:59Z',
        #filters=[{"field": "labels", "op": "array-contains", "value": "szigetspicc"}],
        #filters=[TransactionFilter(field="labels", op="array-contains", value="szigetspicc")],  
        filters={"labels__contains": "szigetspicc"},
    )

    assert isinstance(total, float)
    assert total > -80000
    assert total < -5000
