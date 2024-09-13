from django.urls import path
from . import views

urlpatterns = [
    path('test-cases/create/', views.test_case_create, name='test_case_create'),
    path('test-cases/edit/<int:id>/', views.test_case_edit, name='test_case_edit'),
    path('', views.test_case_list, name='test_case_list'),
]