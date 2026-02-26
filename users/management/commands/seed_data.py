"""
Django management command to seed the database with dummy data.
Usage:
  python manage.py seed_data
  python manage.py seed_data --flush   (clears existing data first)

This command creates:
  - Users (customers + professionals)
  - UserProfiles
  - Professionals with portfolio items and service pricing
  - Products (furniture, decor, construction materials) with images
  - Bookings and Notifications
  - Quotations with items
  - Orders with delivery tracking
"""

import os
import shutil
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings

from users.models import UserProfile, ProfessionalUpgradeRequest
from professionals.models import Professional, Portfolio, ServicePricing
from products.models import Product, Order, OrderItem
from bookings.models import Booking, Notification
from quotations.models import Quotation, QuotationItem
from delivery.models import Delivery, DeliveryTracking


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

STATIC_PRODUCT_DIR = os.path.join(settings.BASE_DIR, 'static', 'images', 'product')
STATIC_PORTFOLIO_DIR = os.path.join(settings.BASE_DIR, 'static', 'images', 'product')  # portfolio images stored here too
MEDIA_PRODUCTS_DIR  = os.path.join(settings.MEDIA_ROOT, 'products')
MEDIA_PORTFOLIOS_DIR = os.path.join(settings.MEDIA_ROOT, 'portfolios')


def copy_image(src_filename, dest_dir, dest_filename=None):
    """
    Copy an image from static/images/product/ into the media subdirectory.
    Returns the relative media path (e.g. 'products/sofa.jpg') or '' on failure.
    """
    if dest_filename is None:
        dest_filename = src_filename

    src  = os.path.join(STATIC_PRODUCT_DIR, src_filename)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, dest_filename)

    if not os.path.exists(src):
        return ''
    if not os.path.exists(dest):
        shutil.copy2(src, dest)
    # Return path relative to MEDIA_ROOT
    return os.path.relpath(dest, settings.MEDIA_ROOT).replace('\\', '/')


# ─────────────────────────────────────────────
#  Data definitions
# ─────────────────────────────────────────────

USERS_DATA = [
    # (username, email, first_name, last_name, password, is_staff, is_superuser, phone, address, budget)
    ('rajesh_k',  'rajesh@example.com',  'Rajesh',  'Kumar',    'Pass@1234', False, False, '+919876543210', '12, MG Road, Bangalore, Karnataka', 'medium'),
    ('priya_m',   'priya@example.com',   'Priya',   'Menon',    'Pass@1234', False, False, '+919812345670', '45, Marine Drive, Kochi, Kerala',   'high'),
    ('arjun_d',   'arjun@example.com',   'Arjun',   'Das',      'Pass@1234', False, False, '+919823456781', '8, Linking Road, Mumbai, Maharashtra','high'),
    ('meena_s',   'meena@example.com',   'Meena',   'Sharma',   'Pass@1234', False, False, '+919834567892', '23, Anna Salai, Chennai, Tamil Nadu', 'high'),
    ('vijay_r',   'vijay@example.com',   'Vijay',   'Reddy',    'Pass@1234', False, False, '+919845678903', '67, Jubilee Hills, Hyderabad, Telangana','medium'),
    ('anita_b',   'anita@example.com',   'Anita',   'Bose',     'Pass@1234', False, False, '+919856789014', '11, Park Street, Kolkata, West Bengal', 'medium'),
    ('suresh_p',  'suresh@example.com',  'Suresh',  'Pillai',   'Pass@1234', False, False, '+919867890125', '34, Brigade Road, Bangalore, Karnataka','low'),
]

PROFESSIONALS_DATA = [
    # (username, type, bio, experience_years, phone, address)
    ('arjun_d', 'interior_designer', 8, '+919823456781', '8, Linking Road, Mumbai, Maharashtra',
     'Award-winning interior designer specialising in modern minimalist and luxury residential spaces. '
     'Worked on 200+ projects across Mumbai, Pune and Bangalore. Expert in space planning, '
     'material selection and 3D visualisation.'),
    ('meena_s', 'architect', 12, '+919834567892', '23, Anna Salai, Chennai, Tamil Nadu',
     'Licensed architect with expertise in sustainable building design and urban planning. '
     'Designed residential villas, commercial complexes and eco-friendly community spaces. '
     'LEED-certified and a published author on green architecture.'),
    ('vijay_r', 'contractor', 15, '+919845678903', '67, Jubilee Hills, Hyderabad, Telangana',
     'Experienced general contractor handling residential and commercial projects across South India. '
     'Speciali in high-quality construction, renovation, and fit-out work delivered on time and budget.'),
    ('anita_b', 'exterior_designer', 6, '+919856789014', '11, Park Street, Kolkata, West Bengal',
     'Creative exterior designer focused on landscape architecture, façade design, and outdoor living spaces. '
     'Delivered award-winning gardens, terraces, and building exteriors across eastern India.'),
]

