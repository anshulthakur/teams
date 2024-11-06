from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

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
    path('test-cases/create/', views.test_case_create, name='test_case_create'),
    path('test-cases/<int:id>/', views.test_case_detail, name='test_case_detail'),
    path('test-cases/<int:id>/export/<str:format_type>/', views.export_testcase, name='export_testcase'),
    path('test-cases/edit/<int:id>/', views.test_case_edit, name='test_case_edit'),
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
    path('', views.test_case_list, name='test_case_list'),
]