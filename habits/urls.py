"""Habits URL configuration."""
from django.urls import path
from . import views

app_name = 'habits'

urlpatterns = [
    path('', views.habits_dashboard_view, name='dashboard'),
    path('api/toggle/', views.toggle_habit_log_api, name='toggle_habit'),
    path('api/create/', views.create_habit_api, name='create_habit'),
]
