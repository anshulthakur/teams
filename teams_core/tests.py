from django.test import TestCase as UnitTestCase
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

from django.core import mail
from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta

from teams_core.metrics import *

User = get_user_model()

# Create your tests here.
class Test_Serializers(APITestCase):
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

class Test_TestRuns(Test_Serializers):
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

class Test_TestCases(Test_Serializers):

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

class Test_TestSuite(UnitTestCase):
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

class Test_Authentication(APITestCase):

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

class Test_TestRunAPI(APITestCase):
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

class Test_Subscriptions(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)
        
        # Create a TestSuite
        self.test_suite = TestSuite.objects.create(name="Suite 1", author=self.user)
        
        # Create a TestCase
        self.test_case = TestCase.objects.create(name="Test Case 1", oid="TC001", author=self.user)
        
        # Add TestCase to TestSuite
        self.test_suite.testcase_set.add(self.test_case)

    def test_subscribe_author_to_testcase(self):
        """
        Test that the author is subscribed to failure notifications
        """
        subscription_exists = Subscription.objects.filter(
            user=self.user,
            event_type='TEST_EXECUTION_FAIL',
            content_type=ContentType.objects.get_for_model(TestCase),
            object_id=self.test_case.id
        ).exists()
        self.assertTrue(subscription_exists, "Author is not subscribed to the test case for failure notifications.")

    def test_subscribe_author_update_to_testcase(self):
        """
        Test that the new author is subscribed to failure notifications when authorship of 
        test case is changed.
        """
        new_author = User.objects.create_user(username='new_author', password='password')
        self.test_case.author = new_author
        self.test_case.save()
        
        subscription_exists = Subscription.objects.filter(
            user=new_author,
            event_type='TEST_EXECUTION_FAIL',
            content_type=ContentType.objects.get_for_model(TestCase),
            object_id=self.test_case.id
        ).exists()
        self.assertTrue(subscription_exists, "New author is not subscribed to the test case for failure notifications.")

    def test_subscribe_maintainer_to_testcase(self):
        """
        Test that the newly added maintainer is subscribed to failure notifications
        """
        maintainer = User.objects.create_user(username='maintainer', password='password')
        self.test_case.maintainers.add(maintainer)

        subscription_exists = Subscription.objects.filter(
            user=maintainer,
            event_type='TEST_EXECUTION_FAIL',
            content_type=ContentType.objects.get_for_model(TestCase),
            object_id=self.test_case.id
        ).exists()
        self.assertTrue(subscription_exists, "Maintainer is not subscribed to the test case for failure notifications.")

    def test_subscribe_author_to_testsuite(self):
        """
        Test that the author is subscribed to failure notifications of all test cases
        in the test suite for existing tests
        """
        subscriptions = Subscription.objects.filter(
            user=self.user,
            event_type='TEST_EXECUTION_FAIL',
            content_type=ContentType.objects.get_for_model(TestCase),
            object_id__in=self.test_suite.testcase_set.values_list('id', flat=True)
        )
        self.assertEqual(subscriptions.count(), self.test_suite.testcase_set.count(), "Author is not subscribed to all test cases in the test suite.")

    def test_subscribe_testsuite_testcase_added_later(self):
        """
        Test that the author is subscribed to failure notifications of all test cases
        that are added after they subscribed to test suite
        """
        new_test_case = TestCase.objects.create(name="New Test Case", oid="TC002", author=self.user)
        self.test_suite.testcase_set.add(new_test_case)

        subscription_exists = Subscription.objects.filter(
            user=self.user,
            event_type='TEST_EXECUTION_FAIL',
            content_type=ContentType.objects.get_for_model(TestCase),
            object_id=new_test_case.id
        ).exists()
        self.assertTrue(subscription_exists, "Author is not subscribed to new test cases added to the test suite.")

    def test_nonauthor_subscribe_testsuite_testcase_added_later(self):
        """
        Test that users subscribed to a TestSuite are automatically subscribed to
        any new TestCase added to the suite.
        """
        # Create a user and a test suite
        user = User.objects.create_user(username="suite_subscriber", password="password")
        test_suite = TestSuite.objects.create(name="Sample Suite")
        
        # Subscribe the user to the test suite
        add_subscription(user, "TEST_EXECUTION_FAIL", test_suite)

        # Create a new test case and add it to the test suite
        test_case = TestCase.objects.create(name="New TestCase", oid="TC123")
        test_suite.testcase_set.add(test_case)

        # Check if the user is subscribed to the new test case
        case_subscribed = Subscription.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(TestCase),
            object_id=test_case.id,
            event_type="TEST_EXECUTION_FAIL",
            active=True
        ).exists()

        self.assertTrue(case_subscribed, "The user should be subscribed to the new TestCase.")

