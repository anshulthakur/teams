# test_api_library.py
import unittest
from teams_api import PortalAuth, TestRunAPI, APIError
import datetime

class TestAPILibrary(unittest.TestCase):
    def setUp(self):
        # Define base_url and initialize API library
        self.base_url = 'http://127.0.0.1:8000'  # Use testserver for Django's test client
        self.credentials = {
            "username": "anshul",
            "password": "password"
        }

        # Initialize the authentication and TestRunAPI client
        self.auth = PortalAuth(base_url=self.base_url)
        self.test_run_api = TestRunAPI(auth=self.auth)
    
    def tearDown(self):
        if self.auth:
            self.auth.logout()

    def test_login_and_create(self):
        """
        Test login using the live server and create a test run successfully.
        """
        # Login using the API
        login_response = self.auth.login(self.credentials['username'], self.credentials['password'])
        self.assertEqual(login_response.status_code, 200, "Login failed.")

        # Create a test run after logging in
        test_run_data = {
            'date': datetime.datetime.now().isoformat(),
            'notes': 'Automated Test Run',
            'published': True,
            'executions': [
                {
                    'testcase': 'TC001',
                    'result': 'PASS',
                    'notes': 'All steps passed',
                    'duration': '00:05:00'
                }
            ]
        }
        create_response = self.test_run_api.create_test_run(test_run_data)
        self.assertEqual(create_response['notes'], 'Automated Test Run', "Test run creation failed.")

    def test_prevent_duplicate_test_run(self):
        """
        Test that duplicate test runs (same timestamp) are not created.
        """
        # Login using the API
        self.auth.login(self.credentials['username'], self.credentials['password'])

        # Create the first test run
        test_run_data = {
            'date': datetime.datetime.now().isoformat(),
            'notes': 'Automated Test Run',
            'published': True,
            'executions': []
        }
        response_1 = self.test_run_api.create_test_run(test_run_data)
        self.assertIsNotNone(response_1['id'], "First test run creation failed.")

        # Try creating a duplicate test run with the same data
        with self.assertRaises(APIError, msg="Duplicate test run should raise an error"):
            self.test_run_api.create_test_run(test_run_data)

    def test_atomicity_on_failure(self):
        """
        Test atomicity of operations: Ensure that no partial data is saved if an error occurs.
        """
        # Login using the API
        self.auth.login(self.credentials['username'], self.credentials['password'])

        # Simulate data that would cause failure (e.g., invalid duration format)
        test_run_data = {
            'date': datetime.datetime.now().isoformat(),
            'notes': 'Test Run with Error',
            'published': True,
            'executions': [
                {
                    'testcase': 'TC_ERROR',
                    'result': 'ERROR',
                    'notes': 'Simulation of failure',
                    'duration': 'invalid-duration'  # This should cause an error
                }
            ]
        }

        with self.assertRaises(APIError, msg="Atomicity failure test"):
            self.test_run_api.create_test_run(test_run_data)

        # Ensure that no data was saved (check server state)
        test_runs = self.client.get(self.test_run_url)
        self.assertEqual(len(test_runs.data), 0, "Test run should not be saved on failure.")

    def test_get_test_run(self):
        """
        Test fetching a test run after creation.
        """
        # Login using the API
        self.auth.login(self.credentials['username'], self.credentials['password'])

        # Create a test run
        test_run_data = {
            'date': datetime.datetime.now().isoformat(),
            'notes': 'Automated Test Run',
            'published': True,
            'executions': []
        }
        create_response = self.test_run_api.create_test_run(test_run_data)
        test_run_id = create_response['id']

        # Fetch the test run
        fetched_test_run = self.test_run_api.get_test_run(test_run_id)
        self.assertEqual(fetched_test_run['id'], test_run_id, "Test run fetch failed.")
        self.assertEqual(fetched_test_run['notes'], 'Automated Test Run')

if __name__ == '__main__':
    unittest.main()
