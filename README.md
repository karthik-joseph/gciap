# Global Construction and Interior Assistance Platform

## Setup Instructions

1. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install django pillow
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## 🔐 Role-Based Access Control (RBAC)

### Overview
The application implements a comprehensive role-based access control system with three user roles:

- **👨‍💼 Admin**: Full system access, manages all users and content
- **👷 Professional**: Can create and manage professional profile, portfolio, and services
- **👤 Customer**: Can browse professionals, book services, and place orders (default role)

### Quick Commands

```bash
# Check a user's role
python manage.py check_role <username>

# Assign a role to a user
python manage.py assign_role <username> <role>
# Examples:
python manage.py assign_role john admin
python manage.py assign_role mary professional
python manage.py assign_role bob customer
```

### RBAC Documentation

📚 **Complete documentation available:**
- **[RBAC Quick Start Guide](RBAC_QUICKSTART.md)** - Get started quickly
- **[RBAC Full Documentation](RBAC_DOCUMENTATION.md)** - Complete reference
- **[RBAC Implementation Summary](RBAC_IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[RBAC Architecture](RBAC_ARCHITECTURE.md)** - Visual diagrams and flow

### Testing RBAC

```bash
# Run the RBAC test script
python test_rbac.py

# Visit the role status page after login
# http://localhost:8088/users/role-status/
```

### Using Roles in Code

#### In Views:
```python
from users.decorators import admin_required, professional_required

@admin_required
def admin_view(request):
    pass

@professional_required
def professional_view(request):
    pass
```

#### In Templates:
```django
{% if is_admin %}
    <a href="/custom-admin/">Admin Panel</a>
{% endif %}

{% if is_professional %}
    <a href="/professionals/dashboard/">Dashboard</a>
{% endif %}
```

## Project Structure

- **users**: User registration, login, profile management, **RBAC system**
- **professionals**: Designer/worker profiles, portfolios, service pricing
- **products**: Product catalog, cart, checkout
- **quotations**: Project quotations and cost estimation
- **bookings**: Booking system and notifications
- **delivery**: Order delivery tracking
- **custom_admin**: Custom admin panel with role-based access

## Features

### User Module
- User registration with budget preference
- Login/logout functionality
- Profile management
- Booking and order history
- **Role-based access control**
- **Role status page**

### Professional Module
- Professional account creation
- Portfolio management with images
- Service pricing by budget level
- Booking management dashboard
- **Role-based dashboard access**

### Product Module
- Global product marketplace
- Budget-based filtering
- Shopping cart
- Checkout and order placement

### Quotation Module
- Create project quotations
- Add quotation items
- Budget estimation
- Quotation comparison

### Booking Module
- Book professional services
- Schedule consultations
- Real-time status updates
- Notifications system

### Delivery Module
- Order tracking
- Delivery status updates
- Tracking timeline

### Error Handling
- Custom 404 page for non-existent URLs
- User-specific navigation:
  - Logged-in users: Navigate to profile or booking history
  - Guest users: Navigate to home page or login
- Helpful links to main sections

## Admin Panels

### Custom Admin Panel (Recommended)

Access at http://127.0.0.1:8000/custom-admin/

**Features:**
- Full CRUD operations for all models
- Dashboard with statistics
- User management (view, delete)
- Professional management (view, edit, delete)
- Product management (create, edit, delete)
- Order management with status updates
- Booking management with status updates
- Quotation management
- Delivery tracking management
- Modern, user-friendly interface
- Comprehensive validations on all forms
- **RBAC-protected (Admin role only)**

**Access Requirements:**
- Admin role (is_staff=True or is_superuser=True)
- Login to admin panel

### Django Default Admin

Access at http://127.0.0.1:8000/django-admin/

Standard Django admin for advanced management.

## URLs

### Public URLs
- Home: /
- Professionals: /professionals/
- Products: /products/

### User URLs
- User Registration: /users/register/
- User Login: /users/login/
- User Profile: /users/profile/
- **Role Status: /users/role-status/** ⭐ NEW
- Booking History: /users/booking-history/

### Professional URLs (Professional Role Required)
- Professional Dashboard: /professionals/dashboard/
- Create Professional: /professionals/create-professional/
- Add Portfolio: /professionals/add-portfolio/
- Add Pricing: /professionals/add-pricing/

### Customer URLs
- Quotations: /quotations/
- Bookings: /bookings/
- Cart: /products/cart/

### Admin URLs (Admin Role Required)
- **Custom Admin: /custom-admin/** 
- **Django Admin: /django-admin/**

## Role-Based Features Summary

| Feature | Admin | Professional | Customer |
|---------|-------|--------------|----------|
| View All Users | ✅ | ❌ | ❌ |
| Manage Products | ✅ | ❌ | ❌ |
| Professional Dashboard | ✅ | ✅ | ❌ |
| Own Profile | ✅ | ✅ | ✅ |
| Browse Products | ✅ | ✅ | ✅ |
| Book Services | ✅ | ✅ | ✅ |
| Admin Panel | ✅ | ❌ | ❌ |

## Development

### Running Tests
```bash
# Test RBAC implementation
python test_rbac.py

# Run Django tests
python manage.py test
```

### Checking User Roles
```bash
# Check role for a specific user
python manage.py check_role <username>

# Assign role to user
python manage.py assign_role <username> <role>
```

## Security

- Role-based access control on all sensitive views
- URL pattern protection via middleware
- Decorator-based view protection
- Template-level UI control
- CSRF protection enabled
- Password validation enabled

## Contributing

When adding new features:
1. Apply appropriate role decorators to views
2. Update templates to show/hide features by role
3. Add permissions to `users/roles.py` if needed
4. Test with different user roles

## Support & Documentation

- **RBAC Quick Start**: See [RBAC_QUICKSTART.md](RBAC_QUICKSTART.md)
- **Full RBAC Docs**: See [RBAC_DOCUMENTATION.md](RBAC_DOCUMENTATION.md)
- **Architecture**: See [RBAC_ARCHITECTURE.md](RBAC_ARCHITECTURE.md)
- **Implementation**: See [RBAC_IMPLEMENTATION_SUMMARY.md](RBAC_IMPLEMENTATION_SUMMARY.md)

