from decimal import Decimal
from typing import Callable, Dict
from google.auth.credentials import Credentials
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from .firebase_client import FirebaseClient

import json
import datetime
import logging
import re

# Improvement ideas:
# - Implement token expiration check in CustomFirebaseCredentials
# - Implement refresh logic in CustomFirebaseCredentials
# - Cache refresh token between sessions
# - Check if device UUID should be stable or if it can be removed

# Note: User document has field: firestoreDataExportDone, which is True.
# Which is a trace of the migration from REST API to Firestore.


logger = logging.getLogger(__name__)

# MCP tool registry and decorator
MCP_TOOLS: Dict[str, Callable] = {}
def mcp_tool(func: Callable) -> Callable:
    MCP_TOOLS[func.__name__] = func
    return func

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
        self.category_name_map = { x['id']: x['name'] for x in self.list_categories()}
        self.label_name_map = { x['id']: x['name'] for x in self.list_labels()}
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

    @staticmethod
    def _matches_filters(value, filters):
        for f in filters or []:
            field = f.get("field")
            op = f.get("op")
            filter_value = f.get("value")
            v = value.get(field)
            if op == ">":
                if not (v is not None and float(v) > float(filter_value)):
                    return False
            elif op == ">=":
                if not (v is not None and float(v) >= float(filter_value)):
                    return False
            elif op == "<":
                if not (v is not None and float(v) < float(filter_value)):
                    return False
            elif op == "<=":
                if not (v is not None and float(v) <= float(filter_value)):
                    return False
            elif op == "=":
                if not (str(v) == str(filter_value)):
                    return False
            elif op == "~=":
                if not (v is not None and re.search(str(filter_value), str(v))):
                    return False
            else:
                logger.warning(f"Unsupported filter op: {op}")
                return False
        return True

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
    

    # ...existing code...
    def list_categories(self, as_json: bool = False):
        """
        Returns the list of categories of the user.
        If as_json is True, returns the data as a JSON string.

        Each category has the fields: id, name, type
        where type can be 'income' or 'expense'
        """
        logger.info("Listing categories.")
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


    @mcp_tool
    def list_labels(self, as_json: bool = False):
        """
        Returns the list of labels used by the user.
        If as_json is True, returns the data as a JSON string.

        Each label item has the fields: id, name
        """
        logger.info("Listing labels.")
        data = []
        for raw_data in self.client.collection(f'users/{self.user_id}/labels').get():
            data.append({
                'id': raw_data.get('path').get('label'),
                # attention: here I switch from fieldName 'text' to 'name', for consistency with categories
                'name': raw_data.get('text'),
            })
        logger.debug(f"Fetched labels content: {data}")
        return self.as_json(data) if as_json else data


    @mcp_tool
    def get_wallet_balance(self, wallet_id: str, start: str = None, end: str = None):
        """Get the balance of a wallet for a specific timeframe.
        The start and end parameters should be in ISO 8601 format. If not set,
        no filtering is done.
        Args:
            wallet_id (str): Name of the wallet. (Should be equal to the results of list_wallets call)
            start (str, optional): Start date in ISO 8601 format.
            end (str, optional): End date in ISO 8601 format.
        Returns:
            int: The balance of the wallet.
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


    @mcp_tool
    def list_wallets(self):
        """List all wallets for the authenticated user. This is required before wallet related calls, to have exact string for names.
        Each wallet is represented by an object with the following fields:
        - id: Unique identifier of the wallet
        - name: Name of the wallet
        - type: Type of the wallet (e.g., cash, bank, etc.)
        - currency: Currency of the wallet
        - updatedAt: Last updated timestamp of the wallet
        """

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


    @mcp_tool
    def get_transaction(self, wallet_id: str, transaction_id: str, as_json: bool = False):
        """Get a specific transaction by its ID from a wallet.
        Args:
            wallet_id (str): ID of the wallet.
            transaction_id (str): ID of the transaction.
            as_json (bool, optional): If True, returns the data as a JSON string.
        Returns:
            dict or str: The transaction data, either as a dictionary or JSON string.
        """
        value = self._get_raw_transaction(wallet_id, transaction_id)
        # Convert category ID to category name using self.category_name_map
        category_id = value.get("category", "")
        category_name = self.category_name_map.get(category_id, None)

        data = {
            "note": value.get("note", ""),
            "madeAt": value.get("madeAt", ""),
            "category": category_name,
            "type": value.get("type", ""),
            "isPending": value.get("isPending", ""),
            "amount": value.get("amount", ""),
        }

        logger.info(f"Getting transaction: wallet_id={wallet_id}, transaction_id={transaction_id}")
        return data if not as_json else self.as_json(data)


    @mcp_tool
    def list_transactions(self, wallet_id: str, start: str, end: str = None, filters: list = None, limit: int = 20, fields: list = ["note", "madeAt", "category", "amount"], as_json: bool = False):
        """
        List transactions for a wallet, filtered by date range and dynamic filters.

        Results are always sorted by 'madeAt' in descending order (most recent transactions first).
        Each returned item has the same fields as get_transaction: id, note, madeAt, category (name), type, isPending, amount.
        Optionally, the returned fields can be limited by the 'fields' parameter, default is ["note", "madeAt", "category", "amount"].

        Args:
            wallet_id (str): ID of the wallet.
            start (str): Start date (ISO 8601, required).
            end (str, optional): End date (ISO 8601).
            filters (list, optional): List of filter dicts, e.g. [{"field": "amount", "op": ">=", "value": 100}].
                The 'field' and 'op' values must be strings.
                Supported operators: "=", "~=", ">", ">=", "<", "<=", where "~=" is regex match.
            limit (int, optional): Max number of transactions to return (default 20).
            fields (list, optional): List of field names to include in the result. Only supported fields are allowed.
            as_json (bool, optional): Return as JSON string if True.
        Returns:
            list or str: List of transaction dicts or JSON string.
        """
        logger.info(f"Listing transactions for wallet_id={wallet_id}, start={start}, end={end}, filters={filters}, limit={limit}")
        query = self.client.collection(f'users/{self.user_id}/wallets/{wallet_id}/transactions')

        # Required start date
        query = query.where(filter=FieldFilter("madeAt", ">=", datetime.datetime.fromisoformat(start)))
        if end:
            query = query.where(filter=FieldFilter("madeAt", "<=", datetime.datetime.fromisoformat(end)))

        # Only order by 'madeAt' (descending), fetch all for post-filtering and limiting
        query = query.order_by("madeAt", direction=firestore.Query.DESCENDING)
        transactions = query.stream()

        allowed_fields = {"id", "note", "madeAt", "category", "type", "isPending", "amount"}
        if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields):
            raise ValueError("'fields' must be a list of strings.")
        unsupported = set(fields) - allowed_fields
        if unsupported:
            raise ValueError(f"Unsupported fields requested: {unsupported}")

        results = []
        for transaction in transactions:
            value = transaction.to_dict()
            # Match get_transaction output fields
            category_id = value.get("category", "")
            category_name = self.category_name_map.get(category_id, None)
            if category_name is None:
                logger.warning(f"Category ID {category_id} not found in category_name_map, using None.")
            data = {
                "id": value.get("path", {}).get("transaction", ""),
                "note": value.get("note", ""),
                "madeAt": value.get("madeAt", ""),
                "category": category_name,
                "type": value.get("type", ""),
                "isPending": value.get("isPending", ""),
                "amount": value.get("amount", ""),
            }
            if not self._matches_filters(data, filters):
                continue
            if fields is not None:
                data = {k: v for k, v in data.items() if k in fields}
            results.append(data)
            if len(results) >= limit:
                break

        logger.info(f"Found {len(results)} transactions.")
        return self.as_json(results) if as_json else results
