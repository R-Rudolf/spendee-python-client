import pytest
from datetime import datetime, timedelta


def test_get_transaction_invalid_wallet_raises(firestore_client, sample_transaction_id, invalid_uuid):
    with pytest.raises(Exception):
        firestore_client.get_transaction(invalid_uuid, sample_transaction_id)


def test_get_transaction_invalid_txid_raises(firestore_client, sample_wallet_id, invalid_uuid):
    with pytest.raises(Exception):
        firestore_client.get_transaction(sample_wallet_id, invalid_uuid)


def test_list_transactions_invalid_fields_raises(firestore_client, sample_wallet_id, sample_date_range):
    with pytest.raises(Exception):
        firestore_client.list_transactions(sample_wallet_id, start=sample_date_range[0], fields=['bad'])


def test_list_transactions_invalid_filters_raises(firestore_client, sample_wallet_id, sample_date_range):
    with pytest.raises(Exception):
        firestore_client.list_transactions(sample_wallet_id, start=sample_date_range[0], filters=[{'no':'field'}])


def test_aggregate_transactions_runs(firestore_client, sample_wallet_id, sample_date_range):
    total = firestore_client.aggregate_transactions(sample_wallet_id, start=sample_date_range[0])
    assert isinstance(total, float)


def test_edit_transaction_invalid_category_raises(firestore_client, editable_transaction_id_with_wallet):
    sample_wallet_id, sample_transaction_id = editable_transaction_id_with_wallet
    with pytest.raises(ValueError):
        firestore_client.edit_transaction(sample_wallet_id, sample_transaction_id, {'category': 'NonExisting'})


def test_edit_transaction_invalid_label_raises(firestore_client, editable_transaction_id_with_wallet):
    sample_wallet_id, sample_transaction_id = editable_transaction_id_with_wallet
    with pytest.raises(ValueError):
        firestore_client.edit_transaction(sample_wallet_id, sample_transaction_id, {'labels': '+NonExisting'})

