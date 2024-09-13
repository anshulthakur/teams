from django.shortcuts import render
from .models import TestCase

def test_case_list(request):
    query = request.GET.get('q')  # Get search query from URL
    test_cases = TestCase.objects.all()

    # Filter by search query if provided
    if query:
        test_cases = test_cases.filter(name__icontains=query)

    return render(request, 'test_case/test_case_list.html', {
        'test_cases': test_cases
    })


def test_case_create(request):
    query = request.GET.get('q')  # Get search query from URL
    test_cases = TestCase.objects.all()

    # Filter by search query if provided
    if query:
        test_cases = test_cases.filter(name__icontains=query)

    return render(request, 'test_case/test_case_list.html', {
        'test_cases': test_cases
    })

def test_case_edit(request):
    query = request.GET.get('q')  # Get search query from URL
    test_cases = TestCase.objects.all()

    # Filter by search query if provided
    if query:
        test_cases = test_cases.filter(name__icontains=query)

    return render(request, 'test_case/test_case_list.html', {
        'test_cases': test_cases
    })