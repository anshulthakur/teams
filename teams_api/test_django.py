from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from rest_framework import status
from django.http import HttpRequest as Request # Import HttpRequest

from teams_core.serializers import *
from teams_core.models import *

from teams_api import TestRunAPI, APIError, PortalAuth
User = get_user_model()

TEST_URL = "http://127.0.0.1:8000"

class TestAPILibrary(APITestCase):
    def setUp(self):
        """Set up the test environment, including creating a user."""
        self.username = "anshul"
        self.password = "password"

    def test_login_and_create(self):
        """Test login using the API and create a test run successfully."""
        # Initialize the authentication and API classes
        auth = PortalAuth(base_url=TEST_URL)
        response = auth.login(username=self.username, password=self.password)
        self.assertIsNotNone(response)

        # Create the TestRunAPI instance
        test_run_api = TestRunAPI(auth)

        # Create a new test run
        data = {
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
        response = test_run_api.create_test_run(data)
        print(response)
        self.assertIsNotNone(response)
        self.assertIn('id', response)  # Ensure test run was created with an ID

    def test_duplicate_test_run_not_allowed(self):
        """Test that creating a duplicate test run is not allowed."""
        auth = PortalAuth(base_url=TEST_URL)
        response = auth.login(username=self.username, password=self.password)
        self.assertIsNotNone(response)

        test_run_api = TestRunAPI(auth)

        # Create the first test run
        data = {
            'date': datetime.datetime.now().isoformat(),
            'notes': 'Original Test Run',
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
        response = test_run_api.create_test_run(data)
        self.assertIsNotNone(response)

        # Try to create a duplicate test run with the same date
        with self.assertRaises(APIError) as context:
            test_run_api.create_test_run(data)  # This should raise an error due to duplicate

        self.assertIn("A test run with this timestamp already exists", str(context.exception))

    def test_get_test_run(self):
        """Test fetching an existing test run."""
        auth = PortalAuth(base_url=TEST_URL)
        response = auth.login(username=self.username, password=self.password)
        self.assertIsNotNone(response)

        test_run_api = TestRunAPI(auth)

        # Create a test run
        data = {
            'date': datetime.datetime.now().isoformat(),
            'notes': 'Test Run for Fetching',
            'published': True,
            'executions': [
                {
                    'testcase': 'TC001',
                    'result': 'PASS',
                    'notes': 'All steps passed',
                    'duration': '00:10:00'
                }
            ]
        }
        created_response = test_run_api.create_test_run(data)
        test_run_id = created_response['id']

        # Fetch the created test run
        fetched_response = test_run_api.get_test_run(test_run_id)
        self.assertEqual(fetched_response['id'], test_run_id)
        self.assertEqual(fetched_response['notes'], 'Test Run for Fetching')

    def test_update_test_run(self):
        """Test updating an existing test run."""
        auth = PortalAuth(base_url=TEST_URL)
        response = auth.login(username=self.username, password=self.password)
        self.assertIsNotNone(response)

        test_run_api = TestRunAPI(auth)

        # Create a test run
        data = {
            'date': datetime.datetime.now().isoformat(),
            'notes': 'Test Run for Updating',
            'published': True,
            'executions': [
                {
                    'testcase': 'TC001',
                    'result': 'FAIL',
                    'notes': 'Some steps failed',
                    'duration': '00:15:00'
                }
            ]
        }
        created_response = test_run_api.create_test_run(data)
        test_run_id = created_response['id']

        # Update the test run
        update_data = {
            'notes': 'Updated Test Run Notes',
            'published': False,  # Change the published status
            'executions': [
                {
                    'testcase': 'TC001',
                    'result': 'PASS',  # Change the result
                    'notes': 'Retested and passed',
                    'duration': '00:12:00'
                }
            ]
        }
        updated_response = test_run_api.update_test_run(test_run_id, update_data)
        print(updated_response)
        self.assertEqual(updated_response['notes'], 'Updated Test Run Notes')
        self.assertEqual(updated_response['published'], False)
        self.assertEqual(updated_response['executions'][0]['result'], 'PASS')

    def test_delete_test_run(self):
        """Test deleting a test run."""
        auth = PortalAuth(base_url=TEST_URL)
        response = auth.login(username=self.username, password=self.password)
        self.assertIsNotNone(response)

        test_run_api = TestRunAPI(auth)

        # Create a test run
        data = {
            'date': datetime.datetime.now().isoformat(),
            'notes': 'Test Run for Deleting',
            'published': True,
            'executions': [
                {
                    'testcase': 'TC001',
                    'result': 'PASS',
                    'notes': 'All steps passed',
                    'duration': '00:20:00'
                }
            ]
        }
        created_response = test_run_api.create_test_run(data)
        test_run_id = created_response['id']

        # Delete the created test run
        delete_response = test_run_api.delete_test_run(test_run_id)
        self.assertIsNone(delete_response)

        # Attempt to fetch the deleted test run
        with self.assertRaises(APIError) as context:
            test_run_api.get_test_run(test_run_id)

        self.assertIn("Failed to fetch test run", str(context.exception))