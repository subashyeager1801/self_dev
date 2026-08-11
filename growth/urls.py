"""Growth URL configuration."""
from django.urls import path
from . import views

app_name = 'growth'

urlpatterns = [
    path('', views.growth_dashboard_view, name='dashboard'),
    path('api/goals/', views.manage_goals, name='manage_goals'),
    path('api/hierarchy/', views.create_hierarchy_api, name='create_hierarchy'),
]
