import os
import json
from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import viewsets

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication

from teams_core.models import TestCase, TestRun, TestExecution, TestSuite
from teams_core.serializers import TestCaseSerializer, TestRunSerializer, TestExecutionSerializer, TestSuiteSerializer, UserSerializer, GroupSerializer
#from teams_core.auth import CsrfExemptSessionAuthentication

from .export import generate_docx, generate_pdf

def test_case_list(request):
    query = request.GET.get('q')  # Get search query from URL
    test_cases = TestCase.objects.all()

    # Filter by search query if provided
    if query:
        test_cases = test_cases.filter(name__icontains=query)

    return render(request, 'test_case/test_case_list.html', {
        'test_cases': test_cases
    })

def test_case_detail(request, id):
    
    test_case = TestCase.objects.get(pk=id)

    content = json.loads(test_case.content)

    return render(request, 'test_case/test_case_detail.html', {
        'testcase': test_case,
        'content': content
    })

@login_required
def test_case_create(request):
    return render(request, 'test_case/test_case_form.html', {})

@login_required
def test_case_edit(request, id):
    test_case = TestCase.objects.get(pk=id)
    return render(request, 'test_case/test_case_form.html', {'testcase': test_case})


def test_suite_list(request):
    query = request.GET.get('q')  # Get search query from URL
    test_suites = TestSuite.objects.all()

    # Filter by search query if provided
    if query:
        test_suites = test_suites.filter(name__icontains=query)

    return render(request, 'test_suite/test_suite_list.html', {
        'test_suites': test_suites
    })

def test_suite_detail(request, id):
    testsuite = get_object_or_404(TestSuite, id=id)
    
    # Get all test cases in the test suite
    test_cases = testsuite.testcase_set.all()

    # Calculate testing statistics for each test case
    test_case_stats = []
    for testcase in test_cases:
        total_runs = TestExecution.objects.filter(testcase=testcase).count()
        successful_runs = TestExecution.objects.filter(testcase=testcase, result='PASS').count()

        test_case_stats.append({
            'testcase': testcase,
            'total_runs': total_runs,
            'successful_runs': successful_runs
        })

    return render(request, 'test_suite/test_suite_detail.html', {
        'testsuite': testsuite,
        'test_case_stats': test_case_stats
    })

@login_required
def test_suite_create(request):
    return render(request, 'test_suite/test_suite_form.html', {})

@login_required
def test_suite_edit(request, id):
    test_suite = TestSuite.objects.get(pk=id)
    return render(request, 'test_suite/test_suite_form.html', {'testsuite': test_suite})


def test_run_list(request):
    test_runs = TestRun.objects.all().order_by('-date')
    return render(request, 'test_run/test_run_list.html', {
        'test_runs': test_runs
    })

def test_run_detail(request, id):
    test_run = TestRun.objects.get(pk=id)
    test_executions = test_run.testexecution_set.all()  # Get all executions for this run
    return render(request, 'test_run/test_run_detail.html', {
        'test_run': test_run,
        'test_executions': test_executions
    })

@login_required
def test_run_create(request):
    return render(request, 'test_run/test_run_form.html', {})

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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TestSuiteViewSet(viewsets.ModelViewSet):
    queryset = TestSuite.objects.all()
    serializer_class = TestSuiteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    #authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class
    authentication_classes = [JWTAuthentication, SessionAuthentication]

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


class TestExecutionViewSet(viewsets.ModelViewSet):
    queryset = TestExecution.objects.all()
    serializer_class = TestExecutionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    #authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class
    authentication_classes = [JWTAuthentication, SessionAuthentication]

def export_testcase(request, id, format_type='docx'):
    testcase = get_object_or_404(TestCase, id=id)

    try:
        if format_type == 'docx':
            docx_filename, docx_path = generate_docx(testcase=testcase)
            
            # Serve the DOCX as a response
            with open(docx_path, 'rb') as docx_file:
                response = HttpResponse(docx_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename="{docx_filename}"'
                return response

        elif format_type == 'pdf':
            pdf_filename, pdf_path = generate_pdf(testcase=testcase)
            
            if pdf_filename is None:
                return HttpResponse(pdf_path, status=500)  # This returns the error message if conversion fails

            # Serve the PDF as a response
            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
                return response

    except OSError as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
    

def export_testsuite(request, id, format_type='docx'):
    testsuite = get_object_or_404(TestSuite, id=id)

    try:
        if format_type == 'docx':
            docx_filename, docx_path = generate_docx(testsuite=testsuite)
            
            # Serve the DOCX as a response
            with open(docx_path, 'rb') as docx_file:
                response = HttpResponse(docx_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename="{docx_filename}"'
                return response

        elif format_type == 'pdf':
            pdf_filename, pdf_path = generate_pdf(testsuite=testsuite)
            
            if pdf_filename is None:
                return HttpResponse(pdf_path, status=500)  # This returns the error message if conversion fails

            # Serve the PDF as a response
            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
                return response

    except OSError as e:
        return HttpResponse(f"Error: {str(e)}", status=500)