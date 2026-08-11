"""
Coach models — AI conversations, messages, and recommendations.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AIConversation(models.Model):
    """A chat conversation with the AI coach."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=200, default='Coach Chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} — {self.title}"


class AIMessage(models.Model):
    """A message in an AI conversation."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'AI Coach'),
    ]

    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class AIRecommendation(models.Model):
    """AI-generated daily recommendation / motivation."""
    TYPE_CHOICES = [
        ('daily_plan', 'Daily Plan'),
        ('motivation', 'Motivation'),
        ('weekly_report', 'Weekly Report'),
        ('monthly_report', 'Monthly Report'),
        ('tip', 'Tip'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_recommendations')
    rec_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content = models.TextField()
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_rec_type_display()} — {self.date}"


class AIMemoryItem(models.Model):
    """Transparent AI memory items stored about user preferences and patterns."""
    CATEGORY_CHOICES = [
        ('preference', '⚙️ User Preference'),
        ('strength', '💪 Observed Strength'),
        ('weakness', '⚠ Growth Area / Weakness'),
        ('pattern', '🔄 Recurring Pattern'),
        ('goal', '🎯 Milestone Goal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_memories')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='preference')
    title = models.CharField(max_length=150)
    detail = models.TextField()
    confidence = models.CharField(max_length=20, default='High')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', '-updated_at']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title} ({self.user.username})"
