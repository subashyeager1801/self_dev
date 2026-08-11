"""
Progress models — Weight history tracking.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class WeightHistory(models.Model):
    """Track weight changes over time."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weight_history')
    date = models.DateField(default=timezone.now)
    weight_kg = models.FloatField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
        verbose_name_plural = 'Weight History'

    def __str__(self):
        return f"{self.user.username} — {self.date}: {self.weight_kg}kg"