# (professional_username, service_name, budget_level, price, description)
PRICING_DATA = [
    ('arjun_d', 'Living Room Design',     'low',    15000.00, 'Basic living room redesign with mood board, colour palette and furniture layout plan.'),
    ('arjun_d', 'Living Room Design',     'medium', 35000.00, 'Complete living room design with custom furniture sourcing, lighting plan and 3D renders.'),
    ('arjun_d', 'Living Room Design',     'high',   75000.00, 'Premium luxury living room design with bespoke furniture, imported finishes and project management.'),
    ('arjun_d', 'Full Home Interior',     'medium', 150000.00,'End-to-end interior design for a 3BHK apartment including all rooms, kitchen and bathrooms.'),
    ('arjun_d', 'Bedroom Design',         'low',    12000.00, 'Bedroom layout, colour scheme, furniture and lighting plan.'),
    ('meena_s', 'House Plan – 2BHK',      'low',    25000.00, 'Architectural plan, elevation and section drawings for a 2BHK house up to 1200 sq ft.'),
    ('meena_s', 'House Plan – 2BHK',      'medium', 50000.00, 'Full architectural drawings, structural layout, electrical and plumbing plans for 2BHK.'),
    ('meena_s', 'House Plan – 3BHK',      'high',   120000.00,'Complete architectural package for a 3BHK villa including 3D renders and BOQ.'),
    ('meena_s', 'Commercial Design',      'high',   500000.00,'Full architectural design for commercial spaces up to 10,000 sq ft.'),
    ('vijay_r', 'Single Floor Construction','low',  500000.00,'Solid construction for a single-floor house up to 1000 sq ft using standard materials.'),
    ('vijay_r', 'Single Floor Construction','medium',900000.00,'Premium single-floor construction with branded materials, tiling and painting.'),
    ('vijay_r', 'Renovation Work',        'low',    100000.00,'Complete renovation of a 2BHK apartment – flooring, painting and fixture replacement.'),
    ('vijay_r', 'Renovation Work',        'medium', 250000.00,'Full renovation with modular kitchen, premium bath fittings and designer flooring.'),
    ('anita_b', 'Garden Design',          'low',    20000.00, 'Landscape plan with plant selection and basic hardscape recommendations.'),
    ('anita_b', 'Garden Design',          'medium', 55000.00, 'Complete garden design with irrigation plan, hardscape, lighting and plant sourcing.'),
    ('anita_b', 'Full Exterior Makeover', 'high',   200000.00,'End-to-end exterior redesign including façade, garden, driveway and outdoor lighting.'),
]

# (professional_username, title, description, image_filename, project_date)
PORTFOLIO_DATA = [
    ('arjun_d', 'Modern Minimalist Living Room', 'Living room makeover.png', date(2024, 8, 15),
     'A sleek, contemporary living space featuring clean lines, neutral tones, custom furniture and layered ambient lighting.'),
    ('arjun_d', 'Luxury Bedroom Suite', 'bedroom design.png', date(2024, 3, 20),
     'Premium bedroom design with custom lighting, imported wood finishes and integrated smart home controls.'),
    ('arjun_d', 'Modern Kitchen Remodel', 'kitchen remodel.png', date(2023, 11, 10),
     'A fully modular kitchen with quartz countertops, concealed lighting and German-brand hardware.'),
    ('meena_s', 'Eco-Friendly Villa, Coimbatore', 'completed building house.png', date(2024, 6, 1),
     '3000 sq ft sustainable villa featuring rainwater harvesting, solar panels and natural cross-ventilation.'),
    ('meena_s', 'Commercial Office Blueprint', 'Building blueprint image.png', date(2023, 9, 14),
     'Detailed architectural blueprint for a 5-floor commercial office complex with open-plan offices and green terraces.'),
    ('meena_s', '3D Villa Render – Kochi', '3D house model image.png', date(2024, 1, 22),
     'Photo-realistic 3D render of a luxury waterfront villa designed for a private client in Kochi.'),
    ('vijay_r', '2BHK Apartment Renovation', 'construction site image.png', date(2024, 5, 5),
     'Complete renovation of a 1200 sq ft apartment including kitchen remodel, bathroom upgrade and luxury flooring.'),
    ('anita_b', 'Tropical Garden Retreat', 'garden design trivandrum.png', date(2024, 7, 30),
     'A lush tropical garden design with a pergola, koi pond, stone pathways and curated plant palette.'),
    ('anita_b', 'Modern House Façade', 'House façade.png', date(2024, 4, 18),
     'Complete exterior makeover featuring textured cladding, LED façade lighting and a minimalist entrance canopy.'),
    ('anita_b', 'Patio & Deck Design', 'patiodeck.png', date(2023, 12, 5),
     'Outdoor deck and patio design with composite decking, planters and weather-resistant furniture layout.'),
]

