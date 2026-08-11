"""
Account models — UserProfile stores all personal data for AI personalization.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """Extended user profile for fitness + self-development personalization."""

    # --- Choices ---
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not', 'Prefer not to say'),
    ]

    FITNESS_GOAL_CHOICES = [
        ('fat_loss', 'Fat Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('athletic', 'Athletic Body'),
        ('strength', 'Strength'),
        ('general', 'General Fitness'),
        ('maintain', 'Maintain Current Body'),
    ]

    EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    WORKOUT_LOCATION_CHOICES = [
        ('home', 'Home'),
        ('gym', 'Gym'),
    ]

    # --- Relations ---
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # --- Personal info ---
    age = models.PositiveIntegerField(null=True, blank=True,
                                      validators=[MinValueValidator(13), MaxValueValidator(100)])
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    height_cm = models.FloatField(null=True, blank=True, help_text='Height in centimeters',
                                  validators=[MinValueValidator(50), MaxValueValidator(300)])
    weight_kg = models.FloatField(null=True, blank=True, help_text='Current weight in kg',
                                  validators=[MinValueValidator(20), MaxValueValidator(500)])
    target_weight_kg = models.FloatField(null=True, blank=True, help_text='Target weight in kg',
                                         validators=[MinValueValidator(20), MaxValueValidator(500)])

    # --- Fitness profile ---
    fitness_goal = models.CharField(max_length=20, choices=FITNESS_GOAL_CHOICES, default='general')
    body_goal = models.TextField(blank=True, help_text='Describe your ideal body goal')
    fitness_experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')

    # --- Workout preferences ---
    workout_location = models.CharField(max_length=10, choices=WORKOUT_LOCATION_CHOICES, default='home')
    available_equipment = models.JSONField(default=list, blank=True,
                                           help_text='List of available equipment')
    daily_workout_minutes = models.PositiveIntegerField(default=45,
                                                        validators=[MinValueValidator(10), MaxValueValidator(180)])
    workout_days_per_week = models.PositiveIntegerField(default=4,
                                                        validators=[MinValueValidator(1), MaxValueValidator(7)])

    # --- Daily targets ---
    sleep_target_hours = models.FloatField(default=7.5,
                                           validators=[MinValueValidator(4), MaxValueValidator(12)])
    water_target_liters = models.FloatField(default=3.0,
                                            validators=[MinValueValidator(1), MaxValueValidator(10)])
    calorie_target = models.PositiveIntegerField(null=True, blank=True,
                                                  help_text='Daily calorie target (auto-calculated if blank)')
    protein_target_grams = models.PositiveIntegerField(null=True, blank=True,
                                                       help_text='Daily protein target in grams')

    # --- Daily Schedule & Free Time ---
    daily_schedule = models.CharField(max_length=200, blank=True, help_text="e.g. 9-5 Job, College Student, Freelancer")
    available_free_hours = models.FloatField(default=3.0, help_text="Available hours per day for growth/workout")

    # --- Self-development & Mental goals ---
    self_dev_goals = models.TextField(blank=True, help_text='Comma-separated self-development goals')
    mental_development_goals = models.JSONField(default=list, blank=True,
                                                help_text="e.g. ['Better focus', 'Reduce procrastination', 'Better sleep']")
    learning_goals_list = models.JSONField(default=list, blank=True,
                                           help_text="e.g. ['Python', 'DSA', 'AI/ML', 'English']")
    career_target_role = models.CharField(max_length=150, blank=True, help_text="e.g. Python Backend Developer")
    career_current_skills = models.JSONField(default=list, blank=True)
    career_skills_to_learn = models.JSONField(default=list, blank=True)
    personal_long_term_goals = models.TextField(blank=True, help_text="Custom 5-10 year aspirations")

    # --- Profile state ---
    profile_completed = models.BooleanField(default=False)
    onboarding_step = models.PositiveIntegerField(default=1)
    avatar_color = models.CharField(max_length=7, default='#6C5CE7',
                                    help_text='Hex color for avatar')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def bmi(self):
        """Calculate BMI from height and weight."""
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 1)
        return None

    @property
    def estimated_daily_calories(self):
        """Estimate daily calorie needs using Mifflin-St Jeor equation."""
        if not all([self.age, self.height_cm, self.weight_kg, self.gender]):
            return None

        if self.gender == 'male':
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age + 5
        else:
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age - 161

        # Activity multiplier based on workout frequency
        if self.workout_days_per_week <= 2:
            multiplier = 1.375
        elif self.workout_days_per_week <= 4:
            multiplier = 1.55
        else:
            multiplier = 1.725

        tdee = bmr * multiplier

        # Adjust for goal
        if self.fitness_goal == 'fat_loss':
            return int(tdee * 0.8)  # 20% deficit
        elif self.fitness_goal == 'muscle_gain':
            return int(tdee * 1.1)  # 10% surplus
        else:
            return int(tdee)

    @property
    def estimated_protein_grams(self):
        """Estimate daily protein needs."""
        if not self.weight_kg:
            return None
        multiplier_map = {
            'fat_loss': 2.0,
            'muscle_gain': 2.2,
            'athletic': 1.8,
            'strength': 2.0,
            'general': 1.6,
            'maintain': 1.6,
        }
        multiplier = multiplier_map.get(self.fitness_goal, 1.6)
        return int(self.weight_kg * multiplier)

    def get_display_name(self):
        """Get the user's display name."""
        return self.user.first_name or self.user.username
