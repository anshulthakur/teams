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

User = get_user_model()

# Create your tests here.
class SerializerTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        # Create an APIClient
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)

    def tearDown(self):
        pass

class Test_TestRuns(SerializerTests):
    def setUp(self):
        super().setUp()
        # Create some test cases for the test run
        self.test_case_1 = TestCase.objects.create(name='Test Case 1', oid='TC001', author=self.test_user)
        self.test_case_2 = TestCase.objects.create(name='Test Case 2', oid='TC002', author=self.test_user)

        # Data payload for creating a TestRun
        self.test_run_data = {
            "notes": "Automated Test Run",
            "executions": [
                {
                    "testcase": "TC001",
                    "result": "PASS",
                    "notes": "All good",
                    "duration": "0:05:00"  # 5 minutes
                },
                {
                    "testcase": "TC002",
                    "result": "FAIL",
                    "notes": "Failed at step 3",
                    "duration": "0:03:00"
                }
            ]
        }

    def test_create_test_run(self):
        """
        Test the creation of a TestRun with TestExecutions.
        """
        response = self.client.post(reverse('teams_core:testrun-list'), self.test_run_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TestRun.objects.count(), 1)
        self.assertEqual(TestExecution.objects.count(), 2)

    def test_get_test_run(self):
        """
        Test fetching a single TestRun.
        """
        # First, create a test run
        response = self.client.post(reverse('teams_core:testrun-list'), self.test_run_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        test_run_id = response.data['id']

        # Now fetch the TestRun
        response = self.client.get(reverse('teams_core:testrun-detail', args=[test_run_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'], 'Automated Test Run')

    def test_delete_test_run(self):
        """
        Test deleting a TestRun.
        """
        # First, create a test run
        response = self.client.post(reverse('teams_core:testrun-list'), self.test_run_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        test_run_id = response.data['id']

        # Delete the test run
        response = self.client.delete(reverse('teams_core:testrun-detail', args=[test_run_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TestRun.objects.count(), 0)
        self.assertEqual(TestExecution.objects.count(), 0)

class Test_TestCases(SerializerTests):

    def setUp(self):
        super().setUp()
        # Create test case data
        self.test_case_data = {
            'name': 'New Test Case',
            'oid': 'TC999',
            'author': self.test_user.id
        }

    def test_create_test_case(self):
        """
        Test creating a new TestCase.
        """
        response = self.client.post(reverse('teams_core:testcase-list'), self.test_case_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TestCase.objects.count(), 1)
        self.assertEqual(TestCase.objects.get().name, 'New Test Case')

    def test_duplicate_test_case_not_allowed(self):
        """
        Test creating a new TestCase.
        """
        response = self.client.post(reverse('teams_core:testcase-list'), self.test_case_data, format='json')
        response = self.client.post(reverse('teams_core:testcase-list'), self.test_case_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TestCase.objects.count(), 1)
        self.assertEqual(TestCase.objects.get().name, 'New Test Case')
        print(response.json())

    def test_get_test_case(self):
        """
        Test fetching a TestCase.
        """
        # Create the test case
        response = self.client.post(reverse('teams_core:testcase-list'), self.test_case_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        test_case_id = response.data['id']

        # Fetch the test case
        response = self.client.get(reverse('teams_core:testcase-detail', args=[test_case_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New Test Case')

    def test_delete_test_case(self):
        """
        Test deleting a TestCase.
        """
        # Create the test case
        response = self.client.post(reverse('teams_core:testcase-list'), self.test_case_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        test_case_id = response.data['id']

        # Delete the test case
        response = self.client.delete(reverse('teams_core:testcase-detail', args=[test_case_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TestCase.objects.count(), 0)

class TestSuiteTest(TestCase):
    def setUp(self):
        # Create test cases to add to the suite
        self.testcase1 = TestCase.objects.create(name="Test Case 1", oid="TC001")
        self.testcase2 = TestCase.objects.create(name="Test Case 2", oid="TC002")

    def test_create_suite(self):
        suite = TestSuite.objects.create(name="Sample Suite")
        suite.testcase_set.add(self.testcase1, self.testcase2)
        self.assertEqual(suite.testcase_set.count(), 2)

    def test_export_suite(self):
        # Simulate the export suite function
        suite = TestSuite.objects.create(name="Sample Suite")
        suite.testcase_set.add(self.testcase1)
        response = self.client.get(reverse('export_testsuite', args=[suite.id, 'docx']))
        self.assertEqual(response.status_code, 200)

class TestAuthentication(APITestCase):

    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        # Define the login URL and credentials
        self.login_url = reverse('login')
        self.credentials = {
            'username': 'testuser',
            'password': 'testpassword'
        }

        # Test case data for creation
        self.test_case_data = {
            'name': 'New Test Case',
            'oid': 'TC999',
            'author': self.test_user.id
        }

        # Test run data for creation
        self.test_run_data = {
            "notes": "Automated Test Run",
            "executions": [
                {
                    "testcase": "TC999",
                    "result": "PASS",
                    "notes": "All good",
                    "duration": "0:05:00"
                }
            ]
        }

    def test_create_without_authentication(self):
        """
        Ensure that creating a test case and test run without authentication fails.
        """
        # Try creating a test case without being authenticated
        response = self.client.post(reverse('teams_core:testcase-list'), self.test_case_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try creating a test run without being authenticated
        response = self.client.post(reverse('teams_core:testrun-list'), self.test_run_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_and_create(self):
        """
        Ensure that a user can login, then create test case and test run successfully.
        """
        # Login using Django's client.login() method
        self.client.login(username=self.credentials['username'], password=self.credentials['password'])

        # Create a test case after login
        response = self.client.post(reverse('teams_core:testcase-list'), self.test_case_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a test run after login
        response = self.client.post(reverse('teams_core:testrun-list'), self.test_run_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TestRun.objects.count(), 1)
        self.assertEqual(TestExecution.objects.count(), 1)

    def test_logout_and_create(self):
        """
        Ensure that after logging out, creating test case and test run fails.
        """
        # Login first
        # Login using Django's client.login() method
        self.client.login(username=self.credentials['username'], password=self.credentials['password'])

        # Logout
        self.client.logout()

        # Try creating a test case after logging out
        response = self.client.post(reverse('teams_core:testcase-list'), self.test_case_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try creating a test run after logging out
        response = self.client.post(reverse('teams_core:testrun-list'), self.test_run_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestRunAPITests(APITestCase):
    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        # Define base URLs for test runs
        self.test_run_url = reverse('teams_core:testrun-list')  # assuming you have registered test run urls
        self.test_run_create_data = {
            'date': timezone.now().isoformat(),  # Use ISO format for date
            'created_by': self.user.id,
            'notes': 'Initial test run',
            'published': True,
        }

    def test_create_test_run(self):
        """
        Test that a new TestRun can be created, and ensure atomicity in case of duplicates.
        """
        # Create the first test run
        response = self.client.post(self.test_run_url, self.test_run_create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Attempt to create a duplicate test run with the same timestamp
        duplicate_response = self.client.post(self.test_run_url, self.test_run_create_data, format='json')
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('A test run with this timestamp already exists for this user.', duplicate_response.data['non_field_errors'])

    def test_push_test_run_updates_existing(self):
        """
        Test that pushing the same test run with the same timestamp updates the existing one.
        """
        # Create the first test run
        response = self.client.post(self.test_run_url, self.test_run_create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        test_run_id = response.data['id']

        # Now, modify the test run data and push it again (same date, same user, updates instead of creates)
        updated_data = self.test_run_create_data.copy()
        updated_data['notes'] = 'Updated test run notes'

        update_url = reverse('teams_core:testrun-detail', args=[test_run_id])  # assuming you have registered detail urls
        update_response = self.client.put(update_url, updated_data, format='json')

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['notes'], 'Updated test run notes')

    def test_unauthorized_access(self):
        """
        Test that an unauthorized user cannot create or update a TestRun.
        """
        self.client.logout()  # Ensure no user is authenticated
        response = self.client.post(self.test_run_url, self.test_run_create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)