# (name, category, budget_level, price, stock, supplier_country, shipping_cost, delivery_days, image_filename, description)
PRODUCTS_DATA = [
    # ── Furniture ──────────────────────────────────────────────────────────────
    ('Scandinavian Wood Sofa',        'furniture', 'medium', 45000.00, 15, 'Sweden',  2500.00, 21,
     'scandinavian_wood_sofa.png',
     'Clean-lined three-seater sofa with solid beech wood legs and premium grey fabric upholstery. Perfect for contemporary living rooms.'),


    ('Curved Off-White Luxury Sofa',  'furniture', 'high',   125000.00, 5, 'Italy',   5000.00, 30,
     'curved_off_white_luxury_sofa.webp',
     'Statement curved sofa in cloud-white boucle fabric with gold-tone legs. A centrepiece for any luxury interior.'),


    ('Modern Office Chair',           'furniture', 'low',    8500.00,  50, 'India',    300.00,  5,
     'modern_office_chair.png',
     'Ergonomic mesh office chair with adjustable lumbar support, armrests and seat height. Built for all-day comfort.'),


    ('Italian Leather Recliner',      'furniture', 'high',   125000.00, 4, 'Italy',   5000.00, 30,
     'italian_leather_recliner.png',
     'Full-grain Italian leather recliner with power-reclining mechanism and USB charging port. Timeless luxury.'),


    ('Bamboo Dining Table (4-Seater)','furniture', 'medium', 28000.00, 12, 'Vietnam', 2000.00, 18,
     'bamboo_dining_table.png',
     'Sustainably sourced bamboo dining table with a honey-finish and matching upholstered chairs.'),


    ('Adana Sheesham 6-Seater Dining','furniture', 'medium', 42000.00,  8, 'India',   1500.00, 10,
     'adana_grand_sheesham_wood_6-seater_dining_table.jpg',
     'Solid sheesham wood 6-seater dining set with a natural grain finish and cushioned chairs.'),


    ('Aphamex 10-Seater Dining Set',  'furniture', 'high',   185000.00, 3, 'India',   4000.00, 21,
     'aphamex_10_seater_dining.webp',
     'Grand 10-seater dining table crafted from premium mango wood with a semi-gloss lacquer finish.'),


    ('Hiro Marble & Wood Dining Set', 'furniture', 'high',   220000.00, 2, 'Italy',   6000.00, 28,
     'buy-dining-furniture-set-hiro-wooden-and-marble-finish-modern-designed-6-seater-dining-table-for-dining-room-by-orange-tree-on-ikiru-online-store-1.webp',
     'Designer 6-seater dining table with an Italian marble top and walnut wood base. A true statement piece.'),


    ('Acacia Open Bookcase Shelf',    'furniture', 'low',    12500.00, 25, 'India',    500.00,  7,
     'Acacia Wood Open BookCase book shelf.webp',
     'Five-shelf open bookcase in acacia wood with natural cane rattan inserts. Suits both home offices and living rooms.'),


    ('Blue Velvet Chesterfield Sofa', 'furniture', 'high',    95000.00,  6,'UK',      4500.00, 25,
     'Blue-Velvet-Chesterfield-Sofa_18.jpg',
     'Classic Chesterfield sofa reinterpreted in rich royal-blue velvet with deep button tufting and polished brass feet.'),


    # ── Decor ──────────────────────────────────────────────────────────────────
    ('Buddha Premium Wall Painting',  'decor', 'medium', 8500.00, 30, 'India',    400.00, 6,
     'Artsense Buddha Premium Wall Painting for Home & Office – Spiritual Wall Art with Golden Premium Floating Frame – 24x36 inches (61x91 cm).jpg',
     '24×36 inch premium canvas print in a golden floating frame. A calming spiritual accent for any room.'),


    ('Moksha Ceramic Waves Vase',     'decor', 'medium', 4200.00, 40, 'India',    200.00, 4,
     'Moksha Ceramic Waves Vase.jpg',
     'Hand-thrown ceramic vase with organic wave texture in matte sage green. Each piece is one of a kind.'),


    ('Kintsugi Marble Crack Wall Art','decor', 'high',   22000.00,  8, 'Japan',   2000.00, 20,
     'Kintsugi Style Marble Crack Peel.jpg',
     'Inspired by the Japanese art of Kintsugi — fractured marble panel with real 24K gold fault lines. A collector piece.'),


    ('Decorative Ribbed Flower Vase', 'decor', 'low',    1800.00, 80, 'India',    150.00,  3,
     'Vase for Flowers Decorative Ribbed Blue Green Plastic Flower Vase.jpg',
     'Set of two ribbed cylindrical vases in ocean blue-green. Lightweight, modern and versatile.'),


    ('Radiant Flower Vase Set of 2',  'decor', 'low',    2400.00, 60, 'India',    150.00,  3,
     'Radiant Decorative Flower Vase Set of 2.jpg',
     'Slim-neck glass vases with a hand-painted floral motif. Ideal for hallways, dining tables and window sills.'),


    ('3D Elephant Wall Art',          'decor', 'low',    3500.00, 35, 'India',    200.00,  5,
     '3d_elephant_wall_art.jpg',
     'Handcrafted 3D metal elephant wall art in antique bronze finish. Adds a sculptural, ethnic touch to any wall.'),


    ('LED Metal Wall Leaves Art',     'decor', 'medium', 6800.00, 20, 'India',    350.00,  6,
     'led_metal_wall_leaves_tree_strutere_wall_art.jpg',
     'Backlit metal tree-of-life wall sculpture with warm LED strip lighting. Creates a dramatic focal point.'),


    ('3-Light Cluster Ceiling Lamp',  'decor', 'medium', 9500.00, 18, 'India',    500.00,  7,
     '3-Light Cluster Hanging Ceiling Lamp.jpg',
     'Industrial-style cluster pendant with three exposed Edison bulbs on braided cord. Suits cafes, dining rooms and lofts.'),


    ('Diamond Pendant Light 3-Light', 'decor', 'high',   18500.00,  9, 'Germany', 1500.00, 15,
     'Diamond Pendant Light 3-Lights Metal Cage Industrial Retro Cluster.jpg',
     'Geometric diamond-cage pendant in matt black with three warm-white bulbs. A bold statement for any ceiling.'),


    ('Retro Rustic Pendant Lamp',     'decor', 'low',    4200.00, 30, 'India',    300.00,  5,
     'Hanging Pendant Light Fixture Lampshade Aluminium Retro Rustic.jpg',
     'Spun-aluminium dome shade in weathered brass. A timeless rustic pendant that works in kitchens and dining rooms alike.'),



    # ── Construction Materials ─────────────────────────────────────────────────
    ('Pearl Grey Floor Marble Tile',  'construction_material', 'high',   3200.00, 500, 'Italy',  1200.00, 18,
     'Pearl Floor Marble - Skyros Marble Tile, Grey Color.jpg',
     'Premium Skyros-grey marble tiles (60×60 cm) with a polished finish. Suitable for floor and wall applications.'),

     
    ('Purple White Marble Floor Slab','construction_material', 'high',  35000.00,  10, 'Turkey', 3000.00, 28,
     'Purple White Marble Slabs For Flooring.jpg',
     'Exotic purple-white marble slabs with dramatic veining. Ideal for accent walls, countertops and luxury flooring.'),
]


