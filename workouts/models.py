"""
Workout models — Exercise library, workout sessions, and exercise completion tracking.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Exercise(models.Model):
    """Exercise library entry."""
    MUSCLE_GROUP_CHOICES = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('shoulders', 'Shoulders'),
        ('biceps', 'Biceps'),
        ('triceps', 'Triceps'),
        ('forearms', 'Forearms'),
        ('quadriceps', 'Quadriceps'),
        ('hamstrings', 'Hamstrings'),
        ('glutes', 'Glutes'),
        ('calves', 'Calves'),
        ('core', 'Core'),
        ('full_body', 'Full Body'),
        ('cardio', 'Cardio'),
    ]

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    name = models.CharField(max_length=100)
    muscle_group = models.CharField(max_length=20, choices=MUSCLE_GROUP_CHOICES)
    secondary_muscles = models.JSONField(default=list, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate')
    equipment = models.JSONField(default=list, blank=True,
                                 help_text='Required equipment list')
    instructions = models.TextField(blank=True)
    is_home_friendly = models.BooleanField(default=False)
    is_gym_exercise = models.BooleanField(default=True)
    calories_per_minute = models.FloatField(default=5.0)
    alternative_exercises = models.ManyToManyField('self', blank=True, symmetrical=True)

    class Meta:
        ordering = ['muscle_group', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_muscle_group_display()})"


class WorkoutSession(models.Model):
    """A workout session (planned or completed)."""
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')

    # AI-generated metadata
    target_muscle_groups = models.JSONField(default=list, blank=True)
    estimated_duration_minutes = models.PositiveIntegerField(default=45)
    difficulty_level = models.CharField(max_length=20, default='intermediate')
    ai_generated = models.BooleanField(default=False)
    ai_notes = models.TextField(blank=True)

    # Completion data
    actual_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    user_rating = models.PositiveIntegerField(null=True, blank=True,
                                               help_text='1-5 difficulty rating from user')
    user_notes = models.TextField(blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} — {self.date}"

    @property
    def completion_percentage(self):
        exercises = self.exercises.all()
        if not exercises:
            return 0
        completed = exercises.filter(completed=True).count()
        return int((completed / exercises.count()) * 100)

    @property
    def total_exercises(self):
        return self.exercises.count()

    @property
    def completed_exercises(self):
        return self.exercises.filter(completed=True).count()


class WorkoutExercise(models.Model):
    """An exercise within a workout session."""
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    # Prescribed
    sets = models.PositiveIntegerField(default=3)
    reps = models.CharField(max_length=20, default='10', help_text='e.g. 10, 8-12, AMRAP')
    rest_seconds = models.PositiveIntegerField(default=60)
    weight_kg = models.FloatField(null=True, blank=True)

    # Completion
    completed = models.BooleanField(default=False)
    actual_sets = models.PositiveIntegerField(null=True, blank=True)
    actual_reps = models.CharField(max_length=50, blank=True)
    actual_weight_kg = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.exercise.name}: {self.sets}×{self.reps}"
