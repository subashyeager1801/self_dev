"""
Notifications models — User reminder preferences and in-app notifications.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class NotificationPreference(models.Model):
    """User preferences for daily reminders."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')

    workout_reminder = models.BooleanField(default=True, help_text="Daily workout prompt")
    water_reminder = models.BooleanField(default=True, help_text="Hydration check")
    meal_reminder = models.BooleanField(default=True, help_text="Food logging reminders")
    learning_reminder = models.BooleanField(default=True, help_text="Study & skill session prompt")
    habit_reminder = models.BooleanField(default=True, help_text="Daily habit check")
    sleep_reminder = models.BooleanField(default=True, help_text="Bedtime wind-down reminder")
    reflection_reminder = models.BooleanField(default=True, help_text="Evening review prompt")

    morning_reminder_time = models.TimeField(default="08:00:00")
    evening_reminder_time = models.TimeField(default="21:30:00")

    def __str__(self):
        return f"Preferences for {self.user.username}"


class InAppNotification(models.Model):
    """In-app alert or reminder."""
    NOTIFICATION_TYPES = [
        ('coach', '🤖 AI Coach Notice'),
        ('workout', '💪 Workout Reminder'),
        ('habit', '🎯 Habit Check'),
        ('trade', '🤝 Skill Trade Update'),
        ('system', '⚡ System Alert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='coach')
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} to {self.user.username}"