BOOKINGS_DATA = [
    # (customer_username, professional_username, service_name, budget_level, booking_date_offset, booking_time, status, notes)
    ('rajesh_k', 'arjun_d',  'Living Room Design', 'medium', 9,  time(10, 0), 'pending',
     'Need a complete modern makeover for my 3BHK living room in Bangalore.'),
    ('priya_m',  'meena_s',  'House Plan – 2BHK',  'medium', 13, time(14, 0), 'confirmed',
     'Planning to build a new 2BHK house on a 1500 sq ft plot in Kochi.'),
    ('suresh_p', 'vijay_r',  'Renovation Work',    'low',    5,  time(9, 0),  'completed',
     'Kitchen and one bathroom renovation for my apartment in Hyderabad.'),
    ('priya_m',  'anita_b',  'Garden Design',      'low',    18, time(11, 0), 'pending',
     'Want a compact terrace garden with low-maintenance plants and a water feature.'),
    ('rajesh_k', 'meena_s',  'House Plan – 2BHK',  'low',    22, time(15, 30),'confirmed',
     'Require architectural drawings for a budget 2BHK house in Mysore.'),
]

QUOTATIONS_DATA = [
    # (customer_username, professional_username, project_title, description, budget_estimate, status, items)
    ('rajesh_k', 'arjun_d',
     'Living Room & Bedroom Redesign',
     'Complete redesign of the living room and master bedroom in a 3BHK flat. Includes custom furniture, lighting and décor.',
     180000.00, 'pending',
     [('3D Floor Plan & Mood Board', 1, 15000.00),
      ('Custom Sofa (3-seater)', 1, 55000.00),
      ('Accent Lighting Package', 1, 28000.00),
      ('Decorative Items & Accessories', 1, 12000.00),
      ('Interior Designer Fee', 2, 35000.00)]),

    ('priya_m', 'meena_s',
     'Villa Architectural Package',
     'Complete architectural package for a 3BHK villa including structural drawings, 3D renders and BOQ.',
     140000.00, 'accepted',
     [('Architectural Drawings Set', 1, 50000.00),
      ('Structural Design', 1, 40000.00),
      ('3D Exterior Render', 2, 25000.00)]),
]


