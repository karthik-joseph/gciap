"""
Django management command to view a user's current role.
Usage:
  python manage.py check_role <username>
  
Example:
  python manage.py check_role john
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from users.roles import get_user_role, ROLE_ADMIN, ROLE_PROFESSIONAL, ROLE_CUSTOMER


class Command(BaseCommand):
    help = 'Check the current role of a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')

        role = get_user_role(user)
        
        self.stdout.write(f'\nUser: {user.username}')
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'Active: {user.is_active}')
        self.stdout.write(f'Staff: {user.is_staff}')
        self.stdout.write(f'Superuser: {user.is_superuser}')
        
        # Check for professional profile
        has_professional = hasattr(user, 'professional')
        self.stdout.write(f'Has Professional Profile: {has_professional}')
        
        if has_professional:
            prof = user.professional
            self.stdout.write(f'Professional Type: {prof.professional_type}')
        
        # Display role
        if role == ROLE_ADMIN:
            role_display = self.style.ERROR('ADMIN')
        elif role == ROLE_PROFESSIONAL:
            role_display = self.style.WARNING('PROFESSIONAL')
        elif role == ROLE_CUSTOMER:
            role_display = self.style.SUCCESS('CUSTOMER')
        else:
            role_display = 'UNKNOWN'
        
        self.stdout.write(f'\nCurrent Role: {role_display}\n')
