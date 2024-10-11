# test_run_api.py
import requests
from .exceptions import APIError

class TestRunAPI:
    def __init__(self, auth):
        self.auth = auth
        self.session = self.auth.session
        self.base_url = self.auth.base_url

    def create_test_run(self, data):
        url = f"{self.base_url}/tests/test-cases/testruns/"
        response = self.session.post(url, json=data)
        if response.status_code != 201:
            raise APIError(f"Failed to create test run: {response.content}")
        return response.json()

    def get_test_run(self, test_run_id):
        url = f"{self.base_url}/tests/test-cases/testruns/{test_run_id}/"
        response = self.session.get(url)
        if response.status_code != 200:
            raise APIError(f"Failed to fetch test run: {response.content}")
        return response.json()

    def update_test_run(self, test_run_id, data):
        url = f"{self.base_url}/tests/test-cases/testruns/{test_run_id}/"
        response = self.session.put(url, json=data)
        if response.status_code not in (200, 201):
            raise APIError(f"Failed to update test run: {response.content}")
        return response.json()

    def delete_test_run(self, test_run_id):
        url = f"{self.base_url}/tests/test-cases/testruns/{test_run_id}/"
        response = self.session.delete(url)
        if response.status_code != 204:
            raise APIError(f"Failed to delete test run: {response.content}")
        return
