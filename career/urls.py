"""Career URL configuration."""
from django.urls import path
from . import views

app_name = 'career'

urlpatterns = [
    path('', views.career_dashboard_view, name='dashboard'),
    path('api/update-profile/', views.update_career_profile_api, name='update_profile'),
    path('api/skills/', views.manage_skill_api, name='manage_skills'),
    path('api/milestones/', views.manage_milestone_api, name='manage_milestones'),
]
