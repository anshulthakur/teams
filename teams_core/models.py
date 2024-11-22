from django.db import models, IntegrityError, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.models import Sum

class TestSuite(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    content = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('teams_core:test_suite_detail', args=[str(self.id)])

class TestCase(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    oid = models.CharField(max_length=1024, blank=True, null=True, unique=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='authored_cases')
    maintainers = models.ManyToManyField(User, related_name='maintained_cases', blank=True)
    content = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    suites = models.ManyToManyField(TestSuite, blank=True)
    version = models.CharField(max_length=20, default="1.0")  # Optional, for version control

    def total_runs(self):
        return TestExecution.objects.filter(testcase=self, run__published=True).exclude(result='SKIPPED').count()

    def successful_runs(self):
        return TestExecution.objects.filter(testcase=self, run__published=True, result='PASS').count()

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('teams_core:test_case_detail', args=[str(self.id)])
    
class TestRun(models.Model):
    date = models.DateTimeField(default=timezone.now, null=False)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=True, blank=True)

    class Meta:
        unique_together = ('date', 'created_by') 
    
    def __str__(self):
        return f'Test Run on {self.date}'
    
    def total_tests_executed(self):
        return TestExecution.objects.filter(run=self).exclude(result='SKIPPED').count()

    def successful_tests(self):
        return TestExecution.objects.filter(run=self, result='PASS').count()
    
    def get_absolute_url(self):
        return reverse('teams_core:test_run_detail', args=[str(self.id)])
    
    def get_runtime(self):
        duration = TestExecution.objects.filter(run=self).aggregate(Sum("duration"))
        return duration['duration__sum']

class TestExecution(models.Model):
    TEST_RESULT_CHOICES = [
        ("PASS", "Test Passed"),
        ("FAIL", "Test Failed"),
        ("SKIPPED", "Test Skipped"),
        ("ERROR", "Error in execution"),
        ("NOT RUN", "Test not run"),
    ]
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)  # Link to TestCase
    result = models.CharField(choices=TEST_RESULT_CHOICES, max_length=10)
    run = models.ForeignKey(TestRun, null=False, blank=False, on_delete=models.CASCADE)
    duration = models.DurationField(blank=True, null=True)  # Track how long the test took

    def __str__(self):
        return f'TE on {self.date} for {self.testcase}'
    
class Subscription(models.Model):
    EVENT_CHOICES = [
        ('TEST_EXECUTION_FAIL', 'Test Execution Failure'),
        ('TEST_RUN_CREATED', 'New Test Run Created'),
        # Additional event types as needed
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    active = models.BooleanField(default=True)
    created_on = models.DateTimeField(default=timezone.now)

    # Generic foreign key fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    subscribed_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.user} subscription to {self.event_type} for {self.subscribed_object}"

    class Meta:
        unique_together = ('user', 'event_type', 'content_type', 'object_id')