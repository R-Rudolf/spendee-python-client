import pytest


def test_list_categories_runs(firestore_client):
    # Sanity: should not raise
    categories = firestore_client.list_categories()
    assert isinstance(categories, list)
    assert len(categories) > 0

