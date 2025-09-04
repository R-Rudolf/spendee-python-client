import pytest


class TestSpendeeFirestoreAccountInit:
    """Test suite for SpendeeFirestore class using live data connection."""
    
    def test_list_wallets(self, firestore_client):
        """Test listing wallets returns expected data structure."""
        # Call the list_wallets method
        wallets = firestore_client.list_wallets()
        
        # Assert that wallets is a list
        assert isinstance(wallets, list), "list_wallets should return a list"
        
        # Assert that we have at least one wallet (assuming user has wallets)
        assert len(wallets) > 0, "User should have at least one wallet"
        
        # Check structure of each wallet
        for wallet in wallets:
            # Required fields
            assert 'id' in wallet, "Wallet should have 'id' field"
            assert 'name' in wallet, "Wallet should have 'name' field"
            assert 'type' in wallet, "Wallet should have 'type' field"
            assert 'currency' in wallet, "Wallet should have 'currency' field"
            
            # Field types
            assert isinstance(wallet['id'], str), "Wallet ID should be a string"
            assert isinstance(wallet['name'], str), "Wallet name should be a string"
            assert isinstance(wallet['type'], str), "Wallet type should be a string"
            assert isinstance(wallet['currency'], str), "Wallet currency should be a string"
            
            # Optional fields
            if 'updatedAt' in wallet:
                assert wallet['updatedAt'] is not None, "updatedAt should not be None if present"
            
            # Validate wallet ID format (should be a UUID)
            assert len(wallet['id']) == 36, "Wallet ID should be a UUID (36 characters)"
            
            # Validate currency format (should be 3-letter code)
            assert len(wallet['currency']) == 3, "Currency should be a 3-letter code"
            
            # Validate wallet type (should be one of common types)
            valid_types = ['cash', 'bank']
            assert wallet['type'] in valid_types, f"Wallet type should be one of {valid_types}"
        
        # Test that wallet names are unique
        wallet_names = [wallet['name'] for wallet in wallets]
        assert len(wallet_names) == len(set(wallet_names)), "Wallet names should be unique"
        
        # Test that wallet IDs are unique
        wallet_ids = [wallet['id'] for wallet in wallets]
        assert len(wallet_ids) == len(set(wallet_ids)), "Wallet IDs should be unique"
        
        print(f"Successfully retrieved {len(wallets)} wallets:")
        for wallet in wallets:
            print(f"  - {wallet['name']} ({wallet['type']}, {wallet['currency']})")
