from django.db import models, IntegrityError, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

class TestSuite(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    content = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class TestCase(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    oid = models.CharField(max_length=1024, blank=True, null=True, unique=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
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