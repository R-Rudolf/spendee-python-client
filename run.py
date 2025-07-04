import os
from dotenv import load_dotenv
from spendee import SpendeeApi
from spendee import SpendeeFirestore

# Load environment variables from .env file
load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

if not EMAIL or not PASSWORD:
    print('Please set EMAIL and PASSWORD in your .env file.')
    exit(1)

# spendee = SpendeeApi(EMAIL, PASSWORD)

# accounts = spendee.wallet_get_all()
# print('Available accounts:')
# for acc in accounts:
#     print(f"- {acc.get('name', 'Unnamed')} (ID: {acc.get('id')}, Balance: {acc.get('balance')} {acc.get('currency')})")

spendee = SpendeeFirestore(EMAIL, PASSWORD)

print(spendee.example_call())
