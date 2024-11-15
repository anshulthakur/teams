from django.contrib import admin

from .models import TestCase, TestExecution, TestRun, TestSuite, Subscription

# Register your models here.
class TestCaseAdmin(admin.ModelAdmin):
    search_fields = ["name", "oid"]
admin.site.register(TestCase, TestCaseAdmin)

class TestExecutionAdmin(admin.ModelAdmin):
    search_fields = ["testcase__oid", "testcase__name"]
admin.site.register(TestExecution, TestExecutionAdmin)

class TestRunAdmin(admin.ModelAdmin):
    pass
admin.site.register(TestRun, TestRunAdmin)

class TestSuiteAdmin(admin.ModelAdmin):
    search_fields = ["name"]
admin.site.register(TestSuite, TestSuiteAdmin)

class SubscriptionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Subscription, SubscriptionAdmin)