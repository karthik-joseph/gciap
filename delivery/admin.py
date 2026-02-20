from django.contrib import admin
from .models import Delivery, DeliveryTracking

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'order', 'delivery_partner', 'status', 'estimated_delivery_date', 'actual_delivery_date']
    list_filter = ['status', 'estimated_delivery_date', 'created_at']
    search_fields = ['tracking_number', 'order__user__username', 'delivery_partner']

@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ['delivery', 'location', 'status_update', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['delivery__tracking_number', 'location', 'status_update']
