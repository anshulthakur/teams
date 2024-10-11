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

class TestAPILibrary(APITestCase):
    def setUp(self):
        # Set up a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )

        # Define base_url and initialize API library
        self.base_url = ''  # Leave empty since we're using the test client
        self.credentials = {
            "username": "testuser",
            "password": "testpassword"
        }

        # Initialize the authentication and TestRunAPI client
        self.auth = PortalAuth(base_url=self.base_url)
        self.test_run_api = TestRunAPI(auth=self.auth)

        # URLs
        self.test_run_url = reverse('teams_core:testrun-list')  # URL for the TestRun API

        # Create some test cases for the test run
        self.test_case_1 = TestCase.objects.create(name='Test Case 1', oid='TC001', author=self.test_user)
        self.test_case_2 = TestCase.objects.create(name='Test Case 2', oid='TC002', author=self.test_user)

    def test_login_and_create(self):
        """Test login using the API and create a test run successfully."""
        login_response = self.auth.login(self.credentials['username'], self.credentials['password'])
        self.assertEqual(login_response.status_code, 200, "Login failed.")

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

    def test_logout(self):
        """Test logging out the user."""
        login_response = self.auth.login(self.credentials['username'], self.credentials['password'])
        self.assertEqual(login_response.status_code, 200, "Login failed.")

        logout_response = self.auth.logout()
        self.assertEqual(logout_response.status_code, 204, "Logout failed.")

        # Verify that the session is no longer valid
        with self.assertRaises(Exception):
            self.auth.session.get(self.test_run_url)

