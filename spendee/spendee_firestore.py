from decimal import Decimal
from google.auth.credentials import Credentials
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from .firebase_client import FirebaseClient

import json
import datetime
from jwt import JWT, exceptions as jwt_exceptions

# Improvement ideas:
# - Implement token expiration check in CustomFirebaseCredentials
# - Implement refresh logic in CustomFirebaseCredentials
# - Cache refresh token between sessions
# - Check if device UUID should be stable or if it can be removed
# - Cache user data (like wallets) to avoid unnecessary API calls

# Note: User document has field: firestoreDataExportDone, which is True.
# Which is a trace of the migration from REST API to Firestore.


class CustomFirebaseCredentials(Credentials):
    """Custom credentials that use existing Firebase access token"""
    
    def __init__(self, firebase_client):
        super().__init__()
        self.firebase_client = firebase_client
        self.token = firebase_client.access_token
        # self.expiry = None
        
    def refresh(self, request):
        return_value = self.firebase_client._token_refresh()
        self.token = self.firebase_client.access_token
        return return_value # not sure about this
    
    def expired(self):
        self.firebase_client._token_expired()


class SpendeeFirestore(FirebaseClient):

    def __init__(self, email: str, password: str, base_url: str = 'https://api.spendee.com/', google_client_id: str = 'AIzaSyCCJPDxVNVFEARQ-LxH7q2aZtdQJGGFO84'):
        self.base_url = base_url
        super().__init__(email, password, google_client_id)
        self.authenticate()
        self.credentials = CustomFirebaseCredentials(self)
        self.client = firestore.Client(project="spendee-app", credentials=self.credentials)
        self.jwt = JWT() # https://github.com/GehirnInc/python-jwt/blob/master/jwt/jwt.py
        access_token_data = self.jwt.decode(self.access_token, do_verify=False)
        self.user_id = access_token_data.get('user_id', None)
        self.email = access_token_data.get('email', None)
        self.user_name = access_token_data.get('name', None)

    def _token_refresh(self):
        if self._token_expired():
            self._access_token = self.get_access_token()
            self.credentials.token = self._access_token
            return True
        return False

    # not tested, return value is possibly wrong
    def _token_expired(self):
        try:
            self.jwt.decode(self.access_token, do_verify=False, do_time_check=True)
            return True
        except jwt_exceptions.JWTDecodeError as e:
            return False
        # from credentials.py
        # skewed_expiry = self.expiry - _helpers.REFRESH_THRESHOLD
        # return _helpers.utcnow() >= skewed_expiry


    def _get_raw_category(self, category_id: str, as_json: bool = False):
        obj = self.client.document(f"users/{self.user_id}/categories/{category_id}").get().to_dict()
        return self.as_json(obj) if as_json else obj


    def _get_raw_label(self, label_id: str, as_json: bool = False):
        obj = self.client.document(f"users/{self.user_id}/labels/{label_id}").get().to_dict()
        return self.as_json(obj) if as_json else obj


    def _list_raw_categories(self, as_json: bool = False):
        raw_data = [
            x.to_dict()
            for x in self.client.collection(f'users/{self.user_id}/categories').get()
        ]
        return self.as_json(raw_data) if as_json else raw_data
    

    def list_categories(self, as_json: bool = False):
        """
        Returns a list of categories for the user.
        If as_json is True, returns the data as a JSON string.
        """
        data = []
        for raw_data in self.client.collection(f'users/{self.user_id}/categories').get():
            data.append({
                'id': raw_data.get('path').get('category'),
                'name': raw_data.get('name'),
                'type': raw_data.get('type'),
            })

        return self.as_json(data) if as_json else data


    def _list_raw_labels(self, as_json: bool = False):
        raw_data = [
            x.to_dict()
            for x in self.client.collection(f'users/{self.user_id}/labels').get()
        ]
        return self.as_json(raw_data) if as_json else raw_data


    def list_labels(self, as_json: bool = False):
        """
        Returns a list of labels for the user.
        If as_json is True, returns the data as a JSON string.
        """
        data = []
        for raw_data in self.client.collection(f'users/{self.user_id}/labels').get():
            data.append({
                'id': raw_data.get('path').get('label'),
                # attention: here I switch from fieldName 'text' to 'name', for consistency with categories
                'name': raw_data.get('text'),
            })

        return self.as_json(data) if as_json else data


    def get_wallet_balance(self, wallet_id: str, start: str = None, end: str = None):
        """
        Returns the balance of the wallet with the given ID for a specific timeframe.
        The start and end parameters should be in ISO 8601 format. If not set, no filtering is done.
        """
        query = self.client.collection(f'users/{self.user_id}/wallets/{wallet_id}/transactions')

        if start:
            query = query.where(filter=FieldFilter("madeAt", ">=", datetime.datetime.fromisoformat(start)))
            starting_balance = 0
        else:
            starting_balance = self.client.document(f'users/{self.user_id}/wallets/{wallet_id}').get('startingBalance', 0)
        if end:
            query = query.where(filter=FieldFilter("madeAt", "<=", datetime.datetime.fromisoformat(end)))
        query = query.order_by("madeAt")
        transactions = query.stream()
        # Could not use aggregation queries here, because each transaction has a different exchange rate, which needs multiplication.
        # https://firebase.google.com/docs/firestore/query-data/aggregation-queries#use_the_sum_aggregation

        total = 0
        for transaction in transactions:
            data = transaction.to_dict()
            usd_value = data.get('usdValue', {})

            amount = Decimal(str(usd_value.get('amount', '0')))
            exchange_rate = Decimal(str(usd_value.get('exchangeRate', '0')))

            converted_value = amount * exchange_rate
            total += converted_value
        
        return round(total + Decimal(str(starting_balance)))


    def list_wallets(self):
        raw_data = [
            x.to_dict()
            for x in self.client.collection(f'users/{self.user_id}/wallets').get()
        ]
        return_data = []
        for wallet in raw_data:
            if wallet["status"] != 'active':
                continue
            return_data.append({
                'id': wallet['path']['wallet'],
                'name': wallet['name'],
                'type': wallet['type'],
                'currency': wallet['currency'],
                'updatedAt': wallet.get('updatedAt', None),
                'visibleCategories': wallet.get('visibleCategories', []),
                'startingBalance': wallet['startingBalance'],
            })
        return return_data


    def _json_serializer(self, obj):
        # Handle Firestore DatetimeWithNanoseconds objects
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")


    def as_json(self, obj):
        return json.dumps(obj, indent=2, default=self._json_serializer, ensure_ascii=False)


    def _get_raw_transaction(self, wallet_id: str, transaction_id: str, as_json: bool = False):
        obj = self.client.document(f"users/{self.user_id}/wallets/{wallet_id}/transactions/{transaction_id}").get().to_dict()
        return self.as_json(obj) if as_json else obj
