"""
Django management command to assign roles to users.
Usage:
  python manage.py assign_role <username> <role>
  
Example:
  python manage.py assign_role john admin
  python manage.py assign_role mary professional
  python manage.py assign_role bob customer
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from users.roles import ROLE_ADMIN, ROLE_PROFESSIONAL, ROLE_CUSTOMER
from professionals.models import Professional


class Command(BaseCommand):
    help = 'Assign a role to a user (admin, professional, or customer)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument(
            'role',
            type=str,
            choices=['admin', 'professional', 'customer'],
            help='Role to assign (admin, professional, or customer)'
        )

    def handle(self, *args, **options):
        username = options['username']
        role = options['role']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')

        # Apply role-specific settings
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully assigned admin role to user "{username}". '
                    f'User is now staff and superuser.'
                )
            )
        
        elif role == 'professional':
            # Check if professional profile exists
            if hasattr(user, 'professional'):
                self.stdout.write(
                    self.style.WARNING(
                        f'User "{username}" already has a professional profile.'
                    )
                )
            else:
                # Create a basic professional profile
                self.stdout.write(
                    self.style.WARNING(
                        f'User "{username}" needs to complete their professional profile. '
                        f'They should log in and fill out the professional registration form.'
                    )
                )
            
            # Remove admin privileges if they had any
            user.is_staff = False
            user.is_superuser = False
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully set professional role for user "{username}".'
                )
            )
        
        elif role == 'customer':
            # Remove admin privileges and professional profile
            user.is_staff = False
            user.is_superuser = False
            user.save()
            
            # Delete professional profile if exists
            if hasattr(user, 'professional'):
                user.professional.delete()
                self.stdout.write(
                    self.style.WARNING(
                        f'Removed professional profile from user "{username}".'
                    )
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully assigned customer role to user "{username}".'
                )
            )
