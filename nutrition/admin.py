from django.contrib import admin
from .models import FoodLog, MealEntry


class MealEntryInline(admin.TabularInline):
    model = MealEntry
    extra = 1


@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'meal_type', 'total_calories', 'total_protein', 'ai_analyzed']
    list_filter = ['meal_type', 'date', 'ai_analyzed']
    search_fields = ['user__username', 'notes']
    inlines = [MealEntryInline]


@admin.register(MealEntry)
class MealEntryAdmin(admin.ModelAdmin):
    list_display = ['food_name', 'food_log', 'portion_size', 'calories', 'protein', 'carbs', 'fat']
    search_fields = ['food_name']
