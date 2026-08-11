"""
Dashboard models — DailyProgress and HabitLog for tracking daily metrics.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DailyProgress(models.Model):
    """Daily summary of all tracked metrics."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_progress')
    date = models.DateField(default=timezone.now)

    # Workout
    workout_completed = models.BooleanField(default=False)
    workout_duration_minutes = models.PositiveIntegerField(default=0)

    # Nutrition
    calories_consumed = models.PositiveIntegerField(default=0)
    protein_consumed = models.FloatField(default=0)
    carbs_consumed = models.FloatField(default=0)
    fat_consumed = models.FloatField(default=0)

    # Hydration
    water_liters = models.FloatField(default=0)

    # Sleep
    sleep_hours = models.FloatField(default=0)

    # Steps
    steps = models.PositiveIntegerField(default=0)

    # Learning / Self-dev
    learning_minutes = models.PositiveIntegerField(default=0)
    reading_done = models.BooleanField(default=False)
    meditation_done = models.BooleanField(default=False)

    # Score
    daily_score = models.PositiveIntegerField(default=0, help_text='Calculated score out of 100')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name_plural = 'Daily Progress'

    def __str__(self):
        return f"{self.user.username} — {self.date}"

    def calculate_score(self):
        """Calculate daily progress score based on user targets."""
        profile = self.user.profile
        score = 0
        total_possible = 0

        # Workout (25 points)
        total_possible += 25
        if self.workout_completed:
            score += 25

        # Protein (20 points)
        total_possible += 20
        protein_target = profile.protein_target_grams or profile.estimated_protein_grams or 100
        if protein_target > 0:
            protein_pct = min(self.protein_consumed / protein_target, 1.0)
            score += int(20 * protein_pct)

        # Water (15 points)
        total_possible += 15
        water_target = profile.water_target_liters or 3.0
        if water_target > 0:
            water_pct = min(self.water_liters / water_target, 1.0)
            score += int(15 * water_pct)

        # Sleep (15 points)
        total_possible += 15
        sleep_target = profile.sleep_target_hours or 7.5
        if sleep_target > 0:
            sleep_pct = min(self.sleep_hours / sleep_target, 1.0)
            score += int(15 * sleep_pct)

        # Learning (15 points)
        total_possible += 15
        learning_target = 60  # 60 minutes default
        if learning_target > 0:
            learning_pct = min(self.learning_minutes / learning_target, 1.0)
            score += int(15 * learning_pct)

        # Reading + Meditation (10 points)
        total_possible += 10
        if self.reading_done:
            score += 5
        if self.meditation_done:
            score += 5

        self.daily_score = min(score, 100)
        return self.daily_score


class Habit(models.Model):
    """Custom habit definition."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='✅')
    target_type = models.CharField(max_length=20, choices=[
        ('boolean', 'Yes/No'),
        ('number', 'Number'),
        ('duration', 'Duration (minutes)'),
    ], default='boolean')
    target_value = models.FloatField(default=1, help_text='Target number or 1 for boolean')
    unit = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class HabitLog(models.Model):
    """Daily log for a custom habit."""
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(default=timezone.now)
    value = models.FloatField(default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['habit', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.habit.name} — {self.date}: {self.value}"


class DailyGrowthScore(models.Model):
    """Multi-pillar holistic growth score with AI explainability."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='growth_scores')
    date = models.DateField(default=timezone.now)

    body_score = models.PositiveSmallIntegerField(default=75)
    mind_score = models.PositiveSmallIntegerField(default=75)
    learning_score = models.PositiveSmallIntegerField(default=70)
    career_score = models.PositiveSmallIntegerField(default=65)
    discipline_score = models.PositiveSmallIntegerField(default=75)
    habits_score = models.PositiveSmallIntegerField(default=80)
    overall_score = models.PositiveSmallIntegerField(default=73)

    why_changed_explanation = models.TextField(
        blank=True,
        help_text="AI explanation of why scores shifted compared to recent baseline."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} Holistic Score — {self.date}: {self.overall_score}%"

    def compute_overall(self):
        """Compute weighted overall growth index."""
        weights = [
            self.body_score * 0.20,
            self.mind_score * 0.20,
            self.learning_score * 0.20,
            self.career_score * 0.15,
            self.discipline_score * 0.15,
            self.habits_score * 0.10,
        ]
        self.overall_score = min(int(sum(weights)), 100)
        return self.overall_score


class DailyTask(models.Model):
    """Prioritized daily action items (High, Medium, Low)."""
    PRIORITY_CHOICES = [
        ('high', '🔥 High Priority'),
        ('medium', '⚡ Medium Priority'),
        ('low', '🌱 Low Priority'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_tasks')
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=200)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=50, default='General')
    completed = models.BooleanField(default=False)
    estimated_minutes = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['completed', 'priority', '-created_at']

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title} ({'✓' if self.completed else '○'})"


class EveningReflection(models.Model):
    """End-of-day reflection answering the 3 core coaching questions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reflections')
    date = models.DateField(default=timezone.now)

    what_went_well = models.TextField(help_text="What went well today?")
    what_could_be_better = models.TextField(help_text="What could have been better?")
    one_improvement_tomorrow = models.TextField(help_text="What is one thing you will improve tomorrow?")
    ai_summary = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} Reflection — {self.date}"
