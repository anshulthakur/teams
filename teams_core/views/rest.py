import os
from datetime import datetime

from django.contrib.auth.models import User, Group
from django.core.files.storage import default_storage

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import viewsets
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication

from teams_core.models import TestCase, TestRun, TestExecution, TestSuite
from teams_core.serializers import TestCaseSerializer, TestRunSerializer, TestExecutionSerializer, TestSuiteSerializer, UserSerializer, GroupSerializer

from teams_core.metrics import (
    get_test_health_overview,
    get_frequent_failures,
    get_latest_test_run_summary,
    get_stable_and_unstable_tests,
)

class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    #permission_classes = [IsAuthenticatedOrReadOnly]  # Use more appropriate permission
    #permission_classes = [AllowAny]  # Open access for uploads
    permission_classes = [IsAuthenticated]
    #authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class

    def post(self, request, format=None):
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Create directory path based on year/month/day
        now = datetime.now()
        upload_path = os.path.join(settings.MEDIA_ROOT, str(now.year), str(now.month), str(now.day))
        os.makedirs(upload_path, exist_ok=True)

        # Save the uploaded file to the correct directory
        file_path = os.path.join(upload_path, file_obj.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        # Return the file URL
        #file_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, str(now.year), str(now.month), str(now.day), file_obj.name))
        file_url = os.path.join(settings.MEDIA_URL, str(now.year), str(now.month), str(now.day), file_obj.name)
        return Response({"url": file_url}, status=status.HTTP_201_CREATED)
    

class ImageListView(APIView):
    def get(self, request, format=None):
        root_folder = settings.MEDIA_ROOT
        file_data = []

        # Walk through the directories and list image files
        for dirpath, _, filenames in os.walk(root_folder):
            for filename in filenames:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, root_folder)
                    file_url = os.path.join(settings.MEDIA_URL, relative_path).replace("\\", "/")
                    file_data.append({'url': file_url})

        return Response(file_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited
    """
    queryset = Group.objects.all().order_by('id')
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TestCaseViewSet(viewsets.ModelViewSet):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    #authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'oid']  # Supports partial matching on these fields

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get('search')
        
        if search:
            queryset = queryset.filter(Q(name__icontains=search.strip()) | Q(oid__icontains=search.strip()))
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TestSuiteViewSet(viewsets.ModelViewSet):
    queryset = TestSuite.objects.all()
    serializer_class = TestSuiteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    #authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']  # Supports partial matching on these fields

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get('search')
        
        if search:
            queryset = queryset.filter(name__icontains=search.strip())
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class TestRunViewSet(viewsets.ModelViewSet):
    queryset = TestRun.objects.all().order_by('-date')
    serializer_class = TestRunSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    #authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def perform_create(self, serializer):
        # Ensure atomic operation
        with transaction.atomic():
            # Before creating, validate uniqueness to avoid duplicates
            if TestRun.objects.filter(date=serializer.validated_data['date'], created_by=self.request.user).exists():
                raise IntegrityError("A test run with this timestamp already exists for this user.")

            # Save the TestRun instance
            serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        # Ensure atomic operation
        with transaction.atomic():
            executions_data = self.request.data.get('executions', [])
            
            # Save the updated TestRun and TestExecutions
            test_run = serializer.save()
            for execution_data in executions_data:
                TestExecution.objects.update_or_create(
                    run=test_run,
                    testcase_id=execution_data['testcase'],
                    defaults={
                        'result': execution_data['result'],
                        'notes': execution_data.get('notes', ''),
                        'duration': execution_data.get('duration', None)
                    }
                )
        

class TestExecutionViewSet(viewsets.ModelViewSet):
    queryset = TestExecution.objects.all()
    serializer_class = TestExecutionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    #authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class
    authentication_classes = [JWTAuthentication, SessionAuthentication]

class TestHealthOverviewView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        API endpoint to return the test health overview.
        """
        overview = get_test_health_overview()
        return Response(overview)


class FrequentFailuresView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        API endpoint to return the most frequent test failures.
        """
        limit = int(request.query_params.get("limit", 5))  # Default to top 5
        failures = list(get_frequent_failures(limit))
        return Response(failures)


class LatestTestRunSummaryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        API endpoint to return summaries of the latest test runs.
        """
        limit = int(request.query_params.get("limit", 5))  # Default to top 5
        summaries = get_latest_test_run_summary(limit)
        return Response(summaries)


class StableUnstableTestsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        API endpoint to return the most stable and unstable tests.
        """
        limit = int(request.query_params.get("limit", 5))  # Default to top 5
        stable_tests, unstable_tests = get_stable_and_unstable_tests(limit)
        return Response({
            "stable_tests": [{"name": t.name, "pass_ratio": t.pass_ratio} for t in stable_tests],
            "unstable_tests": [{"name": t.name, "fail_ratio": t.fail_ratio} for t in unstable_tests],
        })