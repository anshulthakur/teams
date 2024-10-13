import requests
from requests.exceptions import RequestException

class PortalAuth:
    def __init__(self, base_url):
        self.base_url = base_url
        self.access_token = None  # Store the JWT access token
        self.refresh_token = None  # Store the JWT refresh token

    def login(self, username, password):
        # Prepare the login payload for obtaining JWT token
        payload = {
            "username": username,
            "password": password
        }

        try:
            # Send login request to obtain JWT tokens
            response = requests.post(f"{self.base_url}/api/token/", json=payload)
            response.raise_for_status()  # Raise an error for bad responses

            # Extract the access and refresh tokens from the response
            tokens = response.json()
            self.access_token = tokens['access']
            self.refresh_token = tokens['refresh']

            return response  # Return the login response (with tokens)
        except RequestException as e:
            print(f"Login failed: {e}")
            return None

    def refresh_access_token(self):
        """Use the refresh token to get a new access token."""
        try:
            # Send request to refresh the access token using the refresh token
            response = requests.post(f"{self.base_url}/api/token/refresh/", json={"refresh": self.refresh_token})
            response.raise_for_status()
            self.access_token = response.json()['access']  # Update access token
        except RequestException as e:
            print(f"Token refresh failed: {e}")
            return None

    def logout(self):
        self.access_token = None
        self.refresh_token = None
