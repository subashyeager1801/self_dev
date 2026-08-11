"""
Learning models — Knowledge paths, roadmaps (DSA, AI/ML, Python, English), and study sessions.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class LearningGoal(models.Model):
    """A topic or skill the user is actively learning."""
    CATEGORY_CHOICES = [
        ('programming', 'Programming & Software'),
        ('dsa', 'Data Structures & Algorithms'),
        ('ai_ml', 'AI & Machine Learning'),
        ('math', 'Mathematics & Logic'),
        ('communication', 'Communication & English'),
        ('other', 'Other Skills'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_goals')
    title = models.CharField(max_length=150, help_text="e.g. Python Backend, DSA in C++, Deep Learning")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='programming')
    target_hours = models.PositiveIntegerField(default=50)
    completed_hours = models.FloatField(default=0.0)

    # Roadmap JSON structure: [{"week": 1, "topic": "Arrays & Strings", "completed": True}, ...]
    roadmap = models.JSONField(default=list, blank=True)
    current_topic = models.CharField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-updated_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def progress_percentage(self):
        if not self.roadmap:
            if self.target_hours > 0:
                return min(int((self.completed_hours / self.target_hours) * 100), 100)
            return 0
        total_items = len(self.roadmap)
        completed_items = sum(1 for item in self.roadmap if item.get('completed', False))
        return int((completed_items / total_items) * 100) if total_items > 0 else 0


class LearningSession(models.Model):
    """Log of a completed study or practice session."""
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField(default=timezone.now)
    duration_minutes = models.PositiveIntegerField(default=45)
    topics_covered = models.CharField(max_length=250)
    key_takeaways = models.TextField(blank=True)
    practice_problems_solved = models.PositiveIntegerField(default=0)
    revision_due_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.goal.title} — {self.duration_minutes}m on {self.date}"
