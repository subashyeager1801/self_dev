"""Progress URL configuration."""
from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('', views.progress_dashboard_view, name='dashboard'),
    path('api/log-weight/', views.log_weight_view, name='log_weight'),
]
