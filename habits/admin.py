from django.contrib import admin
from .models import DisciplineHabit, DisciplineHabitLog


@admin.register(DisciplineHabit)
class DisciplineHabitAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'icon', 'frequency', 'current_streak', 'best_streak', 'is_active']
    list_filter = ['frequency', 'is_active']


@admin.register(DisciplineHabitLog)
class DisciplineHabitLogAdmin(admin.ModelAdmin):
    list_display = ['habit', 'date', 'completed']
    list_filter = ['date', 'completed']
