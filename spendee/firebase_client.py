import requests
from requests import Session
import logging
from jwt import JWT

logger = logging.getLogger(__name__)

class FirebaseClient(Session):

    def __init__(self, email, password, google_client_id: str = 'AIzaSyCCJPDxVNVFEARQ-LxH7q2aZtdQJGGFO84'):
        self.email = email
        self.password = password
        self.google_client_id = google_client_id
        self._access_token = None
        self._refresh_token = None
        self._jwt_instance = JWT() # https://github.com/GehirnInc/python-jwt/blob/master/jwt/jwt.py
        super().__init__()

    def authenticate(self):
        """
        Handles the full authentication flow: gets refresh token, access token, and device UUID.
        """
        logger.info("Starting authentication flow.")
        self._refresh_token = self.get_refresh_token()
        logger.info("Obtained refresh token.")
        self._access_token = self.get_access_token()
        logger.info("Obtained access token.")

    def _log_jwt(self, token, label):
        try:
            payload = self._jwt_instance.decode(token, do_verify=False)
            logger.debug(f"{label} JWT payload: %s", payload)
        except Exception as e:
            logger.debug(f"Failed to decode {label} JWT: {e}")

    def get_refresh_token(self):
        url = f'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={self.google_client_id}'
        payload = {
            'email': self.email,
            'password': self.password,
            'returnSecureToken': True,
        }
        logger.debug(f"Requesting refresh token for {self.email}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        logger.debug("Refresh token response: %s", data)
        return data.get('refreshToken')

    def get_access_token(self):
        url = f'https://securetoken.googleapis.com/v1/token?key={self.google_client_id}'
        payload = {
            'refresh_token': self._refresh_token,
            'grant_type': 'refresh_token',
        }
        logger.debug("Requesting access token with refresh token.")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        logger.debug("Access token response: %s", data)
        access_token = data.get('access_token')
        if access_token:
            self._log_jwt(access_token, 'Access')
        return access_token

    @property
    def access_token(self):
        if not self._access_token:
            logger.info("Access token not found, authenticating.")
            self.authenticate()
        return self._access_token