class Test_NotificationSummary(APITestCase):

    def setUp(self):
        # Set up user and test cases
        self.test_user = User.objects.create_user(
            username='summaryuser',
            password='password123',
            email='summaryuser@example.com'
        )

        self.test_case = TestCase.objects.create(
            name='Failing Test Case',
            oid='TC1001',
            author=self.test_user,
        )

        self.test_run = TestRun.objects.create(
            created_by=self.test_user,
            notes="Test run with failure",
            published=True
        )

        # Create multiple TestExecution instances with timedelta for duration
        self.execution1 = TestExecution.objects.create(
            run=self.test_run,
            testcase=self.test_case,
            result="FAIL",
            notes="This test failed",
            duration=timedelta(minutes=3)  # Set duration as timedelta
        )

        # Create a notification for this user
        Notification.objects.create(
            recipient=self.test_user,
            actor_content_type=ContentType.objects.get_for_model(self.execution1.testcase),
            actor_object_id=self.execution1.testcase.id,
            verb=f'{self.execution1.testcase.oid} failed',
            description="Test Case 'TC1001' failed",
            timestamp=timezone.now()
        )

    def test_notification_summary_email(self):
        """
        Test that the management command for sending summary notifications sends an email with the correct details.
        """

        # Run the management command to send summary notifications
        call_command('send_notification_summary')

        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify email contents
        email = mail.outbox[0]
        self.assertIn("Test Failure Summary Notification", email.subject)
        self.assertIn("Hello summaryuser,", email.body)
        # self.assertIn("Execution of test case TC1001 failed", email.body)
        self.assertIn("Total new failures: 1", email.body)
        self.assertIn("https://example.com/test-case/1/", email.body)

class Test_HealthMetrics(UnitTestCase):
    
    def setUp(self):
        # Create sample test cases and executions
        self.test_case1 = TestCase.objects.create(name="Login Test")
        self.test_case2 = TestCase.objects.create(name="Signup Test")
        self.test_run = TestRun.objects.create()

        TestExecution.objects.create(testcase=self.test_case1, run=self.test_run, result="PASS")
        TestExecution.objects.create(testcase=self.test_case1, run=self.test_run, result="FAIL")
        TestExecution.objects.create(testcase=self.test_case2, run=self.test_run, result="SKIPPED")

    def test_health_overview(self):
        # Mark the test run as unpublished
        self.test_run.published = False
        self.test_run.save()

        # Health overview should return an empty result since the test run is unpublished
        result = get_test_health_overview()
        self.assertEqual(result, {})
        
        # Mark the test run as published
        self.test_run.published = True
        self.test_run.save()

        # Now, the results should be calculated correctly
        result = get_test_health_overview()
        self.assertEqual(result, {"PASS": 1, "FAIL": 1, "SKIPPED": 1})

    def test_frequent_failures(self):
        # Mark the test run as unpublished
        self.test_run.published = False
        self.test_run.save()

        # Frequent failures should return an empty result
        result = get_frequent_failures()
        self.assertEqual(result, [])

        # Mark the test run as published
        self.test_run.published = True
        self.test_run.save()

        # Now, the frequent failures should return results correctly
        result = get_frequent_failures()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["testcase__name"], "Login Test")
        self.assertEqual(result[0]["failures"], 1)

class Test_MetricsAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

        # Create sample test cases and executions
        self.test_case1 = TestCase.objects.create(name="Login Test")
        self.test_case2 = TestCase.objects.create(name="Signup Test")
        self.test_run = TestRun.objects.create()

        TestExecution.objects.create(testcase=self.test_case1, run=self.test_run, result="PASS")
        TestExecution.objects.create(testcase=self.test_case1, run=self.test_run, result="FAIL")
        TestExecution.objects.create(testcase=self.test_case2, run=self.test_run, result="SKIPPED")
    
    def test_test_health_overview(self):
        response = self.client.get("/tests/metrics/test-health-overview/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("PASS", response.data)
        self.assertIn("FAIL", response.data)
    
    def test_frequent_failures(self):
        response = self.client.get("/tests/metrics/frequent-failures/?limit=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
    
    def test_latest_test_run_summary(self):
        response = self.client.get("/tests/metrics/latest-test-run-summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))