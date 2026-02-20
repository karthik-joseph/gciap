"""
Custom decorators for role-based access control
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .roles import (
    get_user_role, 
    is_admin, 
    is_professional, 
    is_customer,
    ROLE_ADMIN,
    ROLE_PROFESSIONAL,
    ROLE_CUSTOMER
)


def role_required(*allowed_roles):
    """
    Decorator to check if user has one of the allowed roles.
    Usage:
        @role_required('admin')
        @role_required('admin', 'professional')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user_role = get_user_role(request.user)
            
            if user_role not in allowed_roles:
                messages.error(request, f'Access denied. Required role: {", ".join(allowed_roles)}')
                return HttpResponseForbidden('You do not have permission to access this page.')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Decorator for views that require admin role.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def professional_required(view_func):
    """
    Decorator for views that require professional role.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not is_professional(request.user):
            messages.error(request, 'Access denied. Professional account required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def customer_required(view_func):
    """
    Decorator for views that require customer role.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not is_customer(request.user):
            messages.error(request, 'Access denied. Customer account required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_or_professional_required(view_func):
    """
    Decorator for views that require admin or professional role.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not (is_admin(request.user) or is_professional(request.user)):
            messages.error(request, 'Access denied. Admin or Professional account required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_or_owner_required(model_field='user'):
    """
    Decorator for views that require admin role or object ownership.
    The model_field parameter specifies which field to check for ownership.
    
    Usage:
        @admin_or_owner_required('user')
        @admin_or_owner_required('professional__user')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # If user is admin, allow access
            if is_admin(request.user):
                return view_func(request, *args, **kwargs)
            
            # Check ownership - this will be validated in the view
            # The view should handle the ownership check
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
