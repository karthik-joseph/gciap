from django import forms
from django.core.exceptions import ValidationError
from users.models import UserProfile
from professionals.models import Professional, Portfolio, ServicePricing
from products.models import Product
from quotations.models import Quotation, QuotationItem
from bookings.models import Booking
from delivery.models import Delivery, DeliveryTracking

class UserProfileAdminForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'budget_preference']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if len(phone) < 10:
            raise ValidationError('Phone number must be at least 10 digits')
        return phone

class ProfessionalAdminForm(forms.ModelForm):
    class Meta:
        model = Professional
        fields = ['professional_type', 'bio', 'experience_years', 'phone', 'address', 'is_available']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_experience_years(self):
        years = self.cleaned_data.get('experience_years')
        if years < 0:
            raise ValidationError('Experience years cannot be negative')
        if years > 50:
            raise ValidationError('Experience years seems unrealistic (max 50 years)')
        return years

class PortfolioAdminForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['title', 'description', 'image', 'project_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'project_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError('Title must be at least 5 characters')
        return title

class ServicePricingAdminForm(forms.ModelForm):
    class Meta:
        model = ServicePricing
        fields = ['service_name', 'budget_level', 'price', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError('Price must be greater than zero')
        if price > 1000000:
            raise ValidationError('Price seems too high')
        return price

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'price', 'budget_level',
            'image', 'stock_quantity', 'supplier_country', 'shipping_cost', 'delivery_days'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError('Product name must be at least 3 characters')
        return name
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError('Price must be greater than zero')
        return price
    
    def clean_stock_quantity(self):
        quantity = self.cleaned_data.get('stock_quantity')
        if quantity < 0:
            raise ValidationError('Stock quantity cannot be negative')
        return quantity
    
    def clean_shipping_cost(self):
        cost = self.cleaned_data.get('shipping_cost')
        if cost < 0:
            raise ValidationError('Shipping cost cannot be negative')
        return cost
    
    def clean_delivery_days(self):
        days = self.cleaned_data.get('delivery_days')
        if days < 1:
            raise ValidationError('Delivery days must be at least 1 day')
        if days > 365:
            raise ValidationError('Delivery days seems too long (max 365 days)')
        return days

class QuotationAdminForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['user', 'professional', 'project_title', 'project_description', 'budget_estimate', 'status']
        widgets = {
            'project_description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_budget_estimate(self):
        budget = self.cleaned_data.get('budget_estimate')
        if budget <= 0:
            raise ValidationError('Budget estimate must be greater than zero')
        return budget

class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user', 'professional', 'service', 'booking_date', 'booking_time', 'status', 'notes']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class DeliveryAdminForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = [
            'tracking_number', 'delivery_partner', 'estimated_delivery_date',
            'actual_delivery_date', 'status', 'current_location'
        ]
        widgets = {
            'estimated_delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'actual_delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_tracking_number(self):
        tracking = self.cleaned_data.get('tracking_number')
        if len(tracking) < 5:
            raise ValidationError('Tracking number must be at least 5 characters')
        
        if self.instance.pk:
            if Delivery.objects.exclude(pk=self.instance.pk).filter(tracking_number=tracking).exists():
                raise ValidationError('Tracking number must be unique')
        else:
            if Delivery.objects.filter(tracking_number=tracking).exists():
                raise ValidationError('Tracking number must be unique')
        
        return tracking

class DeliveryTrackingAdminForm(forms.ModelForm):
    class Meta:
        model = DeliveryTracking
        fields = ['location', 'status_update']
        widgets = {
            'status_update': forms.Textarea(attrs={'rows': 2}),
        }
