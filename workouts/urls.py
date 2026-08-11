"""Workout URL configuration."""
from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    path('', views.workout_list_view, name='list'),
    path('generate/', views.generate_workout_view, name='generate'),
    path('<int:session_id>/', views.workout_detail_view, name='detail'),
    path('api/toggle-exercise/', views.toggle_exercise_complete, name='toggle_exercise'),
    path('api/rate/', views.rate_workout, name='rate_workout'),
]
