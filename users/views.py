import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserProfileForm, ProfessionalUpgradeRequestForm
from .models import UserProfile, ProfessionalUpgradeRequest
from .roles import get_user_role, ROLE_PERMISSIONS

def check_username(request):
    """AJAX endpoint to check username availability and search existing users."""
    username = request.GET.get('username', '').strip()
    
    if not username:
        return JsonResponse({'available': False, 'error': 'Username is required.', 'suggestions': []})
    
    # Check minimum length
    if len(username) < 3:
        return JsonResponse({
            'available': False,
            'error': 'Username must be at least 3 characters long.',
            'suggestions': []
        })
    
    # Validate format: must start with letter or underscore, only letters/numbers/underscores
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', username):
        return JsonResponse({
            'available': False,
            'error': 'Username must start with a letter or underscore, and contain only letters, numbers, or underscores.',
            'suggestions': []
        })
    
    # Check if username is taken
    is_taken = User.objects.filter(username=username).exists()
    
    # Get suggestions for similar usernames (existing users)
    suggestions = []
    if is_taken:
        # Suggest variations
        for suffix in ['_1', '_2', '1', '2', '_new']:
            suggested = f"{username}{suffix}"
            if not User.objects.filter(username=suggested).exists():
                suggestions.append(suggested)
                if len(suggestions) >= 3:
                    break
    
    # Get existing usernames that match the query (for autocomplete/search)
    matching_users = list(
        User.objects.filter(username__istartswith=username)
        .values_list('username', flat=True)[:5]
    )
    
    return JsonResponse({
        'available': not is_taken,
        'error': 'This username is already taken.' if is_taken else '',
        'suggestions': suggestions,
        'matching_users': matching_users
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                budget_preference=form.cleaned_data['budget_preference']
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('custom_admin:login')
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_staff:
                messages.warning(request, 'Admins must use the Admin Portal.')
                return redirect('custom_admin:login')
            
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials!')
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def profile(request):
    # Create UserProfile if it doesn't exist (for admin users created via createsuperuser)
    profile_obj, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': '',
            'address': '',
            'budget_preference': 'medium'
        }
    )
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=profile_obj)
    
    # Get upgrade request status
    upgrade_request = ProfessionalUpgradeRequest.objects.filter(user=request.user).order_by('-created_at').first()
    
    return render(request, 'users/profile.html', {
        'form': form,
        'profile': profile_obj,
        'upgrade_request': upgrade_request,
    })

@login_required
def booking_history(request):
    bookings = request.user.bookings.all().order_by('-created_at')
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'users/booking_history.html', {'bookings': bookings, 'orders': orders})

@login_required
def role_status(request):
    """View to display the current user's role and permissions"""
    role = get_user_role(request.user)
    permissions = ROLE_PERMISSIONS.get(role, [])
    
    context = {
        'role': role,
        'permissions': permissions,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
        'has_professional_profile': hasattr(request.user, 'professional'),
    }
    
    if hasattr(request.user, 'professional'):
        context['professional'] = request.user.professional
    
    return render(request, 'users/role_status.html', context)

@login_required
def request_upgrade(request):
    """View for regular users to request a professional upgrade."""
    # Don't allow admins or existing professionals
    if request.user.is_staff:
        messages.warning(request, 'Admins do not need to request professional status.')
        return redirect('users:profile')
    
    if hasattr(request.user, 'professional'):
        messages.info(request, 'You already have a professional profile!')
        return redirect('professionals:dashboard')
    
    # Check if there's already a pending request
    existing_request = ProfessionalUpgradeRequest.objects.filter(
        user=request.user, status='pending'
    ).first()
    
    if existing_request:
        messages.info(request, 'You already have a pending upgrade request. Please wait for admin review.')
        return redirect('users:upgrade_status')
    
    if request.method == 'POST':
        form = ProfessionalUpgradeRequestForm(request.POST)
        if form.is_valid():
            upgrade_req = form.save(commit=False)
            upgrade_req.user = request.user
            upgrade_req.save()
            messages.success(request, 'Your professional upgrade request has been submitted! You will be notified once an admin reviews it.')
            return redirect('users:upgrade_status')
    else:
        # Pre-fill from UserProfile if available
        initial_data = {}
        if hasattr(request.user, 'userprofile'):
            profile_obj = request.user.userprofile
            initial_data = {
                'phone': str(profile_obj.phone) if profile_obj.phone else '',
                'address': profile_obj.address or '',
            }
        form = ProfessionalUpgradeRequestForm(initial=initial_data)
    
    return render(request, 'users/request_upgrade.html', {'form': form})

@login_required
def upgrade_status(request):
    """View for users to check their upgrade request status."""
    upgrade_requests = ProfessionalUpgradeRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/upgrade_status.html', {'upgrade_requests': upgrade_requests})

def home(request):
    return render(request, 'home.html')
