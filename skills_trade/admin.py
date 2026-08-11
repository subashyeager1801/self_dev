from django.contrib import admin
from .models import SkillTradeListing, TradeRequest


@admin.register(SkillTradeListing)
class SkillTradeListingAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill_offering', 'skill_seeking', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['skill_offering', 'skill_seeking', 'description']


@admin.register(TradeRequest)
class TradeRequestAdmin(admin.ModelAdmin):
    list_display = ['listing', 'sender', 'status', 'created_at']
    list_filter = ['status', 'created_at']
