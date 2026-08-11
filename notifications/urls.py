"""Notifications URL configuration."""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_center_view, name='center'),
    path('api/preferences/', views.update_preferences_api, name='update_preferences'),
    path('api/mark-read/', views.mark_read_api, name='mark_read'),
    path('api/trigger-test/', views.trigger_test_notification_api, name='trigger_test'),
    path('api/manage-single/', views.manage_single_notification_api, name='manage_single'),
]
