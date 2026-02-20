from django.contrib import admin
from .models import Quotation, QuotationItem

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'professional', 'project_title', 'budget_estimate', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project_title', 'user__username', 'professional__user__username']

@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ['quotation', 'item_name', 'quantity', 'unit_price', 'total_price']
    search_fields = ['item_name', 'quotation__project_title']
