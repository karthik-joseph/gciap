"""
Context processors for making role information available in templates
"""
from .roles import get_user_role, ROLE_ADMIN, ROLE_PROFESSIONAL, ROLE_CUSTOMER


def role_context(request):
    """
    Add role information to template context.
    This makes role checks available in all templates.
    
    Usage in templates:
        {% if user_role == 'admin' %}
        {% if is_admin %}
        {% if is_professional %}
        {% if is_customer %}
    """
    context = {
        'user_role': None,
        'is_admin': False,
        'is_professional': False,
        'is_customer': False,
        'ROLE_ADMIN': ROLE_ADMIN,
        'ROLE_PROFESSIONAL': ROLE_PROFESSIONAL,
        'ROLE_CUSTOMER': ROLE_CUSTOMER,
    }
    
    if request.user.is_authenticated:
        user_role = get_user_role(request.user)
        context.update({
            'user_role': user_role,
            'is_admin': user_role == ROLE_ADMIN,
            'is_professional': user_role == ROLE_PROFESSIONAL,
            'is_customer': user_role == ROLE_CUSTOMER,
        })
    
    return context
