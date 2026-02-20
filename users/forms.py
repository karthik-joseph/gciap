import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import PhoneNumberField
from .models import UserProfile, ProfessionalUpgradeRequest

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name (Optional)',
            'class': 'form-control'
        })
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Email Address',
        'class': 'form-control'
    }))
    phone = PhoneNumberField(
        region='IN',
        widget=forms.TextInput(attrs={
            'placeholder': '+91 1234567890',
            'class': 'form-control phone-input',
            'id': 'phone'
        }),
        help_text='Enter phone number with country code (e.g., +91 for India)'
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Your Address (Optional)',
            'class': 'form-control'
        }),
        required=False  # Made optional
    )
    budget_preference = forms.ChoiceField(
        choices=UserProfile.BUDGET_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone', 'address', 'budget_preference']

    def clean_username(self):
        """Validate username: only letters, numbers, underscores; must start with a letter or underscore; min 3 chars."""
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', username):
            raise forms.ValidationError(
                "Username must start with a letter or underscore, and contain only letters, numbers, or underscores."
            )
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        return username
    
    def clean_password2(self):
        """Validate that password1 and password2 match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match. Please ensure both passwords are identical.")
        
        return password2
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # The PhoneNumberField already validates format
            # Additional validation can be added here if needed
            return phone
        raise forms.ValidationError("Please enter a valid phone number with country code.")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'budget_preference']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ProfessionalUpgradeRequestForm(forms.ModelForm):
    """Form for regular users to request professional upgrade."""
    class Meta:
        model = ProfessionalUpgradeRequest
        fields = ['professional_type', 'bio', 'experience_years', 'phone', 'address', 'reason']
        widgets = {
            'professional_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about your professional experience and skills...',
                'class': 'form-control'
            }),
            'experience_years': forms.NumberInput(attrs={
                'min': '0',
                'placeholder': 'Years of experience',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Professional contact number',
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Your business/professional address',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Why do you want to become a professional on our platform?',
                'class': 'form-control'
            }),
        }
    
    def clean_experience_years(self):
        years = self.cleaned_data.get('experience_years')
        if years is not None and years < 0:
            raise forms.ValidationError('Experience years cannot be negative.')
        return years


class AdminUserEditForm(forms.ModelForm):
    """Form for admins to edit user details."""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
