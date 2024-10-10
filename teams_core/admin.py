from django.contrib import admin

from .models import TestCase, TestExecution, TestRun, TestSuite

# Register your models here.
admin.site.register(TestCase)
admin.site.register(TestExecution)
admin.site.register(TestRun)
admin.site.register(TestSuite)