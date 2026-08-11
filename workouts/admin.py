from django.contrib import admin
from .models import Exercise, WorkoutSession, WorkoutExercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'muscle_group', 'difficulty', 'is_home_friendly', 'is_gym_exercise']
    list_filter = ['muscle_group', 'difficulty', 'is_home_friendly', 'is_gym_exercise']
    search_fields = ['name', 'instructions']


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'date', 'status', 'estimated_duration_minutes', 'user_rating']
    list_filter = ['status', 'date']
    search_fields = ['user__username', 'title']
    inlines = [WorkoutExerciseInline]
