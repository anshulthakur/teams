from collections import Counter
from django.db.models import Count
from django.db.models import Q, F, FloatField, ExpressionWrapper
from teams_core.models import *

def get_test_health_overview():
    """
    Computes the distribution of test results across all test executions
    belonging to published test runs.
    Returns a dictionary with counts for each result type.
    """
    results = TestExecution.objects.filter(run__published=True).values_list("result", flat=True)
    return dict(Counter(results))

def get_frequent_failures(limit=5):
    """
    Finds the most frequently failing test cases from published test runs.
    Returns a queryset with test case names and their failure counts.
    """
    return (
        TestExecution.objects.filter(result="FAIL", run__published=True)
        .values("testcase__name")
        .annotate(failures=Count("id"))
        .order_by("-failures")[:limit]
    )

def get_latest_test_run_summary(limit=5):
    """
    Fetches the latest published test runs and their result summaries.
    Returns a list of dictionaries with the run name and result counts.
    """
    test_runs = TestRun.objects.filter(published=True).order_by("-date")[:limit]
    summaries = []

    for run in test_runs:
        result_counts = (
            TestExecution.objects.filter(run=run)
            .values("result")
            .annotate(count=Count("id"))
        )
        summaries.append({
            "run": str(run),
            "results": {entry["result"]: entry["count"] for entry in result_counts}
        })

    return summaries

def get_stable_and_unstable_tests(limit=5):
    """
    Finds the most stable and unstable tests based on pass and failure ratios,
    considering only published test runs.
    Returns two lists: stable_tests, unstable_tests.
    """
    queryset = TestCase.objects.annotate(
        total_runs=Count("testexecution", filter=Q(testexecution__run__published=True)),
        pass_count=Count(
            "testexecution", filter=Q(testexecution__result="PASS", testexecution__run__published=True)
        ),
        fail_count=Count(
            "testexecution", filter=Q(testexecution__result="FAIL", testexecution__run__published=True)
        ),
        pass_ratio=ExpressionWrapper(
            F("pass_count") * 1.0 / F("total_runs"), output_field=FloatField()
        ),
        fail_ratio=ExpressionWrapper(
            F("fail_count") * 1.0 / F("total_runs"), output_field=FloatField()
        ),
    ).filter(total_runs__gt=0)

    stable_tests = queryset.order_by("-pass_ratio")[:limit]
    unstable_tests = queryset.order_by("-fail_ratio")[:limit]

    return stable_tests, unstable_tests

