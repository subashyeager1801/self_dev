from django.contrib import admin
from .models import WeightHistory


@admin.register(WeightHistory)
class WeightHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'weight_kg']
    list_filter = ['date']
    search_fields = ['user__username']
