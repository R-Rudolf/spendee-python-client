import requests
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
        #print("Access Token:", data['access_token'])  # Debugging line to check the access token
        return data['access_token']

    def get_device_uuid_from_login(self):
        # This should be implemented in the child class if needed, as it may require a specific API call
        return None

    @property
    def access_token(self):
        if not self._access_token:
            self.authenticate()
        return self._access_token

    @property
    def device_uuid(self):
        return self._device_uuid

    @device_uuid.setter
    def device_uuid(self, value):
        self._device_uuid = value
