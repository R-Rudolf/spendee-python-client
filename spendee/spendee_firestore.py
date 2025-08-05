from decimal import Decimal
from google.auth.credentials import Credentials
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from .firebase_client import FirebaseClient

import json
import datetime
import logging

# Improvement ideas:
# - Implement token expiration check in CustomFirebaseCredentials
# - Implement refresh logic in CustomFirebaseCredentials
# - Cache refresh token between sessions
# - Check if device UUID should be stable or if it can be removed

# Note: User document has field: firestoreDataExportDone, which is True.
# Which is a trace of the migration from REST API to Firestore.

logger = logging.getLogger(__name__)

class CustomFirebaseCredentials(Credentials):
    """Custom credentials that use existing Firebase access token"""
    
    def __init__(self, firebase_client):
        super().__init__()
        self.firebase_client = firebase_client
        self.token = firebase_client.access_token
        self.expiry = firebase_client._token_expiration()  # Set expiry from JWT

    # Not validated if refresh really happens after expiry
    def refresh(self, request):
        logger.debug("Refreshing Firebase credentials if needed")
        return_value = self.firebase_client._token_refresh()
        self.token = self.firebase_client.access_token
        self.expiry = self.firebase_client._token_expiration()  # Update expiry
        logger.debug("Firebase credentials refreshed if needed.")
        return return_value # not sure about this
    
    def expired(self):
        logger.info("Checking if Firebase token is expired.")
        return self.firebase_client._token_expired()


class SpendeeFirestore(FirebaseClient):

    def __init__(self, email: str, password: str, base_url: str = 'https://api.spendee.com/', google_client_id: str = 'AIzaSyCCJPDxVNVFEARQ-LxH7q2aZtdQJGGFO84'):
        logger.info("Initializing SpendeeFirestore client.")
        self.base_url = base_url
        super().__init__(email, password, google_client_id)
        self.authenticate()
        self.credentials = CustomFirebaseCredentials(self)
        self.client = firestore.Client(project="spendee-app", credentials=self.credentials)
        access_token_data = self._jwt_instance.decode(self.access_token, do_verify=False)
        self.user_id = access_token_data.get('user_id', None)
        self.email = access_token_data.get('email', None)
        self.user_name = access_token_data.get('name', None)
        self.wallet_name_map = { x['name']: x['id'] for x in self.list_wallets()}
        logger.info(f"SpendeeFirestore initialized for user_id={self.user_id}, email={self.email}")

    def _token_refresh(self):
        logger.debug("Refreshing access token if expired.")
        if self._token_expired():
            self._access_token = self.get_access_token()
            self.credentials.token = self._access_token
            logger.info("Access token refreshed.")
            return True
        logger.debug("Access token is still valid.")
        return False

    def _token_expiration(self):
        """
        Extracts the 'exp' field from the JWT access token and returns it as a datetime object (UTC).
        Returns None if the field is missing or token is invalid.
        """
        try:
            payload = self._jwt_instance.decode(self.access_token, do_verify=False)
            exp = payload.get('exp')
            if exp is not None:
                exp_time = datetime.datetime.fromtimestamp(exp, datetime.timezone.utc)
                logger.debug(f"Token expiration time: {exp_time}")
                return exp_time
        except Exception as e:
            logger.warning(f"Failed to extract 'exp' from JWT: {e}")
        return None

    def _token_expired(self):
        logger.debug("Checking if access token is expired.")
        expiry = self._token_expiration()
        if expiry is None:
            logger.info("Could not determine token expiry, assuming expired.")
            return True
        now = datetime.datetime.now(datetime.timezone.utc)  # Make now timezone-aware
        if now >= expiry:
            logger.info("Access token is expired.")
            return True
        logger.debug("Access token is valid.")
        return False

    def _json_serializer(self, obj):
        # Handle Firestore DatetimeWithNanoseconds objects
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")


    def as_json(self, obj):
        return json.dumps(obj, indent=2, default=self._json_serializer, ensure_ascii=False)

    # --- Spendee API methods ---

    def _get_raw_category(self, category_id: str, as_json: bool = False):
        logger.info(f"Fetching raw category: {category_id}")
        obj = self.client.document(f"users/{self.user_id}/categories/{category_id}").get().to_dict()
        logger.debug(f"Fetched raw category content: {obj}")
        return self.as_json(obj) if as_json else obj


    def _get_raw_label(self, label_id: str, as_json: bool = False):
        logger.info(f"Fetching raw label: {label_id}")
        obj = self.client.document(f"users/{self.user_id}/labels/{label_id}").get().to_dict()
        logger.debug(f"Fetched raw label content: {obj}")
        return self.as_json(obj) if as_json else obj


    def _list_raw_categories(self, as_json: bool = False):
        logger.info("Listing all raw categories.")
        raw_data = [
            x.to_dict()
            for x in self.client.collection(f'users/{self.user_id}/categories').get()
        ]
        logger.debug(f"Fetched raw categories content: {raw_data}")
        return self.as_json(raw_data) if as_json else raw_data
    

    def list_categories(self, as_json: bool = False):
        logger.info("Listing categories.")
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
        logger.debug(f"Fetched categories content: {data}")
        return self.as_json(data) if as_json else data


    def _list_raw_labels(self, as_json: bool = False):
        logger.info("Listing all raw labels.")
        raw_data = [
            x.to_dict()
            for x in self.client.collection(f'users/{self.user_id}/labels').get()
        ]
        logger.debug(f"Fetched raw labels content: {raw_data}")
        return self.as_json(raw_data) if as_json else raw_data


    def list_labels(self, as_json: bool = False):
        logger.info("Listing labels.")
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
        logger.debug(f"Fetched labels content: {data}")
        return self.as_json(data) if as_json else data


    def get_wallet_balance(self, wallet_id: str, start: str = None, end: str = None):
        """
        Returns the balance of the wallet with the given wallet_id for a specific timeframe.
        The start and end parameters should be in ISO 8601 format. If not set, no filtering is done.
        """
        logger.info(f"Calculating balance for wallet_id: {wallet_id}")
        query = self.client.collection(f'users/{self.user_id}/wallets/{wallet_id}/transactions')

        if start:
            query = query.where(filter=FieldFilter("madeAt", ">=", datetime.datetime.fromisoformat(start)))
            starting_balance = 0
        else:
            starting_balance = self.client.document(f'users/{self.user_id}/wallets/{wallet_id}').get().to_dict()['startingBalance']

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
        
        logger.info(f"Total balance calculated: {total + Decimal(str(starting_balance))}")
        return round(total + Decimal(str(starting_balance)))


    def list_wallets(self):
        logger.info("Listing wallets.")
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
                #'visibleCategories': wallet.get('visibleCategories', []),
                #'startingBalance': wallet['startingBalance'],
            })
        logger.info(f"Active wallets found: {len(return_data)}")
        logger.debug(f"Fetched wallets content: {return_data}")
        return return_data


    def _get_raw_transaction(self, wallet_id: str, transaction_id: str, as_json: bool = False):
        logger.info(f"Fetching raw transaction: wallet_id={wallet_id}, transaction_id={transaction_id}")
        obj = self.client.document(f"users/{self.user_id}/wallets/{wallet_id}/transactions/{transaction_id}").get().to_dict()
        logger.debug(f"Fetched raw transaction content: {obj}")
        return self.as_json(obj) if as_json else obj
