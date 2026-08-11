from django.contrib import admin
from .models import DailyProgress, Habit, HabitLog


@admin.register(DailyProgress)
class DailyProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'daily_score', 'workout_completed', 'protein_consumed', 'water_liters', 'sleep_hours']
    list_filter = ['date', 'workout_completed']
    search_fields = ['user__username', 'user__email']


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'icon', 'target_type', 'target_value', 'is_active']
    list_filter = ['is_active', 'target_type']
    search_fields = ['name', 'user__username']


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ['habit', 'date', 'value', 'completed']
    list_filter = ['date', 'completed']
