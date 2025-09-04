import pytest


def test_live_smoke(firestore_client):
    # Simple smoke that live endpoints work
    wallets = firestore_client.list_wallets()
    assert isinstance(wallets, list)
    firestore_client.list_categories()
    firestore_client.list_labels()
