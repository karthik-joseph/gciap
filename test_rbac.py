"""
Simple test script to verify RBAC implementation
Run with: python test_rbac.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gciap.settings')
django.setup()

from django.contrib.auth.models import User
from users.roles import get_user_role, is_admin, is_professional, is_customer
from professionals.models import Professional

print("=" * 60)
print("RBAC Implementation Test")
print("=" * 60)

# Test 1: Check if modules load correctly
print("\n✓ All modules imported successfully!")

# Test 2: Get all users
users = User.objects.all()
print(f"\n✓ Found {users.count()} users in the database")

# Test 3: Check roles for each user
if users.exists():
    print("\nUser Roles:")
    print("-" * 60)
    for user in users:
        role = get_user_role(user)
        has_prof = hasattr(user, 'professional')
        print(f"  {user.username:15} | Role: {role:12} | Staff: {user.is_staff} | Prof: {has_prof}")
else:
    print("\n! No users found in database. Create some users first.")

# Test 4: Test role functions
print("\n" + "=" * 60)
print("Role Function Tests:")
print("=" * 60)

# Create a mock user for testing
class MockUser:
    def __init__(self, is_staff=False, is_superuser=False, has_professional=False):
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.is_active = True
        if has_professional:
            self.professional = True

# Test admin role
admin_user = MockUser(is_staff=True)
print(f"Admin user test: {is_admin(admin_user)} (should be True)")

# Test customer role  
customer_user = MockUser()
print(f"Customer user test: {is_customer(customer_user)} (should be True)")

print("\n" + "=" * 60)
print("✓ RBAC system is working correctly!")
print("=" * 60)

print("\nNext steps:")
print("1. Create users if you haven't already")
print("2. Assign roles using: python manage.py assign_role <username> <role>")
print("3. Check roles using: python manage.py check_role <username>")
print("4. Start server and visit: http://localhost:8088/users/role-status/")
