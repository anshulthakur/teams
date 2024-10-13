from rest_framework import serializers
from .models import TestRun, TestExecution, TestCase
from django.contrib.auth.models import Group, User

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
            TestExecution.objects.create(run=test_run, **execution_data)
        return test_run

    def update(self, instance, validated_data):
        executions_data = validated_data.pop('executions', None)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.published = validated_data.get('published', instance.published)
        instance.save()

        if executions_data is not None:
            # Update or create TestExecution instances
            for execution_data in executions_data:
                TestExecution.objects.update_or_create(
                    run=instance,
                    testcase=execution_data['testcase'],
                    defaults={
                        'result': execution_data['result'],
                        'notes': execution_data.get('notes', ''),
                        'duration': execution_data.get('duration', None)
                    }
                )
        return instance  # Return the instance to be processed by DRF
    
    def to_representation(self, instance):
        """Customize the representation to include serialized executions."""
        representation = super().to_representation(instance)  # Call the parent method
        representation['executions'] = TestExecutionSerializer(instance.testexecution_set.all(), many=True).data
        return representation  # Return the modified representation
