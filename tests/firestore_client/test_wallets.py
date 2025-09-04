import pytest
from datetime import datetime


def test_list_wallets_runs(firestore_client):
    wallets = firestore_client.list_wallets()
    assert isinstance(wallets, list)


def test_get_wallet_balance_invalid_wallet_id_raises(firestore_client, invalid_uuid):
    with pytest.raises(Exception):
        firestore_client.get_wallet_balance(invalid_uuid)


def test_get_wallet_balance_invalid_date_format_raises(firestore_client, sample_wallet_id, invalid_date_format):
    with pytest.raises(Exception):
        firestore_client.get_wallet_balance(sample_wallet_id, date=invalid_date_format)


def test_get_wallet_balance_runs_with_dates(firestore_client, sample_wallet_id):
    assert 10000 < firestore_client.get_wallet_balance(sample_wallet_id, date="2025-08-26T23:59:59Z")
