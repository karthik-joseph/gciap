from django.contrib import admin
from .models import Professional, Portfolio, ServicePricing

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ['user', 'professional_type', 'experience_years', 'is_available', 'created_at']
    list_filter = ['professional_type', 'is_available', 'created_at']
    search_fields = ['user__username', 'phone']

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['professional', 'title', 'project_date', 'created_at']
    list_filter = ['project_date', 'created_at']
    search_fields = ['title', 'professional__user__username']

@admin.register(ServicePricing)
class ServicePricingAdmin(admin.ModelAdmin):
    list_display = ['professional', 'service_name', 'budget_level', 'price', 'created_at']
    list_filter = ['budget_level', 'created_at']
    search_fields = ['service_name', 'professional__user__username']
