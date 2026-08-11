from django.contrib import admin
from .models import CareerProfile, CareerSkill, CareerMilestone


@admin.register(CareerProfile)
class CareerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_role', 'interview_readiness_score', 'updated_at']


@admin.register(CareerSkill)
class CareerSkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill_name', 'proficiency', 'is_critical_gap', 'priority_order']
    list_filter = ['proficiency', 'is_critical_gap']


@admin.register(CareerMilestone)
class CareerMilestoneAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'category', 'completed', 'deadline']
    list_filter = ['category', 'completed']
