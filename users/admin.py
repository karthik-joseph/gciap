from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'budget_preference', 'created_at']
    list_filter = ['budget_preference', 'created_at']
    search_fields = ['user__username', 'phone']
