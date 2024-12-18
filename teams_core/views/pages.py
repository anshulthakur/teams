import json
from markdown2 import markdown

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string

from teams_core.models import TestCase, TestRun, TestExecution, TestSuite

from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from teams_core.utils import add_subscription, remove_subscription
from teams_core.export import generate_docx, generate_pdf

from teams_core.utils import create_new_version

def render_markdown_recursive(data):
    """
    Recursively render Markdown strings in a nested dictionary or list using markdown2.
    """
    if isinstance(data, dict):
        return {key: render_markdown_recursive(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [render_markdown_recursive(item) for item in data]
    elif isinstance(data, str):
        # Convert Markdown to HTML with extras
        return markdown(data, extras=["fenced-code-blocks", "tables", "strike", "underline"])
    return data  # Return as-is for other data types

def overview(request):
    return render(request, 'overview.html', {})


def test_case_list(request):
    query = request.GET.get('name', '')  # Get search query
    sorting = request.GET.get('sort', 'modify')  # Default sorting by last modified
    order = request.GET.get('order', 'desc')  # Default order descending
    page_size = request.GET.get('page_size', 25)  # Default page size
    page = request.GET.get('page', 1)  # Current page

    # Handle minor transformation for sorting
    if sorting == 'modify':
        sorting = 'last_modified'
    ordering = f"{'-' if order == 'desc' else ''}{sorting}"

    # Filter and sort test cases
    test_cases = TestCase.objects.all().order_by(ordering)
    if query:
        test_cases = test_cases.filter(Q(name__icontains=query) | Q(oid__icontains=query))

    # Paginate the test cases
    paginator = Paginator(test_cases, int(page_size) if page_size != 'all' else test_cases.count())
    try:
        test_cases = paginator.page(page)
    except PageNotAnInteger:
        test_cases = paginator.page(1)
    except EmptyPage:
        test_cases = paginator.page(paginator.num_pages)

    # HTMX requests should return the table body only
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'test_case/_test_case_table.html', {
            'test_cases': test_cases,
            'search_query': query,
            'current_sort': sorting,
            'current_order': order,
            'page_size': page_size,
        })

    # Non-HTMX requests render the full page
    return render(request, 'test_case/test_case_list.html', {
        'test_cases': test_cases,
        'search_query': query,
        'current_sort': sorting,
        'current_order': order,
        'page_size': page_size,
    })


def test_case_detail(request, id):
    
    test_case = TestCase.objects.get(pk=id)

    # Load and process the JSON content if it exists
    if test_case.content:
        try:
            raw_content = json.loads(test_case.content)
            # Process Markdown recursively
            content = render_markdown_recursive(raw_content)
        except (json.JSONDecodeError, TypeError) as e:
            content = {}  # Fallback to empty content in case of an error
            print(f"Error decoding content for TestCase {test_case.id}: {e}")
    else:
        content = {}

    # Fetch execution history for the test case
    test_executions = TestExecution.objects.filter(testcase=test_case).order_by('-date')
    
    return render(request, 'test_case/test_case_detail.html', {
        'object': test_case,
        'content': content,
        'test_executions': test_executions
    })

@login_required
def version_test_case(request, id):
    """
    Explicitly create a new version of the test case.
    """
    test_case = get_object_or_404(TestCase, pk=id)
    create_new_version(test_case, request.user, version_comment="User finalized version")
    return redirect(test_case.get_absolute_url())

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
        'object': testsuite,
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

@login_required
def mark_notifications_read(request):
    """Mark all unread notifications as read."""
    request.user.notifications.unread().mark_all_as_read()
    if request.headers.get('HX-Request'):
        return HttpResponse('<ul class="list-group mb-4"><li class="list-group-item text-muted">No unread notifications.</li></ul>')
    return redirect('teams_core:all_notifications')

@login_required
def all_notifications(request):
    # Separate notifications into unread and read for clarity
    unread_notifications = request.user.notifications.unread()
    read_notifications = request.user.notifications.read()
    
    return render(request, 'notification/all_notifications.html', {
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications,
    })

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()

    if request.headers.get('HX-Request') == 'true':
        # If the request is from HTMX, return a small HTML snippet instead of redirecting
        return HttpResponse(
            '<span class="text-muted">Marked as Read</span>', content_type="text/html"
        )
    else:
        # Otherwise, redirect to the notifications page
        return redirect('teams_core:all_notifications')

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.delete()
    return redirect('teams_core:all_notifications')

@login_required
def delete_selected_notifications(request):
    if request.method == "POST":
        notification_ids = request.POST.getlist('notifications')
        Notification.objects.filter(id__in=notification_ids, recipient=request.user).delete()
    return redirect('teams_core:all_notifications')

@login_required
def subscribe_to_event(request, object_type, object_id, event_type):
    model = ContentType.objects.get(model=object_type).model_class()
    obj = get_object_or_404(model, id=object_id)
    add_subscription(request.user, event_type, obj)

    context = { 'user': request.user, 'object': obj, }
    html = render_to_string('subscription/subscribe.html', context) 
    return HttpResponse(html)

@login_required
def unsubscribe_from_event(request, object_type, object_id, event_type):
    model = ContentType.objects.get(model=object_type).model_class()
    obj = get_object_or_404(model, id=object_id)
    remove_subscription(request.user, event_type, obj)
    context = { 'user': request.user, 'object': obj, }
    html = render_to_string('subscription/subscribe.html', context) 
    return HttpResponse(html)


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
