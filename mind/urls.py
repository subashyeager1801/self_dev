"""Mind URL configuration."""
from django.urls import path
from . import views

app_name = 'mind'

urlpatterns = [
    path('', views.mind_dashboard_view, name='dashboard'),
    path('api/checkin/', views.update_checkin_api, name='update_checkin'),
    path('api/journal/', views.create_journal_api, name='create_journal'),
]
