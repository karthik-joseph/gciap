from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from professionals.models import Professional, Portfolio, ServicePricing
from products.models import Product
from datetime import date

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        if not User.objects.filter(username='testuser').exists():
            user = User.objects.create_user(
                username='testuser',
                email='testuser@example.com',
                password='testpass123'
            )
            UserProfile.objects.create(
                user=user,
                phone='1234567890',
                address='123 Test Street',
                budget_preference='medium'
            )
            self.stdout.write(self.style.SUCCESS('Created test user'))
        
        if not User.objects.filter(username='designer1').exists():
            designer_user = User.objects.create_user(
                username='designer1',
                email='designer1@example.com',
                password='testpass123'
            )
            professional = Professional.objects.create(
                user=designer_user,
                professional_type='interior_designer',
                bio='Experienced interior designer with 10 years of expertise',
                experience_years=10,
                phone='9876543210',
                address='456 Design Avenue',
                is_available=True
            )
            
            ServicePricing.objects.create(
                professional=professional,
                service_name='Living Room Design',
                budget_level='low',
                price=500.00,
                description='Basic living room interior design'
            )
            ServicePricing.objects.create(
                professional=professional,
                service_name='Living Room Design',
                budget_level='medium',
                price=1500.00,
                description='Premium living room interior design'
            )
            ServicePricing.objects.create(
                professional=professional,
                service_name='Living Room Design',
                budget_level='high',
                price=5000.00,
                description='Luxury living room interior design'
            )
            self.stdout.write(self.style.SUCCESS('Created professional'))
        
        if not Product.objects.filter(name='Modern Sofa').exists():
            Product.objects.create(
                name='Modern Sofa',
                category='furniture',
                description='Comfortable modern sofa with premium fabric',
                price=800.00,
                budget_level='medium',
                stock_quantity=50,
                supplier_country='Italy',
                shipping_cost=50.00,
                delivery_days=14
            )
            Product.objects.create(
                name='Wooden Coffee Table',
                category='furniture',
                description='Elegant wooden coffee table',
                price=350.00,
                budget_level='low',
                stock_quantity=100,
                supplier_country='India',
                shipping_cost=30.00,
                delivery_days=7
            )
            Product.objects.create(
                name='Designer Wall Art',
                category='decor',
                description='Contemporary wall art piece',
                price=150.00,
                budget_level='medium',
                stock_quantity=200,
                supplier_country='USA',
                shipping_cost=20.00,
                delivery_days=10
            )
            Product.objects.create(
                name='Premium Tiles',
                category='construction_material',
                description='High-quality ceramic tiles',
                price=50.00,
                budget_level='high',
                stock_quantity=500,
                supplier_country='Spain',
                shipping_cost=100.00,
                delivery_days=21
            )
            self.stdout.write(self.style.SUCCESS('Created products'))
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('Test credentials:')
        self.stdout.write('  User: testuser / testpass123')
        self.stdout.write('  Professional: designer1 / testpass123')
