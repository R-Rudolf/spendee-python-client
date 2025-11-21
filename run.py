#!/usr/bin/env python
import os
from dotenv import load_dotenv
from spendee import SpendeeApi
from spendee import SpendeeFirestore
import logging

# Load environment variables from .env file
load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

# Set up logging
file_handler = logging.FileHandler('debug.log', mode='a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, stream_handler])
logger = logging.getLogger(__name__)

if not EMAIL or not PASSWORD:
    logger.error('Please set EMAIL and PASSWORD in your .env file.')
    exit(1)

# spendee = SpendeeApi(EMAIL, PASSWORD)

spendee = SpendeeFirestore(EMAIL, PASSWORD)


logger.info(spendee.list_wallets())


# print("Raiffeisen Étkezés sum in 2025.08: " + str(spendee.aggregate_transactions(
#     wallet_id='b368c5c2-68fe-4f98-9d4f-08e0cdca57a7',
#     start='2025-08-01T00:00:00Z',
#     end='2025-08-31T23:59:59Z',
#     filters=[{"field": "category", "op": "=", "value": "Étkezés"}],
# )))# -30000 < x < -180000

# print("Raiffeisen Szigetspicc label sum in 2025.08: " + str(spendee.aggregate_transactions(
#     wallet_id='b368c5c2-68fe-4f98-9d4f-08e0cdca57a7',
#     start='2025-08-01T00:00:00Z',
#     end='2025-08-31T23:59:59Z',
#     filters=[{"field": "labels", "op": "array-contains", "value": "szigetspicc"}],
# ))) # -50000 < x < -60000


#print(spendee._get_raw_transaction('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', 'a15d8379-6884-4e7d-a007-a1748b62e9d3', as_json=True))
#print(spendee._get_raw_transaction('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', 'd2b4caa7-12eb-4c04-a744-d2bf7e02bdd2', as_json=True))

# Example raw document dumps using the new helper. Paste these outputs back here to expand the schema.
#print(spendee._get_raw_document(f"users/{spendee.user_id}", as_json=True))

# ---
#print("rafi balance: ", spendee.get_wallet_balance('Rafi'))

#print(spendee.list_transactions('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', start='2025-08-01T00:00:00Z', filters=[{"field": "amount", "op": ">=", "value": 5000}], as_json=True))
#print(spendee.list_transactions('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', start='2025-08-01T00:00:00Z', filters=[{"field": "note", "op": "~=", "value": "GYED"}], as_json=True))
#print(spendee.list_transactions('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', start='2025-08-01T00:00:00Z', filters=[{"field": "category", "op": "=", "value": "Fizetés"}], as_json=True))


# print(spendee.list_transactions('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', start='2025-08-15T00:00:00Z',
#     filters=[
#         #{"field": "category", "op": "=", "value": "Other"},
#         {"field": "amount", "op": ">", "value": 0}
#     ],
#     fields=["id", "note", "category"]))

# Example: Update transaction note and category

# updated_transaction = spendee.edit_transaction(
#     wallet_id='b368c5c2-68fe-4f98-9d4f-08e0cdca57a7',
#     transaction_id='d2b4caa7-12eb-4c04-a744-d2bf7e02bdd2',
#     updates={
#         #'note': 'ADOMÁNY, Bogár Péter István2',
#         #'category': "Other"  # Use category name, not ID
#         #'category': "Kafetéria"
#         'category': "Szórakozás"
#     }
# )
#print(spendee._get_transation_labels('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', '875ebb1c-e03d-433f-a6c9-be0316f6c838', as_json=True))

# print(spendee.list_transactions('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', start='2025-08-01T00:00:00Z', filters=[{"field": "category", "op": "=", "value": None}], fields=["id", "note", "category"], as_json=True))
# print(spendee.list_transactions('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', start='2025-08-08', end="2025-08-13", filters=[{"field": "type", "op": "=", "value": "expense"}], fields=["id", "note", "category"], as_json=True))


# Simple label tests (one add, one remove, then multiple ops)
# Replace wallet_id and transaction_id with real IDs before running
# wallet_id = 'b368c5c2-68fe-4f98-9d4f-08e0cdca57a7'
# transaction_id = 'd2b4caa7-12eb-4c04-a744-d2bf7e02bdd2'

# print(spendee.get_transaction(wallet_id, transaction_id))
# print("Adding label 'McDonalds'")
# print(spendee.edit_transaction(wallet_id=wallet_id, transaction_id=transaction_id, updates={'labels': '+McDonalds'}))
# print(spendee.get_transaction(wallet_id, transaction_id))

# print("\n --- TEST CASE: Adding label 'McDonalds'")
# print(spendee.edit_transaction(wallet_id=wallet_id, transaction_id=transaction_id, updates={'labels': '+McDonalds'}))
# print(spendee.get_transaction(wallet_id, transaction_id))

# print("\n --- TEST CASE: Removing label 'Rossmann'")
# print(spendee.edit_transaction(wallet_id=wallet_id, transaction_id=transaction_id, updates={'labels': '-Rossmann'}))
# print(spendee.get_transaction(wallet_id, transaction_id))

# print("\n --- TEST CASE: Adding label 'Rossmann' and removing 'McDonalds' in one go")
# print(spendee.edit_transaction(wallet_id=wallet_id, transaction_id=transaction_id, updates={'labels': '+Rossmann,-McDonalds'}))
# print(spendee.get_transaction(wallet_id, transaction_id))
