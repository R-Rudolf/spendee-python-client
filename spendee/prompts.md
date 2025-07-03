# discussions

firebase SDK authentication:
 - https://claude.ai/share/74c50295-ffad-4659-bd21-0c5b3810b9d6

# Context cache
---
I am a Spendee user, which is a webpage and app on mobile, to track financial transactions gathered from multiple bank accounts.
They do not support a documented API, but I want to implement an MCP server to enable an AI agent to work collaboratively fetching data or refining transaction categories or descriptions.
For that I explored an old github repo, which implemented authentication and REST API calls available back then.
Unfortunately those API calls return outdated data somewhy, like bank account data is 1 week older, than what is available on the webpage.
So I started to investigate the web traffic of the webpage and explored that it uses firestore.
I never used firestore before, so I need explanations and guidance throghout our work.
The client I write will be implemented in python.
---
Here are some key code snippets to understand some aspects of it:

Config identified from web traffic:
```json
"google_client_id": "AIzaSyCCJPDxVNVFEARQ-LxH7q2aZtdQJGGFO84",
"config": {
    "apiKey": "AIzaSyCCJPDxVNVFEARQ-LxH7q2aZtdQJGGFO84",
    "authDomain": "spendee-app.firebaseapp.com",
    "databaseURL": "https://spendee-app.firebaseio.com",
    "projectId": "spendee-app",
    "storageBucket": "spendee-app.appspot.com",
    "messagingSenderId": "320191066468",
    "appId": "1:320191066468:web:b91a0a66620b3912",
    "measurementId": "G-6XWQZRWRLK"
}
```

Working authentication layer extracted from former open source project:
```python
from requests import Session

class FirebaseClient(Session):
    def __init__(self, email, password, google_client_id: str = 'AIzaSyCCJPDxVNVFEARQ-LxH7q2aZtdQJGGFO84'):
        self.email = email
        self.password = password
        self.google_client_id = google_client_id
        self._access_token = None
        self._refresh_token = None
        self._device_uuid = None
        super().__init__()

    def authenticate(self):
        """
        Handles the full authentication flow: gets refresh token, access token, and device UUID.
        """
        self._refresh_token = self.get_refresh_token()
        self._access_token = self.get_access_token()
        self._device_uuid = self.get_device_uuid_from_login()

    def get_refresh_token(self):
        url = f'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={self.google_client_id}'
        payload = {
            'email': self.email,
            'password': self.password,
            'returnSecureToken': True,
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['refreshToken']

    def get_access_token(self):
        url = f'https://securetoken.googleapis.com/v1/token?key={self.google_client_id}'
        payload = {
            'refresh_token': self._refresh_token,
            'grant_type': 'refresh_token',
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print("Access Token:", data['access_token'])  # Debugging line to check the access token
        return data['access_token']

    def get_device_uuid_from_login(self):
        # This should be implemented in the child class if needed, as it may require a specific API call
        return None
```

Example firestore path extracted from web traffic:

projects/spendee-app/databases/(default)/documents/users/af150597-5b96-4f8b-9eb3-0b2e0aa72a81/wallets/b368c5c2-68fe-4f98-9d4f-08e0cdca57a7/transactions/26624eef-6956-4cbc-8aee-68e4fb97396b

