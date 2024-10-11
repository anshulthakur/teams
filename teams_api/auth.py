import requests
from requests.exceptions import RequestException

class PortalAuth:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, username, password):
        # Get CSRF token from the login page
        csrf_response = self.session.get(f"{self.base_url}/api/login/")
        csrf_token = csrf_response.cookies['csrftoken']  # Get the CSRF token from cookies

        # Prepare the login payload
        payload = {
            "username": username,
            "password": password
        }

        # Set headers with the CSRF token
        headers = {
            'X-CSRFToken': csrf_token
        }

        # Send login request
        try:
            response = self.session.post(f"{self.base_url}/api/login/", json=payload, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            return response  # Return the login response
        except RequestException as e:
            print(f"Login failed: {e}")
            return None

    def logout(self):
        self.session.post(f"{self.base_url}/api/logout/")
        self.session.cookies.clear()
