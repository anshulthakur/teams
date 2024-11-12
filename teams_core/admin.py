from django.contrib import admin

from .models import TestCase, TestExecution, TestRun, TestSuite, Subscription

# Register your models here.
admin.site.register(TestCase)
admin.site.register(TestExecution)
admin.site.register(TestRun)
admin.site.register(TestSuite)
admin.site.register(Subscription)