from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from users.decorators import admin_required as role_admin_required

def admin_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='custom_admin:login'):
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, displaying the login page if necessary.
    Now uses the role-based admin check for consistency.
    """
    # Use the new role-based admin_required decorator
    if view_func:
        return role_admin_required(view_func)
    return role_admin_required

