"""
Skills Trade models — Skill marketplace where users list skills they can teach and skills they want to learn.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SkillTradeListing(models.Model):
    """A peer skill exchange listing created by a user."""
    PROFICIENCY_CHOICES = [
        ('intermediate', 'Intermediate Practitioner'),
        ('advanced', 'Advanced / Professional'),
        ('native_fluent', 'Native / Fluent (Language)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trade_listings')
    skill_offering = models.CharField(max_length=150, help_text="e.g. Python & Django, LeetCode DSA, Spoken English")
    offering_proficiency = models.CharField(max_length=30, choices=PROFICIENCY_CHOICES, default='intermediate')

    skill_seeking = models.CharField(max_length=150, help_text="e.g. Machine Learning, System Design, German")
    description = models.TextField(help_text="Describe how you'd like to collaborate (e.g. 1-hour weekly Zoom sessions).")
    preferred_schedule = models.CharField(max_length=150, default="Weekends / Evenings")
    contact_handle = models.CharField(max_length=120, blank=True, help_text="Email, Discord, or Telegram handle")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: Offers [{self.skill_offering}] ↔ Seeks [{self.skill_seeking}]"


class TradeRequest(models.Model):
    """A connection request between two peers on a listing."""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted & Connected'),
        ('declined', 'Declined'),
    ]

    listing = models.ForeignKey(SkillTradeListing, on_delete=models.CASCADE, related_name='requests')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_trade_requests')
    pitch_message = models.TextField(help_text="Introduce yourself and explain what you can share.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request from {self.sender.username} on '{self.listing.skill_offering}' ({self.status})"
