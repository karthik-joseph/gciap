from django.shortcuts import render, redirect, get_object_or_404
from .decorators import admin_required as staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from users.models import UserProfile, ProfessionalUpgradeRequest
from users.forms import AdminUserEditForm
from professionals.models import Professional, Portfolio, ServicePricing
from products.models import Product, Cart, CartItem, Order, OrderItem, OrderStatusHistory
from quotations.models import Quotation, QuotationItem
from bookings.models import Booking, Notification
from delivery.models import Delivery, DeliveryTracking
from .forms import (
    UserProfileAdminForm, ProfessionalAdminForm, PortfolioAdminForm,
    ServicePricingAdminForm, ProductAdminForm, QuotationAdminForm,
    BookingAdminForm, DeliveryAdminForm, DeliveryTrackingAdminForm
)
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test

def admin_login(request):
    next_url = request.GET.get('next')
    
    if request.user.is_authenticated:
        if request.user.is_staff:
            if next_url:
                return redirect(next_url)
            return redirect('custom_admin:dashboard')
        else:
            messages.error(request, 'Access denied. Staff privileges required.')
            return redirect('home')
            
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                if next_url:
                    return redirect(next_url)
                return redirect('custom_admin:dashboard')
            else:
                messages.error(request, 'Access denied. Staff privileges required.')
        else:
            messages.error(request, 'Invalid admin credentials.')
            
    return render(request, 'custom_admin/login.html')

@staff_member_required
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_professionals': Professional.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_bookings': Booking.objects.count(),
        'pending_bookings': Booking.objects.filter(status='pending').count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'pending_upgrades': ProfessionalUpgradeRequest.objects.filter(status='pending').count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_orders': Order.objects.order_by('-created_at')[:5],
        'recent_bookings': Booking.objects.order_by('-created_at')[:5],
    }
    return render(request, 'custom_admin/dashboard.html', context)

@staff_member_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    
    # Search
    query = request.GET.get('q')
    if query:
        users = users.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        
    return render(request, 'custom_admin/users/list.html', {'users': users})

@staff_member_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    try:
        profile = user.userprofile
    except:
        profile = None
    
    # Get upgrade requests for this user
    upgrade_requests = ProfessionalUpgradeRequest.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'custom_admin/users/detail.html', {
        'user': user,
        'profile': profile,
        'upgrade_requests': upgrade_requests,
    })

@staff_member_required
def user_edit(request, pk):
    """Admin view to edit user details."""
    user_obj = get_object_or_404(User, pk=pk)
    
    try:
        profile = user_obj.userprofile
    except UserProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        user_form = AdminUserEditForm(request.POST, instance=user_obj)
        profile_form = UserProfileAdminForm(request.POST, instance=profile) if profile else None
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, f'User {user_obj.username} updated successfully!')
            return redirect('custom_admin:user_detail', pk=pk)
    else:
        user_form = AdminUserEditForm(instance=user_obj)
        profile_form = UserProfileAdminForm(instance=profile) if profile else None
    
    return render(request, 'custom_admin/users/edit.html', {
        'user_obj': user_obj,
        'user_form': user_form,
        'profile_form': profile_form,
    })

