from django.db import models

class Delivery(models.Model):
    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    
    order = models.OneToOneField('products.Order', on_delete=models.CASCADE, related_name='delivery')
    tracking_number = models.CharField(max_length=100, unique=True)
    delivery_partner = models.CharField(max_length=100)
    estimated_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending')
    current_location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Delivery {self.tracking_number} - {self.status}"

class DeliveryTracking(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='tracking_updates')
    location = models.CharField(max_length=200)
    status_update = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.delivery.tracking_number} - {self.status_update}"
    
    class Meta:
        ordering = ['-timestamp']
