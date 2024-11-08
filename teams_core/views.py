import os
import json
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication

from teams_core.models import TestCase, TestRun, TestExecution, TestSuite
from teams_core.serializers import TestCaseSerializer, TestRunSerializer, TestExecutionSerializer, TestSuiteSerializer, UserSerializer, GroupSerializer
#from teams_core.auth import CsrfExemptSessionAuthentication

from .export import generate_docx, generate_pdf

def test_case_list(request):
    query = request.GET.get('name')
    sorting = request.GET.get('sort', 'modify')  # Default to sorting by last modified

    # Determine ordering
    ordering = '-last_modified'
    if sorting == 'modify_asc':
        ordering = 'last_modified'
    elif sorting == 'name_asc':
        ordering = 'name'
    elif sorting == 'name':
        ordering = '-name'
    elif sorting == 'oid_asc':
        ordering = 'oid'
    elif sorting == 'oid':
        ordering = '-oid'
        
    test_cases = TestCase.objects.all().order_by(ordering)

    # Filter by search query if provided
    if query:
        test_cases = test_cases.filter(Q(name__icontains=query) | Q(oid__icontains=query))

    # Render only the table if the request is from HTMX
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'test_case/_test_case_table.html', {
            'test_cases': test_cases,
            'current_sort': sorting
        })

    # Render the full page for non-HTMX requests
    return render(request, 'test_case/test_case_list.html', {
        'test_cases': test_cases,
        'current_sort': sorting
    })

def test_case_detail(request, id):
    
    test_case = TestCase.objects.get(pk=id)

    if test_case.content != None:
        if len(test_case.content)>0:
            content = json.loads(test_case.content)
        else:
            content = ''
    else:
        content = ''

    # Fetch execution history for the test case
    test_executions = TestExecution.objects.filter(testcase=test_case).order_by('-date')
    
    return render(request, 'test_case/test_case_detail.html', {
        'testcase': test_case,
        'content': content,
        'test_executions': test_executions
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

    # # Calculate testing statistics for each test case
    # test_case_stats = []
    # for testcase in test_cases:
    #     total_runs = TestExecution.objects.filter(testcase=testcase).count()
    #     successful_runs = TestExecution.objects.filter(testcase=testcase, result='PASS').count()

    #     test_case_stats.append({
    #         'testcase': testcase,
    #         'total_runs': total_runs,
    #         'successful_runs': successful_runs
    #     })

    return render(request, 'test_suite/test_suite_detail.html', {
        'testsuite': testsuite,
        'testcases': test_cases
    })

@login_required
def test_suite_create(request):
    return render(request, 'test_suite/test_suite_form.html', {})

@login_required
def test_suite_edit(request, id):
    test_suite = TestSuite.objects.get(pk=id)
    return render(request, 'test_suite/test_suite_form.html', {'testsuite': test_suite})


def test_run_list(request, user_id=None):
    # Get all published test runs by default
    test_runs = TestRun.objects.filter(published=True).order_by('-date')

    # Filter by user if `user_id` is provided
    if user_id:
        # Check if the request is made by the same user whose runs are being requested
        requested_user = get_object_or_404(User, pk=user_id)
        if request.user.is_authenticated and request.user.id == requested_user.id:
            # Show both published and private runs for the logged-in user
            test_runs = TestRun.objects.filter(created_by=requested_user).order_by('-date')
        else:
            # For other users, show only published runs of the specified user
            test_runs = TestRun.objects.filter(created_by=requested_user, published=True).order_by('-date')

    return render(request, 'test_run/test_run_list.html', {
        'test_runs': test_runs
    })

@require_http_methods(["GET", "PATCH"])
def test_run_detail(request, id):
    test_run = get_object_or_404(TestRun, id=id)
    if request.method == "PATCH":
        # Ensure the user has permission to publish/unpublish
        if request.user == test_run.created_by or request.user.is_staff:
            publish = request.POST.get('published') == 'true'
            test_run.published = publish
            test_run.save()

        # Redirect back to the detail page to refresh the view
        return redirect('teams_core:test_run_list')  # Reloads the test run list page
    
    test_executions = test_run.testexecution_set.all()  # Get all executions for this run

    # Get search query for TestExecutions by TestCase name or oid
    query = request.GET.get('name')
    if query:
        test_executions = test_executions.filter(
            Q(testcase__name__icontains=query) | Q(testcase__oid__icontains=query)
        )

    # If the request is from HTMX, return only the filtered rows
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'test_run/_test_execution_table.html', {
            'test_executions': test_executions
        })

    # Otherwise, render the full page template
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
        print('perform create')
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