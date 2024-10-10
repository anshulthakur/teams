from rest_framework import serializers
from .models import TestRun, TestExecution, TestCase

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['id', 'name', 'oid', 'author', 'content', 'created_on', 
                  'last_modified', 'suites', 'version']
        extra_kwargs = {
            'author': {'required': False},
            'suites': {'required': False},
            'version': {'required': False},
            'oid': {'required': False},
        }

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

    class Meta:
        model = TestRun
        fields = ['id', 'date', 'created_by', 'notes', 'executions']
        extra_kwargs = {
            'created_by': {'required': False},
            'notes': {'required': False}
        }

    def create(self, validated_data):
        executions_data = validated_data.pop('executions', [])
        test_run = TestRun.objects.create(**validated_data)

        for execution_data in executions_data:
            # Manually set the run field before saving each execution
            TestExecution.objects.create(run=test_run, **execution_data)

        return test_run
