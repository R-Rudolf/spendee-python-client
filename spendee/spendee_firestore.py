from decimal import Decimal
from typing import Callable, Dict, List, Union, Any
from google.auth.credentials import Credentials
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from .firebase_client import FirebaseClient

import json
import datetime
import logging
import re
import uuid

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

    def __init__(self, email: str, password: str, base_url: str = 'https://api.spendee.com/', 
                 google_client_id: str = 'AIzaSyCCJPDxVNVFEARQ-LxH7q2aZtdQJGGFO84'):
        logger.info("Initializing SpendeeFirestore client.")
        self.base_url = base_url
        
        logger.info("Using Firebase authentication.")
        super().__init__(email, password, google_client_id)
        self.authenticate()
        self.credentials = CustomFirebaseCredentials(self)
        self.client = firestore.Client(project="spendee-app", credentials=self.credentials)
        access_token_data = self._jwt_instance.decode(self.access_token, do_verify=False)
        self.user_id = access_token_data.get('user_id', None)
        self.email = access_token_data.get('email', None)
        self.user_name = access_token_data.get('name', None)
        
        # Initialize mappings
        self.wallet_name_map = { x['name']: x['id'] for x in self.list_wallets()}
        categories = self.list_categories()
        self.category_name_map = { x['id']: x['name'] for x in categories}
        self.category_type_map = { x['id']: x['type'] for x in categories}
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
            if "field" not in f or "op" not in f or "value" not in f:
                raise ValueError(f"Invalid filter format: {f}")
            field = f.get("field")
            op = f.get("op")
            filter_value = f.get("value")
            v = value.get(field)
            if op == "array-contains":
                if field != "labels":
                    raise ValueError("array-contains operator is only supported for 'labels' field")
                if filter_value not in v:
                    return False
            elif op == ">":
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
    

    @mcp_tool
    def list_categories(self) -> List[Dict[str, Any]]:
        """
        Returns the list of categories of the user.

        Each category has the fields: id, name, type
        where type can be 'income' or 'expense'
        
        Returns:
            Union[str, List[Dict[str, Any]]]: List of categories or JSON string if as_json=True
        """
        logger.info("Listing categories.")
        data = []
        for raw_data in self.client.collection(f'users/{self.user_id}/categories').get():
            data.append({
                'id': str(raw_data.get('path').get('category')),
                'name': str(raw_data.get('name')),
                'type': str(raw_data.get('type')),
            })
        logger.debug(f"Fetched categories content: {data}")
        return data


    def _list_raw_labels(self, as_json: bool = False):
        logger.info("Listing all raw labels.")
        raw_data = [
            x.to_dict()
            for x in self.client.collection(f'users/{self.user_id}/labels').get()
        ]
        logger.debug(f"Fetched raw labels content: {raw_data}")
        return self.as_json(raw_data) if as_json else raw_data


    @mcp_tool
    def list_labels(self) -> List[Dict[str, str]]:
        """
        Returns the list of labels used by the user.

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
        return data


    @mcp_tool
    def get_wallet_balance(self, wallet_id: str, start: str = None, end: str = None) -> Decimal:
        """Get the balance of a wallet for a specific timeframe.
        The start and end parameters should be in ISO 8601 format. If not set,
        no filtering is done.
        Args:
            wallet_id (str): Name of the wallet. (Should be equal to the results of list_wallets call)
            start (str, optional): Start date in ISO 8601 format.
            end (str, optional): End date in ISO 8601 format.
        Returns:
            Decimal: The balance of the wallet.
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
    def list_wallets(self) -> List[Dict[str, Any]]:
        """List all wallets for the authenticated user. This is required before wallet related calls, to have exact string for names.
        Each wallet is represented by an object with the following fields:
        - id: Unique identifier of the wallet
        - name: Name of the wallet
        - type: Type of the wallet (e.g., cash, bank, etc.)
        - currency: Currency of the wallet
        - updatedAt: Last updated timestamp of the wallet
        
        Returns:
            List[Dict[str, Any]]: List of wallet dictionaries
        """

        # Fetch raw wallet documents (use helper to allow reuse)
        logger.info("Listing wallets.")
        raw_data = self._list_raw_wallets()
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

    def _list_raw_wallets(self, as_json: bool = False):
        """Return raw wallet documents for the authenticated user.

        This helper returns the full document dicts from Firestore without any
        post-processing. It is intended for internal use by other methods that
        need the unmodified wallet documents.
        """
        logger.info("Listing all raw wallets.")
        raw_data = [
            x.to_dict()
            for x in self.client.collection(f'users/{self.user_id}/wallets').get()
        ]
        logger.debug(f"Fetched raw wallets content: {raw_data}")
        return self.as_json(raw_data) if as_json else raw_data


    def _get_raw_transaction(self, wallet_id: str, transaction_id: str, as_json: bool = False):
        logger.info(f"Fetching raw transaction: wallet_id={wallet_id}, transaction_id={transaction_id}")
        obj = self.client.document(f"users/{self.user_id}/wallets/{wallet_id}/transactions/{transaction_id}").get().to_dict()
        logger.debug(f"Fetched raw transaction content: {obj}")
        return self.as_json(obj) if as_json else obj

    def _get_raw_document(self, doc_path: str, as_json: bool = False):
        """
        Fetch any document by its absolute Firestore path under the project, for example:
          - users/{userId}
          - users/{userId}/wallets/{walletId}
          - users/{userId}/categories/{categoryId}
        Returns the dict or JSON string when as_json=True.
        """
        logger.info(f"Fetching raw document: {doc_path}")
        # Support leading/trailing slashes
        doc_path = doc_path.strip('/')
        try:
            obj = self.client.document(doc_path).get().to_dict()
        except Exception as e:
            logger.exception(f"Failed to fetch document {doc_path}: {e}")
            raise
        logger.debug(f"Fetched raw document content for {doc_path}: {obj}")
        return self.as_json(obj) if as_json else obj


    @mcp_tool
    def get_transaction(self, wallet_id: str, transaction_id: str, resolve_category: bool = True, resolve_labels: bool = True) -> Dict[str, Any]:
        """Get a specific transaction by its ID from a wallet.
        Args:
            wallet_id (str): UUID of the wallet.
            transaction_id (str): UUID of the transaction.
            resolve_category (bool, optional): If True, resolves the category to name.
            resolve_labels (bool, optional): If True, resolves the labels to names.
        Returns:
            Dict[str, Any]: The transaction data as a dictionary.
        """
        value = self._get_raw_transaction(wallet_id, transaction_id)
        category_id = value.get("category", "")
        category = category_id
        if resolve_category:
            # Convert category ID to category name using self.category_name_map
            category = self.category_name_map.get(category_id, None)

        labels = self._get_transation_labels(wallet_id, transaction_id, resolve_labels)

        data = {
            "note": value.get("note", ""),
            "madeAt": value.get("madeAt", ""),
            "category": category,
            "type": value.get("type", ""),
            "isPending": value.get("isPending", ""),
            "amount": value.get("amount", ""),
            "labels": labels,
        }

        logger.info(f"Getting transaction: wallet_id={wallet_id}, transaction_id={transaction_id}")
        return data


    def _list_raw_transactions(self, wallet_id: str, start: str, end: str = None, filters: list = None, limit: int = 20, resolve_labels: bool = True, resolve_category: bool = True, as_json: bool = False):
        """
        List raw transactions for a wallet, filtered by date range and dynamic filters.
        
        This method returns all fields from Firestore without any processing (e.g., category IDs are not resolved to names).
        Results are always sorted by 'madeAt' in descending order (most recent transactions first).

        Args:
            wallet_id (str): UUID of the wallet.
            start (str): Start date (ISO 8601, required).
            end (str, optional): End date (ISO 8601).
            filters (list, optional): List of filter dicts, e.g. [{"field": "amount", "op": ">=", "value": 100}].
                The 'field' and 'op' values must be strings.
                Supported operators: "=", "~=", ">", ">=", "<", "<=", "array-contains", where "~=" is regex match and "array-contains" is for labels only.
            limit (int, optional): Max number of transactions to return (default 20).
            as_json (bool, optional): Return as JSON string if True.
        Returns:
            list or str: List of raw transaction dicts or JSON string.
        """
        logger.info(f"Listing raw transactions for wallet_id={wallet_id}, start={start}, end={end}, filters={filters}, limit={limit}")
        query = self.client.collection(f'users/{self.user_id}/wallets/{wallet_id}/transactions')

        # Required start date
        query = query.where(filter=FieldFilter("madeAt", ">=", datetime.datetime.fromisoformat(start)))
        if end:
            query = query.where(filter=FieldFilter("madeAt", "<=", datetime.datetime.fromisoformat(end)))

        # Only order by 'madeAt' (descending), fetch all for post-filtering and limiting
        query = query.order_by("madeAt", direction=firestore.Query.DESCENDING)
        #query._all_descendants = True
        transactions = query.stream()

        results = []
        stored_transactions = []
        for transaction in transactions:
            value = transaction.to_dict()
            # Add the transaction ID to the raw data for consistency
            value["id"] = value.get("path", {}).get("transaction", "")
            category_id = value.get("category", None)
            if resolve_category and category_id is not None:
                # Resolve category ID to category name
                value["category"] = self.category_name_map.get(category_id, None)
            stored_transactions.append(value)

        labels_query = self.client.collection_group('transactionLabels')
        labels_query = labels_query.where(filter=FieldFilter("path.user", "==", self.user_id))
        transactionLabels = [x.to_dict() for x in labels_query.stream()]

        for transaction in stored_transactions:
            transaction["labels"] = [
                self.label_name_map.get(x.get('label'), None) if resolve_labels else x.get('label')
                for x in transactionLabels
                if x.get('path', {}).get('transaction') == transaction.get('id')
            ]

            if not self._matches_filters(transaction, filters):
                continue
            results.append(transaction)
            if limit and len(results) >= limit:
                break

        logger.info(f"Found {len(results)} raw transactions.")
        return self.as_json(results) if as_json else results

    @mcp_tool
    def list_transactions(self,
                          wallet_id: str,
                          start: str,
                          end: str = None,
                          filters: list = None,
                          limit: int = 20,
                          fields: list = ["note", "madeAt", "category", "amount", "labels"]) -> List[Dict[str, Any]]:
        """
        List transactions for a wallet, filtered by date range and dynamic filters.

        Results are always sorted by 'madeAt' in descending order (most recent transactions first).
        Each returned item has the same fields as get_transaction: id, note, madeAt, category (name), isPending, type, amount, labels.
        Optionally, the returned fields can be limited by the 'fields' parameter, default is ["note", "madeAt", "category", "amount"].
        Category IDs are automatically resolved to category names.

        Fields of a transaction (no other fields are supported!):
        - id (str): UUID of the transaction
        - note (str): Transaction note/description
        - madeAt (str): ISO 8601 timestamp of when the transaction was made
        - category (str): Category name
        - isPending (bool): Whether the transaction is pending
        - type (str): Wether the transactions is one of "regular" or "transfer" (across wallets, or out-of-spendee).
        - amount (int): Amount of the transaction in the wallet's currency
        - labels (list): List of label names associated with the transaction. Not supported in filters.

        Args:
            wallet_id (str): UUID of the wallet.
            start (str): Start date (ISO 8601, required).
            end (str, optional): End date (ISO 8601).
            filters (list, optional): List of filter dicts, e.g. [{"field": "amount", "op": ">=", "value": 100}].
                The 'field' and 'op' values must be strings.
                Supported operators: "=", "~=", ">", ">=", "<", "<=", "array-contains", where "~=" is regex match and "array-contains" is for labels only.
                If not provided, use an empty list.
            limit (int, optional): Max number of transactions to return (default 20).
            fields (list, optional): List of field names to include in the result. Only supported fields are allowed.
        Returns:
            List[Dict[str, Any]]: List of transaction dictionaries.
        """
        logger.info(f"Listing transactions for wallet_id={wallet_id}, start={start}, end={end}, filters={filters}, limit={limit}")
        
        # Validate fields parameter
        allowed_fields = {"id", "note", "madeAt", "category", "type", "isPending", "amount", "labels"}
        if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields):
            raise ValueError("'fields' must be a list of strings.")
        unsupported = set(fields) - allowed_fields
        if unsupported:
            raise ValueError(f"Unsupported fields requested: {unsupported}")

        # Get raw transactions first
        raw_transactions = self._list_raw_transactions(wallet_id, start, end, filters, limit, resolve_category=True, resolve_labels=True)
        
        # Process raw transactions to resolve category IDs and apply field filtering
        results = []
        for raw_transaction in raw_transactions:
            # Create processed transaction data matching get_transaction output fields
            data = {
                "id": raw_transaction.get("id", ""),
                "labels": raw_transaction.get("labels", []),
                "note": raw_transaction.get("note", ""),
                "madeAt": raw_transaction.get("madeAt", ""),
                "category": raw_transaction.get("category", ""),
                "type": raw_transaction.get("type", ""),
                "isPending": raw_transaction.get("isPending", ""),
                "amount": raw_transaction.get("amount", ""),
            }
            
            # Apply field filtering
            if fields is not None:
                data = {k: v for k, v in data.items() if k in fields}
            
            results.append(data)

        logger.info(f"Found {len(results)} transactions.")
        return results

    @mcp_tool
    def aggregate_transactions(self, wallet_id: str, start: str, end: str = None, filters: list = []) -> float:
        """
        Aggregate transactions for a wallet, filtered by date range and dynamic filters.
        Returns the total sum of amounts of the matching transactions.

        Args:
            wallet_id (str): UUID of the wallet.
            start (str): Start date (ISO 8601, required).
            end (str, optional): End date (ISO 8601).
            filters (list, optional): List of filter dicts, e.g. [{"field": "amount", "op": ">=", "value": 100}].
                The 'field' and 'op' values must be strings.
                Supported operators: "=", "~=", ">", ">=", "<", "<=", "array-contains", where "~=" is regex match and "array-contains" is for labels only.
                If not provided, use an empty list.
        Returns:
            float: The total sum of amounts of the matching transactions.
        """
        logger.info(f"Aggregating transactions for wallet_id={wallet_id}, start={start}, end={end}, filters={filters}")

        # Get raw transactions first
        raw_transactions = self.list_transactions(wallet_id, start, end, filters, limit=None, fields=["amount"])

        # Sum the amounts
        total_amount = sum(float(tx.get("amount", 0)) for tx in raw_transactions)

        logger.info(f"Total aggregated amount: {total_amount}")
        return total_amount

    def _get_transation_labels(self, wallet_id: str, transaction_id: str, resolve_names: bool = True, as_json: bool = False):
        """
        Get the labels of a specific transaction by its ID from a wallet.
        """
        logger.info(f"Getting transaction labels: wallet_id={wallet_id}, transaction_id={transaction_id}")
        # Query the transactionLabels collection instead of trying to get a single document
        labels = [
            x.get('label')
            for x in self.client.collection(f'users/{self.user_id}/wallets/{wallet_id}/transactions/{transaction_id}/transactionLabels').get()
        ]
        if resolve_names:
            labels = [self.label_name_map.get(label, label) for label in labels]
        return self.as_json(labels) if as_json else labels

    @mcp_tool
    def edit_transaction(self, wallet_id: str, transaction_id: str, updates: Dict[str, Any]) -> None:
        """
        Edit a specific transaction by its ID from a wallet.
        
        Args:
            wallet_id (str): UUID of the wallet.
            transaction_id (str): UUID of the transaction.
            updates (dict): Dictionary containing the fields to update. Supported fields:
                - note (str): Transaction note/description
                - category (str): Category name (will be converted to category ID)
                - labels (str): A single string containing comma-separated operations where each
                    element starts with '+' to add or '-' to remove a label. Example: "+McDonalds,-Rossmann".
                    Labels must already exist for the user; unknown label names will raise ValueError.
        
        Returns:
            None: Operation completes successfully or raises ValueError on error
        Raises:
            ValueError: If the transaction does not exist, or if invalid updates are provided.
        """
        logger.info(f"Editing transaction: wallet_id={wallet_id}, transaction_id={transaction_id}, updates={updates}")
        
        # Get the current transaction data
        current_data = self._get_raw_transaction(wallet_id, transaction_id)
        current_label_ids = self._get_transation_labels(wallet_id, transaction_id, resolve_names=False)
        if not current_data:
            raise ValueError(f"Transaction {transaction_id} not found in wallet {wallet_id}")
        
        # Prepare the update data
        update_data = {}
        
        # Handle each updatable field
        if 'note' in updates:
            update_data['note'] = updates['note']
                
        if 'category' in updates:
            # Convert category name to category ID
            category_name = updates['category']
            category_id = None
            for cat_id, cat_name in self.category_name_map.items():
                if cat_name == category_name:
                    category_id = cat_id
                    break
            if category_id is None:
                raise ValueError(f"Category '{category_name}' not found. Available categories: {list(self.category_name_map.values())}")
            
            category_type = self.category_type_map.get(category_id, None)
            if str(category_type) == 'income' and int(current_data.get('amount', 0)) < 0:
                raise ValueError(f"Cannot change category to income for a transaction with negative amount: {current_data.get('amount', 0)}")
            elif str(category_type) == 'expense' and int(current_data.get('amount', 0)) > 0:
                raise ValueError(f"Cannot change category to expense for a transaction with positive amount: {current_data.get('amount', 0)}")
            elif category_type not in ['income', 'expense']:
                logger.warning(f"Category type '{category_type}' is not valid for transaction: {transaction_id}")
            update_data['category'] = category_id

        # Handle labels operations: single string with comma separated ops, each starting with + or -
        # Example: "+McDonalds,-Rossmann" -> add McDonalds, remove Rossmann
        labels_to_add = set()
        labels_to_delete = set()
        if 'labels' in updates:
            labels_val = updates.get('labels')
            if not isinstance(labels_val, str):
                raise ValueError("'labels' must be a string of comma-separated +Label or -Label operations")

            ops = [s.strip() for s in labels_val.split(',') if s.strip()]
            coll_path = f'users/{self.user_id}/wallets/{wallet_id}/transactions/{transaction_id}/transactionLabels'
            coll = self.client.collection(coll_path)
            for op in ops:
                if len(op) < 2:
                    raise ValueError(f"Invalid label operation: '{op}'")
                action = op[0]
                label_name = op[1:].strip()
                # find label id by name; label must exist
                label_id = None
                for lid, lname in self.label_name_map.items():
                    if lname == label_name:
                        label_id = lid
                        break
                if label_id is None:
                    raise ValueError(f"Label not found: {label_name}")

                if action == '+':
                    if label_id not in current_label_ids:
                        labels_to_add.add(label_id)
                    else:
                        logger.info(f"Label '{label_name}' already present on transaction {transaction_id}, skipping add.")
                elif action == '-':
                    # collect matching label doc refs to delete
                    for doc in coll.where('label', '==', label_id).get():
                        labels_to_delete.add(doc.reference)
                else:
                    raise ValueError(f"Unsupported label action: '{action}'")

        transaction_path = f"users/{self.user_id}/wallets/{wallet_id}/transactions/{transaction_id}"


        batch = self.client.batch()
        for label_id in labels_to_add:
            uuid_str = str(uuid.uuid4())
            label_doc_ref = self.client.collection(f"{transaction_path}/transactionLabels").document(uuid_str)
            batch.set(label_doc_ref, {
                'label': label_id,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'author': self.user_id,
                'modelVersion': 1,
                'path': {
                    'user': self.user_id,
                    'wallet': wallet_id,
                    'transaction': transaction_id,
                    'transactionLabel': uuid_str,
                }
            })
        for label_doc_ref in labels_to_delete:
            batch.delete(label_doc_ref)
        
        doc_ref = self.client.document(transaction_path)
        update_data['updatedAt'] = firestore.SERVER_TIMESTAMP
        batch.set(doc_ref, update_data, merge=True)

        batch.commit()

