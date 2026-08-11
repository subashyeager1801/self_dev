"""
Habits models — Habit creation, daily streaks, and compassionate restart coaching.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DisciplineHabit(models.Model):
    """Custom tracked habit with streaks and frequency."""
    FREQUENCY_CHOICES = [
        ('daily', 'Every Day'),
        ('weekdays', 'Weekdays Only'),
        ('weekends', 'Weekends Only'),
        ('3x_week', '3 Times / Week'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discipline_habits')
    name = models.CharField(max_length=120)
    icon = models.CharField(max_length=10, default="🎯")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    target_description = models.CharField(max_length=150, blank=True, help_text="e.g. 20 pages, 30 min, 1 session")
    current_streak = models.PositiveIntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_active', 'name']

    def __str__(self):
        return f"{self.icon} {self.name} (Streak: {self.current_streak})"


class DisciplineHabitLog(models.Model):
    """Log for a specific habit on a given date."""
    habit = models.ForeignKey(DisciplineHabit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ['habit', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.habit.name} on {self.date}: {'✓' if self.completed else '✗'}"
