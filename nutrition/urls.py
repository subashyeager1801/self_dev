"""Nutrition URL configuration."""
from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    path('', views.food_log_view, name='log'),
    path('add/', views.add_meal_view, name='add_meal'),
    path('api/analyze-photo/', views.analyze_photo_api, name='analyze_photo'),
    path('api/update-entry/', views.update_meal_entry, name='update_entry'),
]
