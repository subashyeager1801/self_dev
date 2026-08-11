from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'gender', 'fitness_goal', 'fitness_experience',
                    'workout_location', 'profile_completed']
    list_filter = ['fitness_goal', 'fitness_experience', 'workout_location', 'profile_completed']
    search_fields = ['user__username', 'user__email', 'user__first_name']
    readonly_fields = ['created_at', 'updated_at']
