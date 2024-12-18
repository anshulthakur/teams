from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
import notifications.urls
from . import views

router = DefaultRouter()
router.register(r'testcases', views.TestCaseViewSet)
router.register(r'testruns', views.TestRunViewSet)
router.register(r'testsuites', views.TestSuiteViewSet)
router.register(r'testexecutions', views.TestExecutionViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

app_name = "teams_core"

urlpatterns = [
    path('test-cases', views.test_case_list, name='test_case_list'),
    path('test-cases/create/', views.test_case_create, name='test_case_create'),
    path('test-cases/<int:id>/', views.test_case_detail, name='test_case_detail'),
    path('test-cases/<int:id>/export/<str:format_type>/', views.export_testcase, name='export_testcase'),
    path('test-cases/edit/<int:id>/', views.test_case_edit, name='test_case_edit'),
    path('test-cases/version/<int:id>/', views.version_test_case, name='version_test_case'),
    path('test-suites/', views.test_suite_list, name='test_suite_list'),
    path('test-suites/create/', views.test_suite_create, name='test_suite_create'),
    path('test-suites/<int:id>/', views.test_suite_detail, name='test_suite_detail'),
    path('test-suites/<int:id>/export/<str:format_type>/', views.export_testsuite, name='export_testsuite'),
    path('test-suites/edit/<int:id>/', views.test_suite_edit, name='test_suite_edit'),
    path('test-runs/', views.test_run_list, name='test_run_list'),
    path('test-runs/u/<int:user_id>/', views.test_run_list, name='user_test_run_list'),
    path('test-runs/<int:id>/', views.test_run_detail, name='test_run_detail'),
    path('test-runs/create/', views.test_run_create, name='test_run_create'),
    path('api/upload-image/', views.ImageUploadView.as_view(), name='upload-image'),
    path('api/list-images/', views.ImageListView.as_view(), name='list-images'),
    path('test-cases/', include(router.urls)),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('notifications/', views.all_notifications, name='all_notifications'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/delete-selected/', views.delete_selected_notifications, name='delete_selected_notifications'),
    path('notifications/mark-all-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('<str:object_type>/<int:object_id>/subscribe/<str:event_type>/', views.subscribe_to_event, name='subscribe_to_event'),
    path('<str:object_type>/<int:object_id>/unsubscribe/<str:event_type>/', views.unsubscribe_from_event, name='unsubscribe_from_event'),
    path("metrics/test-health-overview/", views.TestHealthOverviewView.as_view(), name="test_health_overview"),
    path("metrics/frequent-failures/", views.FrequentFailuresView.as_view(), name="frequent_failures"),
    path("metrics/latest-test-run-summary/", views.LatestTestRunSummaryView.as_view(), name="latest_test_run_summary"),
    path("metrics/stable-unstable-tests/", views.StableUnstableTestsView.as_view(), name="stable_unstable_tests"),
    path('', views.overview, name='overview'),
]