@staff_member_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    # Prevent deleting admin users
    if user.is_staff or user.is_superuser:
        messages.error(request, 'Cannot delete admin users!')
        return redirect('custom_admin:user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('custom_admin:user_list')
    
    # For GET requests, we no longer use this page — deletion is via modal
    return redirect('custom_admin:user_list')

@staff_member_required
def user_delete_ajax(request, pk):
    """AJAX endpoint for deleting users via modal."""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        
        # Prevent deleting admin users
        if user.is_staff or user.is_superuser:
            return JsonResponse({'success': False, 'error': 'Cannot delete admin users!'})
        
        username = user.username
        user.delete()
        return JsonResponse({'success': True, 'message': f'User {username} deleted successfully!'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@staff_member_required
def convert_to_professional(request, pk):
    """
    Admin view to convert a regular user to a professional.
    """
    user = get_object_or_404(User, pk=pk)
    
    # Don't allow converting admin users
    if user.is_staff or user.is_superuser:
        messages.warning(request, 'Admin users cannot be converted to professionals.')
        return redirect('custom_admin:user_detail', pk=pk)
    
    # Check if user is already a professional
    if hasattr(user, 'professional'):
        messages.warning(request, f'{user.username} is already a professional!')
        return redirect('custom_admin:user_detail', pk=pk)
    
    if request.method == 'POST':
        from professionals.forms import ProfessionalForm
        form = ProfessionalForm(request.POST)
        if form.is_valid():
            professional = form.save(commit=False)
            professional.user = user
            professional.save()
            messages.success(request, f'{user.username} has been converted to a professional!')
            return redirect('custom_admin:professional_detail', pk=professional.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from professionals.forms import ProfessionalForm
        # Pre-fill user field and profile data
        initial_data = {'user': user}
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
            initial_data.update({
                'phone': str(profile.phone) if profile.phone else '',
                'address': profile.address or ''
            })
        form = ProfessionalForm(initial=initial_data)
        # Make user field readonly since we're converting a specific user
        form.fields['user'].widget.attrs['readonly'] = True
        form.fields['user'].disabled = True
    
    return render(request, 'custom_admin/users/convert_to_professional.html', {
        'form': form,
        'user': user
    })


# =====================
# Upgrade Request Management
# =====================

@staff_member_required
def upgrade_request_list(request):
    """Admin view to list all professional upgrade requests."""
    requests = ProfessionalUpgradeRequest.objects.all().select_related('user').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        requests = requests.filter(status=status)
    
    # Search
    query = request.GET.get('q')
    if query:
        requests = requests.filter(
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(professional_type__icontains=query)
        )
    
    return render(request, 'custom_admin/users/upgrade_requests.html', {'upgrade_requests': requests})

@staff_member_required
def upgrade_request_detail(request, pk):
    """Admin view to see upgrade request details."""
    upgrade_req = get_object_or_404(ProfessionalUpgradeRequest, pk=pk)
    return render(request, 'custom_admin/users/upgrade_request_detail.html', {'upgrade_request': upgrade_req})

@staff_member_required
def upgrade_request_approve(request, pk):
    """Admin view to approve an upgrade request and create professional profile."""
    upgrade_req = get_object_or_404(ProfessionalUpgradeRequest, pk=pk)
    
    if upgrade_req.status != 'pending':
        messages.warning(request, 'This request has already been processed.')
        return redirect('custom_admin:upgrade_request_detail', pk=pk)
    
    if request.method == 'POST':
        # Create the professional profile
        user = upgrade_req.user
        
        # Check if already a professional
        if hasattr(user, 'professional'):
            upgrade_req.status = 'approved'
            upgrade_req.admin_notes = 'User already had a professional profile.'
            upgrade_req.save()
            messages.info(request, f'{user.username} already has a professional profile.')
            return redirect('custom_admin:upgrade_request_list')
        
        # Create professional
        Professional.objects.create(
            user=user,
            professional_type=upgrade_req.professional_type,
            bio=upgrade_req.bio,
            experience_years=upgrade_req.experience_years,
            phone=upgrade_req.phone,
            address=upgrade_req.address,
            is_available=True,
        )
        
        upgrade_req.status = 'approved'
        upgrade_req.admin_notes = request.POST.get('admin_notes', '')
        upgrade_req.save()
        
        messages.success(request, f'{user.username} has been upgraded to a professional!')
        return redirect('custom_admin:upgrade_request_list')
    
    return redirect('custom_admin:upgrade_request_detail', pk=pk)

@staff_member_required
def upgrade_request_reject(request, pk):
    """Admin view to reject an upgrade request."""
    upgrade_req = get_object_or_404(ProfessionalUpgradeRequest, pk=pk)
    
    if upgrade_req.status != 'pending':
        messages.warning(request, 'This request has already been processed.')
        return redirect('custom_admin:upgrade_request_detail', pk=pk)
    
    if request.method == 'POST':
        upgrade_req.status = 'rejected'
        upgrade_req.admin_notes = request.POST.get('admin_notes', 'Request rejected by admin.')
        upgrade_req.save()
        messages.success(request, f'Upgrade request from {upgrade_req.user.username} has been rejected.')
        return redirect('custom_admin:upgrade_request_list')
    
    return redirect('custom_admin:upgrade_request_detail', pk=pk)


@staff_member_required
def professional_list(request):
    professionals = Professional.objects.all().select_related('user').order_by('-created_at')
    
    # Search
    query = request.GET.get('q')
    if query:
        professionals = professionals.filter(
            Q(user__username__icontains=query) | 
            Q(bio__icontains=query)
        )
        
    return render(request, 'custom_admin/professionals/list.html', {'professionals': professionals})

@staff_member_required
def professional_detail(request, pk):
    professional = get_object_or_404(Professional, pk=pk)
    portfolios = professional.portfolios.all()
    pricings = professional.pricings.all()
    bookings = professional.bookings.all()
    return render(request, 'custom_admin/professionals/detail.html', {
        'professional': professional,
        'portfolios': portfolios,
        'pricings': pricings,
        'bookings': bookings
    })

@staff_member_required
def professional_edit(request, pk):
    professional = get_object_or_404(Professional, pk=pk)
    if request.method == 'POST':
        form = ProfessionalAdminForm(request.POST, instance=professional)
        if form.is_valid():
            form.save()
            messages.success(request, 'Professional updated successfully!')
            return redirect('custom_admin:professional_detail', pk=pk)
    else:
        form = ProfessionalAdminForm(instance=professional)
    return render(request, 'custom_admin/professionals/edit.html', {'form': form, 'professional': professional})

@staff_member_required
def professional_delete(request, pk):
    professional = get_object_or_404(Professional, pk=pk)
    if request.method == 'POST':
        professional.delete()
        messages.success(request, 'Professional deleted successfully!')
        return redirect('custom_admin:professional_list')
    return render(request, 'custom_admin/professionals/delete.html', {'professional': professional})

@staff_member_required
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    
    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(supplier_country__icontains=query)
        )
    
    # Filter
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
        
    budget = request.GET.get('budget')
    if budget:
        products = products.filter(budget_level=budget)
        
    return render(request, 'custom_admin/products/list.html', {'products': products})

@staff_member_required
def product_create(request):
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('custom_admin:product_list')
    else:
        form = ProductAdminForm()
    return render(request, 'custom_admin/products/create.html', {'form': form})

@staff_member_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('custom_admin:product_list')
    else:
        form = ProductAdminForm(instance=product)
    return render(request, 'custom_admin/products/edit.html', {'form': form, 'product': product})

@staff_member_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('custom_admin:product_list')
    return render(request, 'custom_admin/products/delete.html', {'product': product})

@staff_member_required
def order_list(request):
    orders = Order.objects.all().select_related('user').order_by('-created_at')
    
    # Search
    query = request.GET.get('q')
    if query:
        # Check if query is numeric for ID search
        if query.isdigit():
            orders = orders.filter(Q(id=query) | Q(user__username__icontains=query))
        else:
            orders = orders.filter(user__username__icontains=query)
            
    # Filter
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
        
    return render(request, 'custom_admin/orders/list.html', {'orders': orders})

@staff_member_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    try:
        delivery = order.delivery
    except:
        delivery = None
    return render(request, 'custom_admin/orders/detail.html', {
        'order': order,
        'items': items,
        'delivery': delivery
    })

@staff_member_required
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.ORDER_STATUS) and new_status != order.status:
            order.status = new_status
            order.save()
            # Record the change in history so the tracking page shows it
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                changed_by=request.user,
            )
            messages.success(request, f'Order status updated to "{order.get_status_display()}".') 
    return redirect('custom_admin:order_detail', pk=pk)

@staff_member_required
def booking_list(request):
    bookings = Booking.objects.all().select_related('user', 'professional').order_by('-created_at')
    
    # Search
    query = request.GET.get('q')
    if query:
        if query.isdigit():
            bookings = bookings.filter(
                Q(id=query) | 
                Q(user__username__icontains=query) |
                Q(professional__user__username__icontains=query)
            )
        else:
            bookings = bookings.filter(
                Q(user__username__icontains=query) |
                Q(professional__user__username__icontains=query)
            )
            
    # Filter
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)

    return render(request, 'custom_admin/bookings/list.html', {'bookings': bookings})

