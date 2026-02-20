"""
Role-based access control constants and utilities
"""

# Role constants
ROLE_ADMIN = 'admin'
ROLE_PROFESSIONAL = 'professional'
ROLE_CUSTOMER = 'customer'

ROLE_CHOICES = [
    (ROLE_ADMIN, 'Administrator'),
    (ROLE_PROFESSIONAL, 'Professional'),
    (ROLE_CUSTOMER, 'Customer'),
]

# Permission groups by role
ROLE_PERMISSIONS = {
    ROLE_ADMIN: [
        'view_all_users',
        'manage_users',
        'view_all_professionals',
        'manage_professionals',
        'view_all_products',
        'manage_products',
        'view_all_orders',
        'manage_orders',
        'view_all_bookings',
        'manage_bookings',
        'view_all_quotations',
        'manage_quotations',
        'view_all_deliveries',
        'manage_deliveries',
        'manage_system_settings',
    ],
    ROLE_PROFESSIONAL: [
        'view_own_profile',
        'manage_own_profile',
        'view_own_bookings',
        'manage_own_bookings',
        'view_own_portfolio',
        'manage_own_portfolio',
        'view_own_pricing',
        'manage_own_pricing',
    ],
    ROLE_CUSTOMER: [
        'view_own_profile',
        'manage_own_profile',
        'view_products',
        'manage_own_cart',
        'view_own_orders',
        'create_orders',
        'view_own_bookings',
        'create_bookings',
        'view_own_quotations',
        'create_quotations',
    ],
}


def get_user_role(user):
    """
    Get the role of a user
    """
    if not user or not user.is_authenticated:
        return None
    
    # Check if user is superuser or staff (admin)
    if user.is_superuser or user.is_staff:
        return ROLE_ADMIN
    
    # Check if user has a professional profile
    if hasattr(user, 'professional'):
        return ROLE_PROFESSIONAL
    
    # Default role is customer
    return ROLE_CUSTOMER


def has_permission(user, permission):
    """
    Check if a user has a specific permission based on their role
    """
    role = get_user_role(user)
    if not role:
        return False
    
    return permission in ROLE_PERMISSIONS.get(role, [])


def is_admin(user):
    """Check if user is an admin"""
    return get_user_role(user) == ROLE_ADMIN


def is_professional(user):
    """Check if user is a professional"""
    return get_user_role(user) == ROLE_PROFESSIONAL


def is_customer(user):
    """Check if user is a customer"""
    return get_user_role(user) == ROLE_CUSTOMER
