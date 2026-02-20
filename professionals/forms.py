from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Professional, Portfolio, ServicePricing

class ProfessionalForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Select User',
        help_text='Choose which user to convert to professional',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Professional
        fields = ['user', 'professional_type', 'bio', 'experience_years', 'phone', 'address', 'is_available']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'experience_years': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users who are NOT already professionals
        existing_professional_users = Professional.objects.values_list('user_id', flat=True)
        self.fields['user'].queryset = User.objects.exclude(id__in=existing_professional_users)
        
        # Update help text
        self.fields['user'].help_text = f'Select a user to convert to professional ({self.fields["user"].queryset.count()} available)'

    def clean_user(self):
        user = self.cleaned_data.get('user')
        # Check if user already has a professional profile
        if Professional.objects.filter(user=user).exists():
            raise ValidationError(f'{user.username} already has a professional profile.')
        return user

    def clean_experience_years(self):
        years = self.cleaned_data.get('experience_years')
        if years is not None and years < 0:
            raise ValidationError('Experience years cannot be negative')
        return years


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['title', 'description', 'image', 'project_date']
        widgets = {
            'project_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ServicePricingForm(forms.ModelForm):
    class Meta:
        model = ServicePricing
        fields = ['service_name', 'budget_level', 'price', 'description']
        widgets = {
            'price': forms.NumberInput(attrs={'placeholder': '₹ Price', 'min': '0.01'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError('Price must be greater than zero')
        return price

