"""Dashboard URL configuration."""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('api/daily-progress/', views.home_view, name='update_daily_progress'),
    path('api/tasks/', views.manage_tasks_api, name='manage_tasks'),
    path('api/reflection/', views.save_reflection_api, name='save_reflection'),
]
