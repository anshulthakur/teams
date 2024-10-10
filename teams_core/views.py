from datetime import datetime
import os
from django.shortcuts import render
from .models import TestCase

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated

from rest_framework import viewsets
from .models import TestCase, TestRun, TestExecution
from .serializers import TestCaseSerializer, TestRunSerializer, TestExecutionSerializer
import json
from django.contrib.auth.decorators import login_required
from .auth import CsrfExemptSessionAuthentication

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
    authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class

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
    
class TestCaseViewSet(viewsets.ModelViewSet):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class


class TestRunViewSet(viewsets.ModelViewSet):
    queryset = TestRun.objects.all().order_by('-date')
    serializer_class = TestRunSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class TestExecutionViewSet(viewsets.ModelViewSet):
    queryset = TestExecution.objects.all()
    serializer_class = TestExecutionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [CsrfExemptSessionAuthentication]  # Apply custom authentication class
