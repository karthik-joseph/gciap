from django.db import models
from django.contrib.auth.models import User

class Professional(models.Model):
    PROFESSIONAL_TYPES = [
        ('interior_designer', 'Interior Designer'),
        ('exterior_designer', 'Exterior Designer'),
        ('architect', 'Architect'),
        ('worker', 'Worker'),
        ('contractor', 'Contractor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    professional_type = models.CharField(max_length=20, choices=PROFESSIONAL_TYPES)
    bio = models.TextField()
    experience_years = models.IntegerField(default=0)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.professional_type}"

class Portfolio(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='portfolios')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolios/')
    project_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.professional.user.username} - {self.title}"

class ServicePricing(models.Model):
    BUDGET_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='pricings')
    service_name = models.CharField(max_length=200)
    budget_level = models.CharField(max_length=10, choices=BUDGET_LEVELS)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.professional.user.username} - {self.service_name} ({self.budget_level})"
