from rest_framework import serializers
from .models import TestRun, TestExecution, TestCase, TestSuite
from django.contrib.auth.models import Group, User
from notifications.signals import notify
from teams_core.utils import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class TestCaseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TestCase
        fields = ['id', 'name', 'oid', 'author', 'content', 'created_on', 
                  'last_modified', 'suites', 'version', 'maintainers']
        extra_kwargs = {
            'author': {'required': False},
            'maintainers': {'required': False},
            'suites': {'required': False},
            'version': {'required': False},
            'oid': {'required': False},
        }

class TestSuiteSerializer(serializers.ModelSerializer):
    testcases = serializers.PrimaryKeyRelatedField(many=True, write_only=True, queryset=TestCase.objects.all())
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = TestSuite
        fields = ['id', 'name', 'content', 'created_on', 
                  'last_modified', 'author', 'testcases']

    def create(self, validated_data):
        testcases = validated_data.pop('testcases', [])
        testsuite = TestSuite.objects.create(**validated_data)
        testsuite.testcase_set.set(testcases)  # Assign test cases
        return testsuite

    def update(self, instance, validated_data):
        testcases = validated_data.pop('testcases', None)
        instance.name = validated_data.get('name', instance.name)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        
        if testcases is not None:
            instance.testcase_set.set(testcases)
        return instance

    def to_representation(self, instance):
        """Customize the representation to include serialized test cases."""
        representation = super().to_representation(instance)  # Call the parent method
        representation['testcases'] = TestCaseSerializer(instance.testcase_set.all(), many=True).data
        return representation  # Return the modified representation


class TestExecutionSerializer(serializers.ModelSerializer):
    testcase = serializers.SlugRelatedField(slug_field='oid', queryset=TestCase.objects.all())

    class Meta:
        model = TestExecution
        fields = ['id', 'date', 'testcase', 'result', 'notes', 'duration', 'run']
        extra_kwargs = {
            'testcase': {'required': True},
            'result': {'required': True},
            'run': {'required': False},  # Set 'run' to False since it will be set during creation in the TestRunSerializer
        }


class TestRunSerializer(serializers.ModelSerializer):
    executions = TestExecutionSerializer(many=True, required=False)  # Enable write access
    created_by = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = TestRun
        fields = ['id', 'date', 'created_by', 'notes', 'executions', 'published']
        extra_kwargs = {
            'created_by': {'required': False},
            'notes': {'required': False},
            'date' : {'required': False},
            'published': {'required': False}
        }
    
    def validate(self, data):
        user = self.context['request'].user
        if self.instance is None:  # Only check for uniqueness if creating a new instance
            if TestRun.objects.filter(date=data['date'], created_by=user).exists():
                raise serializers.ValidationError("A test run with this timestamp already exists for this user.")
        return data

    def create(self, validated_data):
        executions_data = validated_data.pop('executions', [])
        test_run = TestRun.objects.create(**validated_data)
        for execution_data in executions_data:
            execution = TestExecution.objects.create(run=test_run, **execution_data)
            # Send notification if the test case failed
            if execution.result == 'FAIL':
                self._send_failure_notification(execution)
        return test_run

    def update(self, instance, validated_data):
        executions_data = validated_data.pop('executions', None)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.published = validated_data.get('published', instance.published)
        instance.save()

        if executions_data is not None:
            # Update or create TestExecution instances
            for execution_data in executions_data:
                execution, created = TestExecution.objects.update_or_create(
                    run=instance,
                    testcase=execution_data['testcase'],
                    defaults={
                        'result': execution_data['result'],
                        'notes': execution_data.get('notes', ''),
                        'duration': execution_data.get('duration', None)
                    }
                )
                # Send notification if the test case failed and is newly created or updated to fail
                if execution.result == 'FAIL' and (created or execution_data['result'] == 'FAIL'):
                    self._send_failure_notification(execution)
        return instance  # Return the instance to be processed by DRF
    
    def to_representation(self, instance):
        """Customize the representation to include serialized executions."""
        representation = super().to_representation(instance)  # Call the parent method
        representation['executions'] = TestExecutionSerializer(instance.testexecution_set.all(), many=True).data
        return representation  # Return the modified representation
    
    def _send_failure_notification(self, execution):
        # Get the author of the test case
        test_case = execution.testcase
        test_case_author = test_case.author

        # Compose the message content
        message = f"Test Case '{execution.testcase.oid}' failed during the test run on {execution.run.date}."
        # Check if the author exists
        if test_case_author:
            # Send a notification to the test case author
            notify.send(
                sender=execution.run.created_by,
                recipient=test_case_author,
                verb=f'{execution.testcase.oid} failed',
                description=message,
                target=execution.run,
                action_object=execution,
            )
        
        if execution.run.published:
            subscribers = get_active_subscribers('TEST_EXECUTION_FAIL', test_case)
            for subscriber in subscribers:
                    notify.send(
                        sender=execution.run.created_by,
                        recipient=subscriber,
                        verb=f'{execution.testcase.oid} failed',
                        description=message,
                        target=execution.run,
                        action_object=execution
                    )
