# GCIAP — Full Technical Reference

> Global Construction and Interior Assistance Platform  
> Django 5.x · SQLite (dev) · Whitenoise · Tailwind CDN · Anime.js

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Settings & Configuration](#2-settings--configuration)
3. [Database & Models](#3-database--models)
4. [URL Routing](#4-url-routing)
5. [Role-Based Access Control (RBAC)](#5-role-based-access-control-rbac)
6. [Forms & Validation](#6-forms--validation)
7. [Authentication System](#7-authentication-system)
8. [Custom Admin Panel](#8-custom-admin-panel)
9. [Product & Cart System](#9-product--cart-system)
10. [Professionals System](#10-professionals-system)
11. [Bookings & Quotations](#11-bookings--quotations)
12. [Delivery System](#12-delivery-system)
13. [Template Architecture](#13-template-architecture)
14. [Skeleton Loading System](#14-skeleton-loading-system)
15. [Static Files & Styling](#15-static-files--styling)
16. [Middleware Stack](#16-middleware-stack)
17. [Context Processors](#17-context-processors)
18. [Filters & Search](#18-filters--search)
19. [Key Patterns to Replicate](#19-key-patterns-to-replicate)

---

## 1. Project Structure

```
gciap/                          ← Django project config (settings, urls, wsgi)
users/                          ← Auth, profiles, roles, upgrade requests
professionals/                  ← Professional profiles, portfolios, pricing
products/                       ← Products, cart, orders
quotations/                     ← Quotation requests
bookings/                       ← Service bookings + notifications
delivery/                       ← Delivery tracking
custom_admin/                   ← Fully custom admin panel (NOT django-admin)
templates/
│── base/base.html              ← Main site base template
│── custom_admin/base_admin.html← Admin base template
│── home.html
│── users/                      ← login, register, profile, role_status, etc.
│── professionals/
│── products/
│── quotations/
│── bookings/
│── custom_admin/               ← 30 admin templates (list, detail, modals)
│── 404.html
static/
│── css/base.css                ← Global CSS tokens
│── css/admin.css               ← Admin-specific CSS
│── fonts/                      ← Boa Construktor custom font
│── images/
│── js/
```

---

## 2. Settings & Configuration

**File:** `gciap/settings.py`

### Installed Apps (custom)
```python
INSTALLED_APPS = [
    # ... django builtins ...
    'phonenumber_field',    # Phone number validation
    'custom_admin',
    'users',
    'professionals',
    'products',
    'quotations',
    'bookings',
    'delivery',
]
```

### Middleware Order (important)
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',       # Static files in prod
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.UserRoleContextMiddleware',       # Attaches role to request
    'users.middleware.RoleBasedAccessMiddleware',       # Enforces URL-level RBAC
]
```

### Templates — Custom Context Processor
```python
'context_processors': [
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'users.context_processors.role_context',           # Adds is_admin, is_professional, etc.
],
```

### Static & Media
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Auth Redirects
```python
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
```

### Password Validators (4 built-in)
```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': '...UserAttributeSimilarityValidator'},
    {'NAME': '...MinimumLengthValidator'},
    {'NAME': '...CommonPasswordValidator'},
    {'NAME': '...NumericPasswordValidator'},
]
```

### Locale
```python
LANGUAGE_CODE = 'en-in'
TIME_ZONE = 'Asia/Kolkata'
```

### Production Safety Block (auto-disabled in DEBUG)
```python
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

---

## 3. Database & Models

### Database
- **Development:** SQLite (`db.sqlite3`)
- Engine: `django.db.backends.sqlite3`

---

### `users` App Models

#### `UserProfile` — extends Django's built-in `User`
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField(region='IN')     # django-phonenumber-field
    address = models.TextField(blank=True, null=True)
    budget_preference = models.CharField(choices=['low','medium','high'])
    created_at / updated_at                   # auto timestamps
```

#### `ProfessionalUpgradeRequest` — user requests to become professional
```python
class ProfessionalUpgradeRequest(models.Model):
    user = models.ForeignKey(User, ...)
    professional_type = CharField(choices=[interior_designer, exterior_designer,
                                           architect, worker, contractor])
    bio, experience_years, phone, address, reason
    status = CharField(choices=['pending','approved','rejected'], default='pending')
    admin_notes = TextField(blank=True, null=True)
    # Meta: ordering = ['-created_at']
```

---

### `professionals` App Models

```python
class Professional(models.Model):
    user = models.OneToOneField(User, ...)   # 1-to-1 with Django User
    professional_type, bio, experience_years, phone, address
    is_available = BooleanField(default=True)

class Portfolio(models.Model):
    professional = ForeignKey(Professional, related_name='portfolios')
    title, description
    image = ImageField(upload_to='portfolios/')
    project_date = DateField()

class ServicePricing(models.Model):
    professional = ForeignKey(Professional, related_name='pricings')
    service_name
    budget_level = CharField(choices=['low','medium','high'])
    price = DecimalField(max_digits=10, decimal_places=2)
    description
```

---

### `products` App Models

```python
class Product(models.Model):
    category = CharField(choices=['furniture','decor','construction_material'])
    budget_level = CharField(choices=['low','medium','high'])
    name, description
    price = DecimalField(max_digits=10, decimal_places=2)
    image = ImageField(upload_to='products/')
    stock_quantity, supplier_country, shipping_cost, delivery_days

class Cart(models.Model):
    user = ForeignKey(User, related_name='carts')
    def get_total()  # sums CartItem subtotals

class CartItem(models.Model):
    cart = ForeignKey(Cart, related_name='items')
    product = ForeignKey(Product)
    quantity
    def get_subtotal()

class Order(models.Model):
    status = CharField(choices=['pending','confirmed','shipped','delivered','cancelled'])
    user, total_amount, shipping_address

class OrderItem(models.Model):
    order = ForeignKey(Order, related_name='items')
    product, quantity, price   # price snapshot at order time
```

---

### `bookings` App Models
- Booking of professionals by customers
- Notification system for booking updates

### `quotations` App Models
- Quotation requests between customers and professionals

### `delivery` App Models
- Delivery tracking linked to orders (tracking events)

---

## 4. URL Routing

### Root `gciap/urls.py`
```python
urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('custom-admin/', include('custom_admin.urls')),
    path('users/',        include('users.urls')),
    path('professionals/',include('professionals.urls')),
    path('products/',     include('products.urls')),
    path('quotations/',   include('quotations.urls')),
    path('bookings/',     include('bookings.urls')),
    path('delivery/',     include('delivery.urls')),
    path('',              views.home, name='home'),
]
```

### `users/urls.py` (app_name = 'users')
| URL | Name | Purpose |
|-----|------|---------|
| `register/` | `register` | User registration |
| `check-username/` | `check_username` | AJAX username availability |
| `login/` | `login` | Login page |
| `logout/` | `logout` | Logout |
| `profile/` | `profile` | View/edit own profile |
| `booking-history/` | `booking_history` | User's order/booking history |
| `role-status/` | `role_status` | Show current role & permissions |
| `request-upgrade/` | `request_upgrade` | Submit upgrade to professional |
| `upgrade-status/` | `upgrade_status` | Check request status |

### `custom_admin/urls.py` (app_name = 'custom_admin')
| URL Pattern | Name | Purpose |
|-------------|------|---------|
| `''` | `dashboard` | Admin home |
| `users/` | `user_list` | List all users |
| `users/<pk>/` | `user_detail` | User details |
| `users/<pk>/edit/` | `user_edit` | Edit user (modal) |
| `users/<pk>/delete/` | `user_delete` | Delete user (modal) |
| `users/<pk>/delete-ajax/` | `user_delete_ajax` | AJAX delete |
| `users/<pk>/convert-to-professional/` | `convert_to_professional` | Promote user |
| `upgrade-requests/` | `upgrade_request_list` | List upgrade requests |
| `upgrade-requests/<pk>/` | `upgrade_request_detail` | Detail view |
| `upgrade-requests/<pk>/approve/` | `upgrade_request_approve` | Approve (modal) |
| `upgrade-requests/<pk>/reject/` | `upgrade_request_reject` | Reject (modal) |
| `professionals/<pk>/edit/` | `professional_edit` | Edit professional |
| `products/create/` | `product_create` | Create product (modal) |
| `products/<pk>/edit/` | `product_edit` | Edit product (modal) |
| `orders/<pk>/update-status/` | `order_update_status` | Change order status |
| `bookings/<pk>/update-status/` | `booking_update_status` | Change booking status |
| `delivery/create/<order_id>/` | `delivery_create` | Create delivery |
| `delivery/<pk>/add-tracking/` | `delivery_add_tracking` | Log tracking event |

---

## 5. Role-Based Access Control (RBAC)

### Three Roles
```python
# users/roles.py
ROLE_ADMIN        = 'admin'        # is_superuser or is_staff
ROLE_PROFESSIONAL = 'professional' # has a Professional profile linked to User
ROLE_CUSTOMER     = 'customer'     # default for all authenticated users
```

### Role Detection (`get_user_role`)
```python
def get_user_role(user):
    if user.is_superuser or user.is_staff:
        return ROLE_ADMIN
    if hasattr(user, 'professional'):   # checks OneToOne reverse relation
        return ROLE_PROFESSIONAL
    return ROLE_CUSTOMER
```

### Role Permissions Dictionary
Each role has a list of named permissions (e.g. `'manage_users'`, `'create_bookings'`).  
Check with `has_permission(user, 'permission_name')`.

### Three Protection Layers

#### Layer 1 — URL Middleware (`RoleBasedAccessMiddleware`)
Blocks whole URL prefixes at the middleware level, before the view even runs:
```python
self.protected_patterns = {
    '/admin/':                         [ROLE_ADMIN],
    '/custom-admin/':                  [ROLE_ADMIN],
    '/professionals/dashboard/':       [ROLE_PROFESSIONAL, ROLE_ADMIN],
    '/professionals/create-professional/': [ROLE_CUSTOMER, ROLE_ADMIN],
}
```

#### Layer 2 — View Decorators
```python
# users/decorators.py
@admin_required                          # only admin
@professional_required                   # only professional
@customer_required                       # only customer
@admin_or_professional_required          # either
@role_required('admin', 'professional')  # generic multi-role
@login_required                          # built-in
```

#### Layer 3 — Template Conditionals
Variables available in every template via context processor:
```html
{% if is_admin %} ... {% endif %}
{% if is_professional %} ... {% endif %}
{% if user_role == 'admin' %} ... {% endif %}
```

---

## 6. Forms & Validation

### `UserRegistrationForm` (extends `UserCreationForm`)
Fields: `username, first_name, last_name, email, password1, password2, phone, address, budget_preference`

**Custom clean methods:**
```python
def clean_username(self):
    # Min 3 chars
    # Regex: must start with letter/underscore, only letters/numbers/underscores
    # Uniqueness check against DB

def clean_password2(self):
    # Ensures password1 == password2
    # Raises ValidationError("Passwords don't match") if not

def clean_phone(self):
    # PhoneNumberField with region='IN' handles format validation
    # Raises error if empty
```

**Optional fields:** `address`, `last_name` — set `required=False`

**Phone field:** uses `phonenumber_field.formfields.PhoneNumberField` (installed library)

### `ProfessionalUpgradeRequestForm`
Fields: `professional_type, bio, experience_years, phone, address, reason`
```python
def clean_experience_years(self):
    # Cannot be negative
```

### `AdminUserEditForm`
Fields: `username, first_name, last_name, email, is_active` — for admin-only user editing.

### AJAX Username Check
`GET /users/check-username/?username=foo` → JSON `{ "available": true/false }`  
Used in registration form for real-time feedback.

---

## 7. Authentication System

### Login
- Uses Django's built-in `authenticate()` + `login()`
- Redirects to `LOGIN_REDIRECT_URL = '/'`

### Logout
- Uses Django's `logout()`
- Redirects to home

### Registration Flow
1. `UserCreationForm` creates the `auth.User`
2. `UserProfile` is created with `OneToOneField` → phone, address, budget
3. Auto-login after registration

### Password Validation (4 built-in validators active)
1. **UserAttributeSimilarity** — password can't be too similar to username/email
2. **MinimumLength** — default 8 characters
3. **CommonPassword** — rejects common passwords
4. **NumericPassword** — can't be all numbers

---

## 8. Custom Admin Panel

### Location
`/custom-admin/` — completely separate from Django's `/django-admin/`.  
**Protected by:** `@admin_required` decorator on every view + `RoleBasedAccessMiddleware`.

### Base Template: `templates/custom_admin/base_admin.html`
- Fixed **sidebar** with nav links (Dashboard, Users, Professionals, Products, Orders, Bookings, Upgrade Requests, Django Admin link)
- **Header bar** showing logged-in username + role badge
- **Global Modal Shell** — single animated modal used across all admin actions

### Global Modal Pattern
Every edit/delete/approve/reject action uses the **same modal overlay** in `base_admin.html`.  
Child templates inject content via template blocks:

```html
<!-- In child template -->
{% block body_data %}data-use-modal="true"{% endblock %}
{% block modal_title %}Edit User{% endblock %}
{% block modal_cancel_url %}{% url 'custom_admin:user_list' %}{% endblock %}
{% block modal_content %}
    <form method="post">{% csrf_token %}{{ form.as_p }}<button>Save</button></form>
{% endblock %}
```

The `data-use-modal="true"` on `<body>` triggers the modal to open automatically on page load.  
**Animations** (open/close/escape key) are handled in `base_admin.html` via Anime.js.

### Admin Dashboard Views
- **Stats cards** — user count, professional count, product count, booking count
- **Recent activity** — latest orders, latest bookings

### Admin CRUD Pattern (example: Users)
```
/custom-admin/users/         → list (search + filter)
/custom-admin/users/<pk>/    → detail
/custom-admin/users/<pk>/edit/   → edit (modal form)
/custom-admin/users/<pk>/delete/ → delete confirmation (modal)
```
All forms open in the shared animated modal.

### Upgrade Request Workflow
1. User submits form at `/users/request-upgrade/`
2. Admin sees list at `/custom-admin/upgrade-requests/`
3. Admin opens detail, clicks Approve or Reject → modal form
4. On approve: `Professional` record is created, `is_staff` NOT set — role comes from `hasattr(user, 'professional')`
5. On reject: status updated, optional admin notes saved

---

## 9. Product & Cart System

### Product Filters (List Page)
- Filter by **category**: `furniture`, `decor`, `construction_material`
- Filter by **budget_level**: `low`, `medium`, `high`
- Combined filters work together via `Q` objects or chained `.filter()`
- **Dynamic empty state messages:** "No [category] products found in [budget] budget" or generic message

### Cart Flow
1. `Add to Cart` → creates/gets user's `Cart`, creates/updates `CartItem`
2. Cart view shows items, quantities, subtotals, total
3. Checkout → creates `Order` + `OrderItem` records (price snapshot at buy time)

### Order Status Lifecycle
```
pending → confirmed → shipped → delivered
                             → cancelled
```

---

## 10. Professionals System

### Public List (`/professionals/`)
- Browse all professionals
- Filter by `professional_type`
- Each card shows: photo, type, bio, experience, availability badge

### Professional Dashboard (`/professionals/dashboard/`)
- **Protected:** `@professional_required` + middleware
- Manage own profile, portfolio entries, service pricing

### Portfolio
- Image upload to `portfolios/` media folder
- Title, description, project date per entry

### Service Pricing
- Per service name, with budget level and price
- Multiple pricing entries per professional

---

## 11. Bookings & Quotations

### Bookings
- Customer books a professional for a service
- Status tracking on the booking
- **Notifications system** (`/bookings/notifications/`) — all booking updates are logged as notifications for the user

### Quotations
- Customer requests a quote from a professional
- Professional can respond with a price

---

## 12. Delivery System

### Models
- `Delivery` — linked to an `Order`, contains carrier, tracking number, estimated date
- `TrackingEvent` — log entries (date, location, description)

### Admin Actions
- Create delivery for an order
- Add tracking events to an existing delivery

---

## 13. Template Architecture

### Main Site: `templates/base/base.html`
**Includes:**
- Tailwind CSS (CDN) with custom config (extended colors, animations, keyframes)
- Google Fonts (Inter)
- Anime.js (CDN)
- Custom font: **Boa Construktor** (TTF loaded via `@font-face`)
- Custom CSS: `base.css`

**Navbar features:**
- Fixed top navbar with glassmorphism effect (`.navbar-blur`)
- Shows different nav items based on `{% if is_admin %}`, `{% if is_professional %}`
- Role badge displayed in nav (colour-coded: red=admin, amber=professional, blue=customer)
- Mobile hamburger menu (toggle via JS)
- Scroll effect: navbar background changes on scroll

**Messages system:**
- Django messages rendered as toast notifications (top-right, fixed)
- Slide-in via Anime.js, auto-dismiss after 5 seconds

**Animations:**
- IntersectionObserver for scroll-triggered fade-in on `section`, `.glass-panel`, `.card-shine`
- Stagger animation for grid children
- Mouse parallax on background blobs (`.blur-3xl`)

**Footer:**
- Quick links, account links, copyright

### Admin Site: `templates/custom_admin/base_admin.html`
- Fixed sidebar + scrollable main content
- Sticky header
- Global modal shell (described in §8)
- Page-bar progress indicator (purple top bar on load)
- Skeleton engine (same as main site, without offline banner)

---

## 14. Skeleton Loading System

**Implemented in:** `base.html` and `base_admin.html`

### How It Works
1. A **purple page-bar** (`#sk-page-bar`) runs across the top of the page on every load
2. On `DOMContentLoaded`, all `.sk-section` elements are auto-resolved (550ms delay)
3. Resolving a section:
   - Hides `.sk-placeholder` (the shimmer skeleton)
   - Shows `.sk-content` (actual content) with fade-in
   - OR shows `.sk-empty` if there are `[data-sk-item]` elements but count = 0

### HTML Structure for Skeleton
```html
<div class="sk-section" id="my-section">
    <!-- Shown while loading -->
    <div class="sk-placeholder">
        <div class="sk-shimmer"></div>
    </div>
    <!-- Shown after load — with data-sk-item on each item -->
    <div class="sk-content grid">
        {% for item in items %}
        <div data-sk-item>{{ item.name }}</div>
        {% endfor %}
    </div>
    <!-- Shown if items list is empty -->
    <div class="sk-empty">No items found.</div>
</div>
```

### JavaScript API (`window.GCIAPSkeleton`)
```javascript
window.GCIAPSkeleton.resolve('section-id')   // resolve one section
window.GCIAPSkeleton.error('section-id', 'Error message')  // show error state
window.GCIAPSkeleton.autoResolve(550)        // resolve all after delay
window.GCIAPSkeleton.finishBar()             // complete the page bar
```

### CSS Classes
| Class | Purpose |
|-------|---------|
| `sk-section` | Wrapper element |
| `sk-placeholder` | Skeleton shimmer shown before content |
| `sk-content` | Real content (hidden until resolved) |
| `sk-empty` | Empty state (shown when no items) |
| `sk-visible` | Added on content after reveal |
| `sk-shimmer` | Animated gradient shimmer |
| `sk-page-bar` | Purple top progress bar |

---

## 15. Static Files & Styling

### CSS Files
- `static/css/base.css` — global tokens: `.glass`, `.glass-panel`, `.gradient-primary`, `.text-gradient`, `.gradient-text`, `.sk-*` skeleton styles, `#sk-page-bar`
- `static/css/admin.css` — admin sidebar active states, `.admin-nav-link`

### Custom Font
```css
@font-face {
    font-family: 'Boa Construktor';
    src: url('/static/fonts/boa-construktor-font/BoaConstruktorBold-zrjL4.ttf') format('truetype');
    font-weight: bold;
}
/* Usage in Tailwind: class="font-boa" */
```

### Tailwind Custom Config (in-template)
```javascript
tailwind.config = {
    theme: {
        extend: {
            fontFamily: { 'boa': ['Boa Construktor'], 'primary': ['Inter'] },
            colors: {
                primary: { 50→900: sky blue scale },
                accent: { DEFAULT: '#8b5cf6', light, dark },
                dark: { 100: '#1e293b', 200: '#0f172a', 300: '#020617' }
            },
            animation: { 'fade-in', 'slide-up', 'float' },
            keyframes: { fadeIn, slideUp, float }
        }
    }
}
```

### Glassmorphism Classes
```css
.glass       { background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); }
.glass-panel { background: rgba(15,23,42,0.6);     backdrop-filter: blur(10px); }
.glass-dark  { background: rgba(15,23,42,0.8);     backdrop-filter: blur(10px); }
```

---

## 16. Middleware Stack

### `UserRoleContextMiddleware`
Runs on every request. Attaches to the request object:
```python
request.user_role       # 'admin' | 'professional' | 'customer' | None
request.is_admin        # bool
request.is_professional # bool
request.is_customer     # bool
```

### `RoleBasedAccessMiddleware`
Checks URL prefixes against `protected_patterns`. If the logged-in user's role is NOT in the allowed list → `redirect('home')` with an error message.

### `WhiteNoiseMiddleware`
Must be placed **second** (right after `SecurityMiddleware`) to serve static files efficiently in production without a separate web server.

---

## 17. Context Processors

### `users.context_processors.role_context`
Makes these variables available in **every template automatically**:
```python
{
    'user_role': 'admin' | 'professional' | 'customer' | None,
    'is_admin': True/False,
    'is_professional': True/False,
    'is_customer': True/False,
    'ROLE_ADMIN': 'admin',
    'ROLE_PROFESSIONAL': 'professional',
    'ROLE_CUSTOMER': 'customer',
}
```
Registered in `settings.py` → `TEMPLATES[0]['OPTIONS']['context_processors']`.

---

## 18. Filters & Search

### Products (`/products/`)
- `?category=furniture` — filter by category choice
- `?budget=low` — filter by budget level
- Both combined: `?category=furniture&budget=low`
- Empty state message is dynamic: includes the active filter labels

### Professionals (`/professionals/`)
- Filter by professional type
- Search by name/bio via `icontains` lookups

### Admin Lists
- Most admin list views support search via `GET` parameter
- Search done with `Q` objects for multi-field search:
  ```python
  from django.db.models import Q
  qs.filter(Q(username__icontains=q) | Q(email__icontains=q))
  ```

---

## 19. Key Patterns to Replicate

### ✅ New App Checklist
```bash
python manage.py startapp myapp
```
1. Add `'myapp'` to `INSTALLED_APPS`
2. Create `myapp/models.py` with models
3. Create `myapp/forms.py`
4. Create `myapp/views.py` with `@login_required` / `@admin_required` as needed
5. Create `myapp/urls.py` with `app_name = 'myapp'`
6. Include in `gciap/urls.py`: `path('myapp/', include('myapp.urls'))`
7. Create `templates/myapp/` folder with HTML files
8. Run `python manage.py makemigrations && python manage.py migrate`

### ✅ Protect a View
```python
from users.decorators import admin_required, professional_required

@admin_required
def my_admin_view(request): ...

@professional_required
def my_pro_view(request): ...
```

### ✅ Check Role in Template
```html
{% if is_admin %}
    <a href="{% url 'custom_admin:dashboard' %}">Admin Panel</a>
{% endif %}
```

### ✅ Admin Modal Form (edit/delete)
In child template:
```html
{% extends 'custom_admin/base_admin.html' %}
{% block body_data %}data-use-modal="true"{% endblock %}
{% block modal_title %}Edit Something{% endblock %}
{% block modal_cancel_url %}{% url 'custom_admin:list_view' %}{% endblock %}
{% block modal_content %}
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}
        <div style="display:flex;justify-content:flex-end;gap:1rem;margin-top:1.5rem;">
            <a href="{% url 'custom_admin:list_view' %}" class="btn-cancel">Cancel</a>
            <button type="submit" class="btn-primary">Save</button>
        </div>
    </form>
{% endblock %}
```

### ✅ Skeleton Section
```html
<div class="sk-section" id="products-section">
    <div class="sk-placeholder">
        <!-- shimmer rows go here -->
        <div class="sk-shimmer" style="height:80px;border-radius:12px;margin-bottom:1rem;"></div>
    </div>
    <div class="sk-content grid grid-cols-3 gap-6">
        {% for product in products %}
        <div data-sk-item class="card-shine glass-panel rounded-2xl p-4">
            {{ product.name }}
        </div>
        {% endfor %}
    </div>
    <div class="sk-empty flex-col items-center justify-center py-20">
        <p class="sk-empty-text text-slate-400">No products found.</p>
    </div>
</div>
```

### ✅ Role-Based URL Middleware
In `users/middleware.py`, add to `self.protected_patterns`:
```python
'/my-new-section/': [ROLE_ADMIN],
```

### ✅ Custom Form Validation
```python
class MyForm(forms.ModelForm):
    def clean_fieldname(self):
        value = self.cleaned_data.get('fieldname')
        if not some_condition(value):
            raise forms.ValidationError("Human-readable error message")
        return value
```

### ✅ Phone Number Field
```python
# models.py
from phonenumber_field.modelfields import PhoneNumberField
phone = PhoneNumberField(region='IN')

# forms.py
from phonenumber_field.formfields import PhoneNumberField
phone = PhoneNumberField(region='IN', widget=forms.TextInput(attrs={...}))
```

### ✅ Image Upload
```python
# Model
image = models.ImageField(upload_to='folder_name/')

# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# gciap/urls.py (dev only)
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Form tag
<form enctype="multipart/form-data">
```

---

## 20. Dependencies (`requirements.txt`)

| Package | Purpose |
|---------|---------|
| `Django>=5.0,<6.0` | Web framework |
| `Pillow>=10.0` | Image processing (ImageField) |
| `python-dotenv>=1.0` | Load `.env` variables |
| `psycopg2-binary>=2.9` | PostgreSQL driver (kept, not used in dev) |
| `dj-database-url>=2.0` | Parse DATABASE_URL (kept, not used in dev) |
| `gunicorn>=21.0` | Production WSGI server |
| `whitenoise>=6.0` | Static file serving in production |
| `django-phonenumber-field` | Phone number model/form field |

---

*Generated: 2026-02-23 | Project: GCIAP*
