from django.db import models

class Product(models.Model):
    PRODUCT_CATEGORIES = [
        ('furniture', 'Furniture'),
        ('decor', 'Decor'),
        ('construction_material', 'Construction Material'),
    ]
    
    BUDGET_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=25, choices=PRODUCT_CATEGORIES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    budget_level = models.CharField(max_length=10, choices=BUDGET_LEVELS)
    image = models.ImageField(upload_to='products/')
    stock_quantity = models.IntegerField(default=0)
    supplier_country = models.CharField(max_length=100)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_days = models.IntegerField(default=7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.budget_level}"

class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart - {self.user.username}"
    
    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def get_subtotal(self):
        return self.product.price * self.quantity

class Order(models.Model):
    ORDER_STATUS = [
        ('order_placed', 'Order Placed'),
        ('processing', 'Processing'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='order_placed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class OrderStatusHistory(models.Model):
    """Records every status change on an order so the tracking timeline is accurate."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS)
    note = models.CharField(max_length=300, blank=True, default='')
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='order_status_changes'
    )

    class Meta:
        ordering = ['changed_at']

    def __str__(self):
        return f"Order {self.order.id} → {self.status} at {self.changed_at:%Y-%m-%d %H:%M}"

