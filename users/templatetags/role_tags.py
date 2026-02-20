"""
Template tags for role-based access control.

Usage in templates:
    {% load role_tags %}
    
    {% if request.user|is_admin %}
        <p>You are an admin</p>
    {% endif %}
    
    {% if request.user|is_professional %}
        <p>You are a professional</p>
    {% endif %}
    
    {% if request.user|is_customer %}
        <p>You are a customer</p>
    {% endif %}
    
    {% if request.user|has_role:"admin" %}
        <p>Admin only content</p>
    {% endif %}
    
    {% user_role request.user as role %}
    <p>Your role is: {{ role }}</p>
"""
from django import template
from users.roles import (
    get_user_role,
    is_admin,
    is_professional,
    is_customer,
    has_permission
)

register = template.Library()


@register.filter
def user_role(user):
    """
    Template filter to get the role of a user.
    Usage: {{ request.user|user_role }}
    """
    return get_user_role(user)


@register.filter
def is_admin_user(user):
    """
    Template filter to check if user is admin.
    Usage: {% if request.user|is_admin_user %}
    """
    return is_admin(user)


@register.filter
def is_professional_user(user):
    """
    Template filter to check if user is professional.
    Usage: {% if request.user|is_professional_user %}
    """
    return is_professional(user)


@register.filter
def is_customer_user(user):
    """
    Template filter to check if user is customer.
    Usage: {% if request.user|is_customer_user %}
    """
    return is_customer(user)


@register.filter
def has_role(user, role):
    """
    Template filter to check if user has a specific role.
    Usage: {% if request.user|has_role:"admin" %}
    """
    return get_user_role(user) == role


@register.filter
def user_has_permission(user, permission):
    """
    Template filter to check if user has a specific permission.
    Usage: {% if request.user|user_has_permission:"manage_products" %}
    """
    return has_permission(user, permission)


@register.simple_tag
def get_user_role_tag(user):
    """
    Simple tag to get user role.
    Usage: {% get_user_role_tag request.user as role %}
    """
    return get_user_role(user)