@staff_member_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'custom_admin/bookings/detail.html', {'booking': booking})

@staff_member_required
def booking_update_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Booking.STATUS_CHOICES):
            booking.status = status
            booking.save()
            messages.success(request, f'Booking status updated to {status}!')
    return redirect('custom_admin:booking_detail', pk=pk)

@staff_member_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully!')
        return redirect('custom_admin:booking_list')
    return render(request, 'custom_admin/bookings/delete.html', {'booking': booking})

@staff_member_required
def quotation_list(request):
    quotations = Quotation.objects.all().select_related('user').order_by('-created_at')
    
    # Search
    query = request.GET.get('q')
    if query:
        if query.isdigit():
            quotations = quotations.filter(Q(id=query) | Q(user__username__icontains=query))
        else:
            quotations = quotations.filter(Q(user__username__icontains=query))
            
    # Filter
    status = request.GET.get('status')
    if status:
        quotations = quotations.filter(status=status)
        
    return render(request, 'custom_admin/quotations/list.html', {'quotations': quotations})

@staff_member_required
def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    items = quotation.items.all()
    return render(request, 'custom_admin/quotations/detail.html', {
        'quotation': quotation,
        'items': items
    })

@staff_member_required
def quotation_delete(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    if request.method == 'POST':
        quotation.delete()
        messages.success(request, 'Quotation deleted successfully!')
        return redirect('custom_admin:quotation_list')
    return render(request, 'custom_admin/quotations/delete.html', {'quotation': quotation})

@staff_member_required
def delivery_list(request):
    deliveries = Delivery.objects.all().select_related('order').order_by('-created_at')
    
    # Search
    query = request.GET.get('q')
    if query:
        if query.isdigit():
             deliveries = deliveries.filter(Q(order__id=query))
        else:
             deliveries = deliveries.filter(tracking_number__icontains=query)

    return render(request, 'custom_admin/delivery/list.html', {'deliveries': deliveries})

@staff_member_required
def delivery_create(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        form = DeliveryAdminForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.order = order
            delivery.save()
            messages.success(request, 'Delivery created successfully!')
            return redirect('custom_admin:order_detail', pk=order_id)
    else:
        form = DeliveryAdminForm()
    return render(request, 'custom_admin/delivery/create.html', {'form': form, 'order': order})

@staff_member_required
def delivery_edit(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method == 'POST':
        form = DeliveryAdminForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            messages.success(request, 'Delivery updated successfully!')
            return redirect('custom_admin:order_detail', pk=delivery.order.pk)
    else:
        form = DeliveryAdminForm(instance=delivery)
    return render(request, 'custom_admin/delivery/edit.html', {'form': form, 'delivery': delivery})

@staff_member_required
def delivery_add_tracking(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method == 'POST':
        form = DeliveryTrackingAdminForm(request.POST)
        if form.is_valid():
            tracking = form.save(commit=False)
            tracking.delivery = delivery
            tracking.save()
            messages.success(request, 'Tracking update added!')
            return redirect('custom_admin:order_detail', pk=delivery.order.pk)
    else:
        form = DeliveryTrackingAdminForm()
    return render(request, 'custom_admin/delivery/add_tracking.html', {'form': form, 'delivery': delivery})
