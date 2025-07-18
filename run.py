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

# accounts = spendee.wallet_get_all()
# print('Available accounts:')
# for acc in accounts:
#     print(f"- {acc.get('name', 'Unnamed')} (ID: {acc.get('id')}, Balance: {acc.get('balance')} {acc.get('currency')})")

spendee = SpendeeFirestore(EMAIL, PASSWORD)


#print(spendee.list_labels(as_json=True))
print(spendee.list_categories(as_json=True))
#print(spendee.get_raw_transaction('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', 'a15d8379-6884-4e7d-a007-a1748b62e9d3', as_json=True))
#print(spendee.get_raw_transaction('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7', 'd2b4caa7-12eb-4c04-a744-d2bf7e02bdd2', as_json=True))
# wallets = spendee.list_wallets()
# for wallet in wallets:
#     print(wallet['name'])
#     print(spendee.get_wallet_balance(wallet['id'], start='2025-07-02T00:00:00Z'))

# Example usage of logger for debug/info
# logger.debug('Debug message')
# logger.info('Info message')
