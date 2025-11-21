#!/usr/bin/env python3
"""
Shared fixtures for firestore_client tests.

This module provides fixtures specific to the firestore_client test suite,
building upon the global fixtures from the parent conftest.py.
"""

import pytest
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

@pytest.fixture(scope="session")
def firestore_client():
    """
    Shared SpendeeFirestore client for firestore_client tests.
    
    This fixture creates a single authenticated client that can be reused
    across all firestore_client test modules.
    """
    from spendee import SpendeeFirestore
    
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    
    if not email or not password:
        pytest.fail("EMAIL and PASSWORD environment variables required")
    else:
        client = SpendeeFirestore(email, password)
        return client


@pytest.fixture(scope="session")
def sample_wallet_id(firestore_client):
    """
    Get a sample wallet ID for testing.
    
    Returns a specific wallet ID that's known to exist in the test environment.
    """
    wallets = firestore_client.list_wallets()
    if not wallets:
        pytest.skip("No wallets available for testing")
    
    # Try to find a specific wallet ID, or use the first one
    target_wallet_id = '5668018f-2c8d-41b0-9ef9-fbaa6518891d'
    for wallet in wallets:
        if wallet['id'] == target_wallet_id:
            return target_wallet_id
    pytest.fail(f"Target wallet ID {target_wallet_id} not found in available wallets")


@pytest.fixture(scope="session")
def sample_transaction_id(firestore_client, sample_wallet_id):
    """
    Get a sample transaction ID for testing.
    
    Returns a transaction ID from the sample wallet.
    """
    transactions = firestore_client.list_transactions(
        sample_wallet_id, 
        fields=['id'], 
        start=(datetime.now() - timedelta(days=60)).isoformat(), 
        limit=1
    )
    
    if not transactions:
        pytest.skip("No transactions available for testing")
    
    return transactions[0]['id']

@pytest.fixture(scope="session")
def editable_transaction_id_with_wallet(firestore_client):
    """
    Get a wallet ID and transaction ID pair for testing edit operations.
    
    Returns a tuple of (wallet_id, transaction_id) that can be used for editing.
    """
    # Specific known editable transaction
    transaction_id = 'fa08917b-9181-48df-a183-23635730bbbe'
    wallet_id = '5668018f-2c8d-41b0-9ef9-fbaa6518891d'
    
    # Verify the transaction exists
    try:
        firestore_client.get_transaction(wallet_id, transaction_id)
        return wallet_id, transaction_id
    except Exception:
        pytest.skip("Editable transaction not available for testing")

@pytest.fixture(scope="session")
def test_categories(firestore_client):
    """
    Get all categories for testing.
    
    Returns the list of all available categories.
    """
    return firestore_client.list_categories()

@pytest.fixture(scope="session")
def test_labels(firestore_client):
    """
    Get all labels for testing.
    
    Returns the list of all available labels.
    """
    return firestore_client.list_labels()

@pytest.fixture
def sample_date_range():
    """
    Sample date range for testing.
    
    Returns a tuple of (start_date, end_date) in ISO format.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    return start_date.isoformat(), end_date.isoformat()

@pytest.fixture
def invalid_uuid():
    """
    Invalid UUID for testing error cases.
    
    Returns a string that is not a valid UUID.
    """
    return 'invalid-uuid'

@pytest.fixture
def invalid_date_format():
    """
    Invalid date format for testing error cases.
    
    Returns a string that is not a valid date format.
    """
    return 'bad-date'
