from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(models.Model):
    BUDGET_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField(region='IN', help_text='Phone number with country code')
    address = models.TextField(blank=True, null=True)
    budget_preference = models.CharField(max_length=10, choices=BUDGET_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.budget_preference}"


class ProfessionalUpgradeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    PROFESSIONAL_TYPES = [
        ('interior_designer', 'Interior Designer'),
        ('exterior_designer', 'Exterior Designer'),
        ('architect', 'Architect'),
        ('worker', 'Worker'),
        ('contractor', 'Contractor'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upgrade_requests')
    professional_type = models.CharField(max_length=20, choices=PROFESSIONAL_TYPES)
    bio = models.TextField(help_text='Tell us about your professional experience')
    experience_years = models.IntegerField(default=0, help_text='Years of experience')
    phone = models.CharField(max_length=15, help_text='Professional contact number')
    address = models.TextField(help_text='Business/professional address')
    reason = models.TextField(help_text='Why do you want to become a professional?')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True, help_text='Admin review notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_professional_type_display()} ({self.status})"
