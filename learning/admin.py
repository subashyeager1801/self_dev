from django.contrib import admin
from .models import LearningGoal, LearningSession


class LearningSessionInline(admin.TabularInline):
    model = LearningSession
    extra = 1


@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'category', 'target_hours', 'completed_hours', 'is_active']
    list_filter = ['category', 'is_active']
    inlines = [LearningSessionInline]


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ['goal', 'date', 'duration_minutes', 'practice_problems_solved']
    list_filter = ['date']
