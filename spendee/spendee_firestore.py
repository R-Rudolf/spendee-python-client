from google.auth.credentials import Credentials
from google.cloud import firestore
from .firebase_client import FirebaseClient

class CustomFirebaseCredentials(Credentials):
    """Custom credentials that use existing Firebase access token"""
    
    def __init__(self, access_token):
        super().__init__()
        self.token = access_token
        
    def refresh(self, request):
        # todo
        pass
    
    def expired(self):
        # Check if token is expired
        pass

class SpendeeFirestore(FirebaseClient):
    def __init__(self, email: str, password: str, base_url: str = 'https://api.spendee.com/', google_client_id: str = 'AIzaSyCCJPDxVNVFEARQ-LxH7q2aZtdQJGGFO84'):
        self.base_url = base_url
        super().__init__(email, password, google_client_id)
        self.authenticate()
        self.credentials = CustomFirebaseCredentials(self.get_access_token())
        self.client = firestore.Client(project="spendee-app", credentials=self.credentials)

    def example_call(self):
        # example = self.client\
        #     .collection('users')\
        #     .document('af150597-5b96-4f8b-9eb3-0b2e0aa72a81')\
        #     .collection('wallets')\
        #     .document('b368c5c2-68fe-4f98-9d4f-08e0cdca57a7')\
        #     .collection('transactions')\
        #     .document('26624eef-6956-4cbc-8aee-68e4fb97396b')
        example = self.client.document('users/af150597-5b96-4f8b-9eb3-0b2e0aa72a81/wallets/b368c5c2-68fe-4f98-9d4f-08e0cdca57a7/transactions/26624eef-6956-4cbc-8aee-68e4fb97396b')
        return example.get().to_dict()
