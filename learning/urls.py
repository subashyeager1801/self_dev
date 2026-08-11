"""Learning URL configuration."""
from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('', views.learning_dashboard_view, name='dashboard'),
    path('api/create-roadmap/', views.create_roadmap_api, name='create_roadmap'),
    path('api/toggle-topic/', views.toggle_roadmap_topic_api, name='toggle_topic'),
    path('api/log-session/', views.log_study_session_api, name='log_session'),
]
