from django.db import models
from django.contrib.auth.models import User

class TestSuite(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    content = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=False, blank=False, on_delete=models.SET_NULL)

class TestCase(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    author = models.ForeignKey(User, null=False, blank=False, on_delete=models.SET_NULL)
    content = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    suites = models.ManyToManyField('TestSuite')

class TestRun(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=False, blank=False, on_delete=models.SET_NULL)

class TestExecution(models.Model):
    TEST_RESULT_CHOICES = [
        ("PASS", "Test Passed"),
        ("FAIL", "Test Failed"),
    ]
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    testcase = models.ForeignKey('TestSuite', on_delete=models.SET_NULL)
    result = models.CharField(choices=TEST_RESULT_CHOICES, max_length=5)
    run = models.ForeignKey('TestRun', null=False, blank=False, on_delete=models.CASCADE)
