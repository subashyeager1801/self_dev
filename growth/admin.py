from django.contrib import admin
from .models import GrowthCategory, Goal, GoalProgress


@admin.register(GrowthCategory)
class GrowthCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'user', 'is_preset']
    list_filter = ['is_preset']
    search_fields = ['name']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'goal_type', 'target_value', 'current_value', 'is_active']
    list_filter = ['goal_type', 'is_active']
    search_fields = ['title', 'user__username']


@admin.register(GoalProgress)
class GoalProgressAdmin(admin.ModelAdmin):
    list_display = ['goal', 'date', 'value']
    list_filter = ['date']