# ─────────────────────────────────────────────
#  Command
# ─────────────────────────────────────────────

class Command(BaseCommand):
    help = 'Seed the database with realistic dummy data for GCIAP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing seeded data before inserting fresh records.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write(self.style.WARNING('Flushing existing data...'))
            self._flush()

        self.stdout.write(self.style.MIGRATE_HEADING('\n=== GCIAP Seed Data ===\n'))

        users     = self._seed_users()
        profs     = self._seed_professionals(users)
        self._seed_pricing(profs)
        self._seed_portfolios(profs)
        products  = self._seed_products()
        self._seed_bookings(users, profs)
        self._seed_quotations(users, profs)
        self._seed_orders(users, products)

        self.stdout.write(self.style.SUCCESS('\n✅  Seed completed successfully!\n'))

    # ── Flush ──────────────────────────────────────────────────────────────────
    def _flush(self):
        DeliveryTracking.objects.all().delete()
        Delivery.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Notification.objects.all().delete()
        Booking.objects.all().delete()
        QuotationItem.objects.all().delete()
        Quotation.objects.all().delete()
        Portfolio.objects.all().delete()
        ServicePricing.objects.all().delete()
        Professional.objects.all().delete()
        Product.objects.all().delete()
        UserProfile.objects.filter(user__username__in=[u[0] for u in USERS_DATA]).delete()
        User.objects.filter(username__in=[u[0] for u in USERS_DATA]).delete()
        self.stdout.write(self.style.WARNING('  Existing data removed.\n'))

    # ── Users ──────────────────────────────────────────────────────────────────
    def _seed_users(self):
        self.stdout.write('  Creating users & profiles...')
        users = {}
        for username, email, first, last, password, is_staff, is_su, phone, address, budget in USERS_DATA:
            user, created = User.objects.get_or_create(
                username=username,
                defaults=dict(email=email, first_name=first, last_name=last,
                              is_staff=is_staff, is_superuser=is_su),
            )
            if created:
                user.set_password(password)
                user.save()

            UserProfile.objects.get_or_create(
                user=user,
                defaults=dict(phone=phone, address=address, budget_preference=budget),
            )
            users[username] = user
            status = 'created' if created else 'exists'
            self.stdout.write(f'    [{status}] {username}')
        return users

    # ── Professionals ─────────────────────────────────────────────────────────
    def _seed_professionals(self, users):
        self.stdout.write('  Creating professionals...')
        profs = {}
        for username, prof_type, exp_years, phone, address, bio in PROFESSIONALS_DATA:
            user = users.get(username)
            if not user:
                continue
            prof, created = Professional.objects.get_or_create(
                user=user,
                defaults=dict(professional_type=prof_type, bio=bio,
                              experience_years=exp_years, phone=phone,
                              address=address, is_available=True),
            )
            profs[username] = prof
            status = 'created' if created else 'exists'
            self.stdout.write(f'    [{status}] {username} → {prof_type}')
        return profs

    # ── Service Pricing ───────────────────────────────────────────────────────
    def _seed_pricing(self, profs):
        self.stdout.write('  Creating service pricing...')
        count = 0
        for username, service_name, budget_level, price, description in PRICING_DATA:
            prof = profs.get(username)
            if not prof:
                continue
            _, created = ServicePricing.objects.get_or_create(
                professional=prof, service_name=service_name, budget_level=budget_level,
                defaults=dict(price=Decimal(str(price)), description=description),
            )
            if created:
                count += 1
        self.stdout.write(f'    {count} pricing records created.')

    # ── Portfolios ────────────────────────────────────────────────────────────
    def _seed_portfolios(self, profs):
        self.stdout.write('  Creating portfolio items & copying images...')
        count = 0
        for username, title, img_file, proj_date, description in PORTFOLIO_DATA:
            prof = profs.get(username)
            if not prof:
                continue
            if Portfolio.objects.filter(professional=prof, title=title).exists():
                self.stdout.write(f'    [exists] {title}')
                continue

            # Copy image into media/portfolios/
            rel_path = copy_image(img_file, MEDIA_PORTFOLIOS_DIR)
            p = Portfolio(professional=prof, title=title, description=description,
                          project_date=proj_date)
            if rel_path:
                p.image = rel_path
            p.save()
            count += 1
            self.stdout.write(f'    [created] {title}')
        self.stdout.write(f'    {count} portfolio items created.')

    # ── Products ──────────────────────────────────────────────────────────────
    def _seed_products(self):
        self.stdout.write('  Creating products & copying images...')
        products = {}
        count = 0
        for (name, category, budget_level, price, stock,
             supplier_country, shipping_cost, delivery_days,
             img_file, description) in PRODUCTS_DATA:

            if Product.objects.filter(name=name).exists():
                products[name] = Product.objects.get(name=name)
                self.stdout.write(f'    [exists] {name}')
                continue

            rel_path = copy_image(img_file, MEDIA_PRODUCTS_DIR)
            p = Product(
                name=name, category=category, budget_level=budget_level,
                price=Decimal(str(price)), stock_quantity=stock,
                supplier_country=supplier_country,
                shipping_cost=Decimal(str(shipping_cost)),
                delivery_days=delivery_days, description=description,
            )
            if rel_path:
                p.image = rel_path
            p.save()
            products[name] = p
            count += 1
            self.stdout.write(f'    [created] {name}')
        self.stdout.write(f'    {count} products created.')
        return products

    # ── Bookings & Notifications ───────────────────────────────────────────────
    def _seed_bookings(self, users, profs):
        self.stdout.write('  Creating bookings & notifications...')
        today = date.today()
        count = 0
        for (cust_username, prof_username, service_name, budget_level,
             day_offset, bk_time, status, notes) in BOOKINGS_DATA:

            customer = users.get(cust_username)
            prof     = profs.get(prof_username)
            if not customer or not prof:
                continue

            service = ServicePricing.objects.filter(
                professional=prof, service_name=service_name, budget_level=budget_level
            ).first()

            booking_date = today + timedelta(days=day_offset)

            if Booking.objects.filter(user=customer, professional=prof,
                                      booking_date=booking_date).exists():
                continue

            booking = Booking.objects.create(
                user=customer, professional=prof, service=service,
                booking_date=booking_date, booking_time=bk_time,
                status=status, notes=notes,
            )
            count += 1

            # Notification for customer
            Notification.objects.create(
                user=customer, booking=booking, is_read=False,
                message=(f'Your booking with {prof.user.get_full_name()} '
                         f'({prof.get_professional_type_display()}) on '
                         f'{booking_date.strftime("%d %b %Y")} has been received.'),
            )
            # Notification for professional
            Notification.objects.create(
                user=prof.user, booking=booking, is_read=False,
                message=(f'New booking request from {customer.get_full_name()} '
                         f'for {service_name} on {booking_date.strftime("%d %b %Y")}.'),
            )

        self.stdout.write(f'    {count} bookings + {count*2} notifications created.')

    # ── Quotations ────────────────────────────────────────────────────────────
    def _seed_quotations(self, users, profs):
        self.stdout.write('  Creating quotations...')
        count = 0
        for (cust_username, prof_username, title, description,
             budget, status, items) in QUOTATIONS_DATA:

            customer = users.get(cust_username)
            prof     = profs.get(prof_username)
            if not customer:
                continue

            if Quotation.objects.filter(user=customer, project_title=title).exists():
                self.stdout.write(f'    [exists] {title}')
                continue

            q = Quotation.objects.create(
                user=customer, professional=prof, project_title=title,
                project_description=description,
                budget_estimate=Decimal(str(budget)), status=status,
            )
            for item_name, qty, unit_price in items:
                QuotationItem.objects.create(
                    quotation=q, item_name=item_name, quantity=qty,
                    unit_price=Decimal(str(unit_price)),
                    total_price=Decimal(str(qty * unit_price)),
                )
            count += 1
            self.stdout.write(f'    [created] {title}')
        self.stdout.write(f'    {count} quotations created.')

    # ── Orders & Delivery ─────────────────────────────────────────────────────
    def _seed_orders(self, users, products):
        self.stdout.write('  Creating orders & deliveries...')
        today = date.today()

        orders_data = [
            ('rajesh_k', '12, MG Road, Bangalore, Karnataka', 'confirmed', [
                ('Scandinavian Wood Sofa', 1),
                ('Moksha Ceramic Waves Vase', 2),
            ]),
            ('priya_m', '45, Marine Drive, Kochi, Kerala', 'shipped', [
                ('Diamond Pendant Light 3-Light', 1),
                ('Blue Velvet Chesterfield Sofa', 1),
            ]),
            ('suresh_p', '34, Brigade Road, Bangalore, Karnataka', 'delivered', [
                ('Modern Office Chair', 2),
                ('Retro Rustic Pendant Lamp', 1),
            ]),
        ]

        count = 0
        for cust_username, shipping_address, order_status, order_items in orders_data:
            customer = users.get(cust_username)
            if not customer:
                continue

            if Order.objects.filter(user=customer, shipping_address=shipping_address).exists():
                self.stdout.write(f'    [exists] order for {cust_username}')
                continue

            total = Decimal('0')
            item_objs = []
            for product_name, qty in order_items:
                product = products.get(product_name)
                if product:
                    subtotal = product.price * qty
                    total += subtotal
                    item_objs.append((product, qty, product.price))

            order = Order.objects.create(
                user=customer, total_amount=total,
                shipping_address=shipping_address, status=order_status,
            )
            for product, qty, price in item_objs:
                OrderItem.objects.create(order=order, product=product,
                                         quantity=qty, price=price)

            # Create delivery record
            import random, string
            tracking_no = 'GCP' + ''.join(random.choices(string.digits, k=9))
            delivery_status_map = {
                'confirmed': 'pending',
                'shipped':   'in_transit',
                'delivered': 'delivered',
            }
            delivery = Delivery.objects.create(
                order=order,
                tracking_number=tracking_no,
                delivery_partner='BlueDart Express',
                estimated_delivery_date=today + timedelta(days=7),
                actual_delivery_date=today if order_status == 'delivered' else None,
                status=delivery_status_map.get(order_status, 'pending'),
                current_location='Mumbai Dispatch Hub' if order_status != 'delivered' else shipping_address,
            )

            # Tracking updates
            tracking_updates = [
                ('Mumbai Warehouse', 'Order confirmed and packed'),
                ('Mumbai Dispatch Hub', 'Dispatched from warehouse'),
            ]
            if order_status in ('shipped', 'delivered'):
                tracking_updates.append(('Pune Transit Hub', 'Package in transit'))
            if order_status == 'delivered':
                tracking_updates.append((shipping_address, 'Package delivered successfully'))

            for location, update in tracking_updates:
                DeliveryTracking.objects.create(
                    delivery=delivery, location=location, status_update=update,
                )

            count += 1
            self.stdout.write(f'    [created] order #{order.id} for {cust_username}')

        self.stdout.write(f'    {count} orders with deliveries created.')
