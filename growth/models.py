"""
Growth models — Self-development goals and progress tracking.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class GrowthCategory(models.Model):
    """Category for self-development goals."""
    PRESET_CATEGORIES = [
        ('fitness', 'Fitness', '💪'),
        ('learning', 'Learning', '📚'),
        ('career', 'Career', '💼'),
        ('coding', 'Coding', '💻'),
        ('ai', 'AI / ML', '🤖'),
        ('reading', 'Reading', '📖'),
        ('discipline', 'Discipline', '🎯'),
        ('sleep', 'Sleep', '😴'),
        ('productivity', 'Productivity', '⚡'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='growth_categories')
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='🎯')
    is_preset = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Growth Categories'

    def __str__(self):
        return f"{self.icon} {self.name}"


class Goal(models.Model):
    """A self-development goal."""
    GOAL_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('long_term', 'Long-term'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    category = models.ForeignKey(GrowthCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default='long_term')
    target_value = models.FloatField(default=100, help_text='Target value or percentage')
    current_value = models.FloatField(default=0)
    unit = models.CharField(max_length=50, blank=True, help_text='e.g. hours, chapters, problems')
    is_active = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-updated_at']

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(int((self.current_value / self.target_value) * 100), 100)

    @property
    def is_completed(self):
        return self.current_value >= self.target_value


class GoalProgress(models.Model):
    """Daily progress on a goal."""
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='progress_logs')
    date = models.DateField(default=timezone.now)
    value = models.FloatField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['goal', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.goal.title} — {self.date}: {self.value}"


class GoalHierarchy(models.Model):
    """Cascading long-term vision into actionable steps."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goal_hierarchies')
    ten_year_vision = models.CharField(max_length=250, help_text="e.g. Become a Lead AI Architect & Achieve Complete Financial Independence")
    yearly_goal = models.CharField(max_length=250, help_text="e.g. Land Senior Backend/AI Role & Save $20k")
    monthly_goal = models.CharField(max_length=250, help_text="e.g. Build 2 Production AI Projects & Solve 60 LeetCode Mediums")
    weekly_goal = models.CharField(max_length=250, help_text="e.g. Complete System Design Module & 5 Gym Sessions")
    daily_action = models.CharField(max_length=250, help_text="e.g. 90 min focused coding + 45 min workout today")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Vision: {self.ten_year_vision[:40]}..."
