import pytest


def test_list_labels_runs(firestore_client):
    # Sanity: should not raise
    labels = firestore_client.list_labels()
    assert isinstance(labels, list)
    assert len(labels) > 0
