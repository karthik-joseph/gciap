"""
Middleware for role-based access control
"""
from django.shortcuts import redirect
from django.contrib import messages
from .roles import get_user_role, ROLE_ADMIN, ROLE_PROFESSIONAL, ROLE_CUSTOMER


class RoleBasedAccessMiddleware:
    """
    Middleware to enforce role-based access control on specific URL patterns.
    This provides an additional layer of security beyond view decorators.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define URL patterns and their required roles
        self.protected_patterns = {
            '/admin/': [ROLE_ADMIN],  # Django admin
            '/custom-admin/': [ROLE_ADMIN],  # Custom admin panel
            '/professionals/dashboard/': [ROLE_PROFESSIONAL, ROLE_ADMIN],
            '/professionals/create-professional/': [ROLE_CUSTOMER, ROLE_ADMIN],
            '/professionals/add-portfolio/': [ROLE_PROFESSIONAL, ROLE_ADMIN],
            '/professionals/add-pricing/': [ROLE_PROFESSIONAL, ROLE_ADMIN],
        }
    
    def __call__(self, request):
        # Check if the request path requires role-based access control
        if request.user.is_authenticated:
            user_role = get_user_role(request.user)
            
            # Check each protected pattern
            for pattern, allowed_roles in self.protected_patterns.items():
                if request.path.startswith(pattern):
                    if user_role not in allowed_roles:
                        messages.error(
                            request,
                            f'Access denied. You do not have permission to access this area.'
                        )
                        return redirect('home')
        
        response = self.get_response(request)
        return response


class UserRoleContextMiddleware:
    """
    Middleware to add user role information to request context.
    This makes role information easily accessible in templates and views.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            request.user_role = get_user_role(request.user)
            request.is_admin = request.user_role == ROLE_ADMIN
            request.is_professional = request.user_role == ROLE_PROFESSIONAL
            request.is_customer = request.user_role == ROLE_CUSTOMER
        else:
            request.user_role = None
            request.is_admin = False
            request.is_professional = False
            request.is_customer = False
        
        response = self.get_response(request)
        return response
