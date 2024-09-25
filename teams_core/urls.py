from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'testcases', views.TestCaseViewSet)


urlpatterns = [
    path('test-cases/create/', views.test_case_create, name='test_case_create'),
    path('test-cases/<int:id>/', views.test_case_detail, name='test_case_detail'),
    path('test-cases/edit/<int:id>/', views.test_case_edit, name='test_case_edit'),
    path('api/upload-image/', views.ImageUploadView.as_view(), name='upload-image'),
    path('api/list-images/', views.ImageListView.as_view(), name='list-images'),
    path('test-cases/', include(router.urls)),
    path('api/', include('rest_framework.urls')),  # Ensure DRF URLs are included
    path('', views.test_case_list, name='test_case_list'),
]