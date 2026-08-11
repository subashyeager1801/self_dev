"""
Nutrition models — Food logging and meal tracking.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class FoodLog(models.Model):
    """A meal entry (may contain multiple food items)."""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_logs')
    date = models.DateField(default=timezone.now)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='lunch')
    photo = models.ImageField(upload_to='food_photos/%Y/%m/', null=True, blank=True)
    notes = models.TextField(blank=True)

    # AI analysis
    ai_analyzed = models.BooleanField(default=False)
    ai_raw_response = models.TextField(blank=True)

    # Totals (cached from entries)
    total_calories = models.FloatField(default=0)
    total_protein = models.FloatField(default=0)
    total_carbs = models.FloatField(default=0)
    total_fat = models.FloatField(default=0)
    total_fiber = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_meal_type_display()} — {self.date}"

    def update_totals(self):
        """Recalculate totals from entries."""
        entries = self.entries.all()
        self.total_calories = sum(e.calories for e in entries)
        self.total_protein = sum(e.protein for e in entries)
        self.total_carbs = sum(e.carbs for e in entries)
        self.total_fat = sum(e.fat for e in entries)
        self.total_fiber = sum(e.fiber for e in entries)
        self.save()


class MealEntry(models.Model):
    """Individual food item within a meal."""
    food_log = models.ForeignKey(FoodLog, on_delete=models.CASCADE, related_name='entries')
    food_name = models.CharField(max_length=200)
    portion_size = models.CharField(max_length=100, blank=True, help_text='e.g. 1 cup, 200g')

    # Nutrition per portion
    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    fiber = models.FloatField(default=0)

    # User correction
    user_corrected = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.food_name} ({self.calories} kcal)"
