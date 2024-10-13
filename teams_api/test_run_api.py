import requests
from .exceptions import APIError

class TestRunAPI:
    def __init__(self, auth):
        self.auth = auth
        self.base_url = self.auth.base_url

    def _get_auth_headers(self):
        """Helper method to get the Authorization headers with the access token."""
        if not self.auth.access_token:
            raise APIError("No access token found. Please log in.")
        return {
            "Authorization": f"Bearer {self.auth.access_token}"
        }

    def create_test_run(self, data):
        url = f"{self.base_url}/tests/test-cases/testruns/"
        headers = self._get_auth_headers()  # Add JWT token to headers

        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 201:
            raise APIError(f"Failed to create test run: {response.content}")
        return response.json()

    def get_test_run(self, test_run_id):
        url = f"{self.base_url}/tests/test-cases/testruns/{test_run_id}/"
        headers = self._get_auth_headers()  # Add JWT token to headers

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise APIError(f"Failed to fetch test run: {response.content}")
        return response.json()

    def update_test_run(self, test_run_id, data):
        url = f"{self.base_url}/tests/test-cases/testruns/{test_run_id}/"
        headers = self._get_auth_headers()  # Add JWT token to headers

        response = requests.put(url, json=data, headers=headers)
        if response.status_code not in (200, 201):
            raise APIError(f"Failed to update test run: {response.content}")
        return response.json()

    def delete_test_run(self, test_run_id):
        url = f"{self.base_url}/tests/test-cases/testruns/{test_run_id}/"
        headers = self._get_auth_headers()  # Add JWT token to headers

        response = requests.delete(url, headers=headers)
        if response.status_code != 204:
            raise APIError(f"Failed to delete test run: {response.content}")
        return
