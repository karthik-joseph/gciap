from django import forms
from django.core.exceptions import ValidationError
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'budget_level', 'image', 
                  'stock_quantity', 'supplier_country', 'shipping_cost', 'delivery_days']
        widgets = {
            'price': forms.NumberInput(attrs={'placeholder': '₹ Price', 'min': '0.01'}),
            'shipping_cost': forms.NumberInput(attrs={'placeholder': '₹ Shipping Cost', 'min': '0'}),
            'stock_quantity': forms.NumberInput(attrs={'min': '0'}),
            'delivery_days': forms.NumberInput(attrs={'min': '1'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError('Price must be greater than zero')
        return price

    def clean_stock_quantity(self):
        quantity = self.cleaned_data.get('stock_quantity')
        if quantity is not None and quantity < 0:
            raise ValidationError('Stock quantity cannot be negative')
        return quantity

    def clean_shipping_cost(self):
        cost = self.cleaned_data.get('shipping_cost')
        if cost is not None and cost < 0:
            raise ValidationError('Shipping cost cannot be negative')
        return cost

    def clean_delivery_days(self):
        days = self.cleaned_data.get('delivery_days')
        if days is not None and days < 1:
            raise ValidationError('Delivery days must be at least 1')
        return days

