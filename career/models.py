"""
Career models — Target role, skill gap matrix, milestones, and interview prep.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CareerProfile(models.Model):
    """User career profile and target role aspiration."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='career_profile')
    target_role = models.CharField(max_length=150, default="Software Engineer",
                                   help_text="e.g. Python Backend Developer, AI Engineer, Data Scientist")
    target_industry = models.CharField(max_length=150, blank=True)
    target_timeline = models.CharField(max_length=100, default="6 months")
    current_status = models.CharField(max_length=100, default="Preparing for interviews")
    resume_notes = models.TextField(blank=True)
    interview_readiness_score = models.PositiveIntegerField(default=50, help_text="0 to 100%")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} → {self.target_role}"


class CareerSkill(models.Model):
    """Skills and gap analysis for target role."""
    PROFICIENCY_CHOICES = [
        ('learning', 'Learning / Needs Work ⚠'),
        ('competent', 'Competent / Proficient ✓'),
        ('advanced', 'Advanced / Expert 🌟'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_skills')
    skill_name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='learning')
    is_critical_gap = models.BooleanField(default=False)
    priority_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['priority_order', 'skill_name']

    def __str__(self):
        return f"{self.skill_name} ({self.get_proficiency_display()})"


class CareerMilestone(models.Model):
    """Projects, certifications, and interview preparation targets."""
    CATEGORY_CHOICES = [
        ('project', 'Portfolio Project'),
        ('interview_prep', 'Interview Practice'),
        ('resume', 'Resume / Portfolio'),
        ('job_application', 'Job Application'),
        ('certification', 'Certification / Exam'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_milestones')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='project')
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    deadline = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['completed', 'deadline', '-created_at']

    def __str__(self):
        return f"{self.title} ({'✓' if self.completed else 'Pending'})"
