from django.contrib import admin
from .models import MoodLog, JournalEntry


@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'mood', 'energy', 'focus', 'stress', 'motivation']
    list_filter = ['date']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'date', 'created_at']
    search_fields = ['title', 'content', 'ai_reflection']
