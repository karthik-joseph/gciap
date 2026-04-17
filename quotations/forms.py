from django import forms
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .models import Quotation, QuotationItem

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['project_title', 'project_description', 'budget_estimate', 'professional']
        widgets = {
            'project_title': forms.TextInput(attrs={'placeholder': 'Enter project title'}),
            'project_description': forms.Textarea(attrs={'placeholder': 'Describe your project requirements...', 'rows': 4}),
            'budget_estimate': forms.NumberInput(attrs={'placeholder': '₹ Enter budget estimate', 'min': '0', 'step': '0.01'}),
        }
    
    def clean_budget_estimate(self):
        budget = self.cleaned_data.get('budget_estimate')
        if budget is not None and budget < 0:
            raise ValidationError('Budget estimate cannot be negative')
        if budget is not None and budget == 0:
            raise ValidationError('Budget estimate must be greater than zero')
        return budget
    
    def clean_project_title(self):
        title = self.cleaned_data.get('project_title')
        if title and len(title) < 3:
            raise ValidationError('Project title must be at least 3 characters')
        return title

class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ['item_name', 'quantity', 'unit_price']
        widgets = {
            'item_name': forms.TextInput(attrs={'placeholder': 'Enter item name'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Quantity', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'placeholder': '₹ Unit price', 'min': '0', 'step': '0.01'}),
        }
    
    def clean_item_name(self):
        name = self.cleaned_data.get('item_name')
        if name and len(name) < 2:
            raise ValidationError('Item name must be at least 2 characters')
        return name
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise ValidationError('Quantity must be at least 1')
        return quantity
    
    def clean_unit_price(self):
        price = self.cleaned_data.get('unit_price')
        if price is not None and price < 0:
            raise ValidationError('Unit price cannot be negative')
        if price is not None and price == 0:
            raise ValidationError('Unit price must be greater than zero')
        return price

