"""
Mind models — Mental development, daily 1-10 check-in, and journaling with AI reflection.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MoodLog(models.Model):
    """Daily check-in for mental and emotional wellness (1 to 10 scale)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_logs')
    date = models.DateField(default=timezone.now)

    mood = models.PositiveSmallIntegerField(default=7, help_text="1 (Low) to 10 (Excellent)")
    energy = models.PositiveSmallIntegerField(default=7, help_text="1 (Exhausted) to 10 (High Energy)")
    focus = models.PositiveSmallIntegerField(default=7, help_text="1 (Distracted) to 10 (Laser Focused)")
    stress = models.PositiveSmallIntegerField(default=4, help_text="1 (Calm) to 10 (High Stress)")
    motivation = models.PositiveSmallIntegerField(default=7, help_text="1 (Zero) to 10 (Unstoppable)")
    sleep_quality = models.PositiveSmallIntegerField(default=7, help_text="1 (Poor) to 10 (Restful)")
    mental_clarity = models.PositiveSmallIntegerField(default=7, help_text="1 (Brain Fog) to 10 (Clear)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} Check-in — {self.date}"

    @property
    def mind_score(self):
        """Calculates a composite mental wellness score out of 100."""
        # Positive indicators: mood, energy, focus, motivation, sleep_quality, mental_clarity (weight higher)
        # Negative indicator: stress (inverted)
        positives = (self.mood + self.energy + self.focus + self.motivation + self.sleep_quality + self.mental_clarity) / 6.0
        stress_inverted = 11 - self.stress
        composite = (positives * 0.75 + stress_inverted * 0.25) * 10
        return min(max(int(composite), 0), 100)


class JournalEntry(models.Model):
    """Daily reflection and journaling with AI pattern analysis."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(help_text="Write your thoughts, challenges, and reflections here.")

    # AI supportive reflection (non-diagnostic)
    ai_reflection = models.TextField(blank=True)
    detected_patterns = models.JSONField(default=list, blank=True,
                                         help_text="Identified habits, procrastination cues, or strengths")
    actionable_advice = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Journal by {self.user.username} on {self.date}"
