from rest_framework import serializers
from .models import TestCase

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['id', 'name', 'author', 'content', 'created_on', 
                  'last_modified', 'suites', 'version']
        extra_kwargs = {
            'author': {'required': False},
            'suites': {'required': False},
            'version': {'required': False}
        }