from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Professional, Portfolio, ServicePricing
from .forms import ProfessionalForm, PortfolioForm, ServicePricingForm
from users.decorators import professional_required, admin_or_professional_required, admin_required
from users.roles import get_user_role, is_admin, is_professional

def professional_list(request):
    prof_type = request.GET.get('type', '')
    professionals = Professional.objects.filter(is_available=True)
    if prof_type:
        professionals = professionals.filter(professional_type=prof_type)

    # Human-readable label map for the empty state message
    type_labels = {
        'interior_designer': 'Interior Designers',
        'exterior_designer': 'Exterior Designers',
        'architect':         'Architects',
        'worker':            'Workers',
        'contractor':        'Contractors',
    }
    selected_type_label = type_labels.get(prof_type, '')

    return render(request, 'professionals/professional_list.html', {
        'professionals':      professionals,
        'prof_type':          prof_type,
        'selected_type_label': selected_type_label,
    })

def professional_detail(request, pk):
    professional = get_object_or_404(Professional, pk=pk)
    portfolios = professional.portfolios.all()
    pricings = professional.pricings.all()
    budget = request.GET.get('budget')
    if budget:
        pricings = pricings.filter(budget_level=budget)
    return render(request, 'professionals/professional_detail.html', {
        'professional': professional,
        'portfolios': portfolios,
        'pricings': pricings
    })

@admin_required  # Changed to admin-only
def create_professional(request):
    """
    Admin-only view to create professional profiles.
    Regular users cannot access this.
    """
    if request.method == 'POST':
        form = ProfessionalForm(request.POST)
        if form.is_valid():
            professional = form.save(commit=False)
            # Admin can specify which user to make professional
            professional.save()
            messages.success(request, f'Professional profile created for {professional.user.username}!')
            return redirect('custom_admin:professional_list')
    else:
        form = ProfessionalForm()
    return render(request, 'professionals/create_professional.html', {'form': form})

@admin_or_professional_required
def dashboard(request):
    # Allow admins to view any professional's dashboard
    if is_admin(request.user):
        # Optionally, redirect admin to admin panel or show all professionals
        return redirect('custom_admin:dashboard')
    
    try:
        professional = Professional.objects.get(user=request.user)
        portfolios = professional.portfolios.all()
        pricings = professional.pricings.all()
        bookings = professional.bookings.all().order_by('-created_at')
        return render(request, 'professionals/dashboard.html', {
            'professional': professional,
            'portfolios': portfolios,
            'pricings': pricings,
            'bookings': bookings
        })
    except Professional.DoesNotExist:
        return redirect('professionals:create_professional')

@professional_required
def add_portfolio(request):
    professional = get_object_or_404(Professional, user=request.user)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.professional = professional
            portfolio.save()
            messages.success(request, 'Portfolio added!')
            return redirect('professionals:dashboard')
    else:
        form = PortfolioForm()
    return render(request, 'professionals/add_portfolio.html', {'form': form})

@professional_required
def delete_portfolio(request, pk):
    professional = get_object_or_404(Professional, user=request.user)
    portfolio = get_object_or_404(Portfolio, pk=pk, professional=professional)
    portfolio.delete()
    messages.success(request, 'Portfolio deleted!')
    return redirect('professionals:dashboard')

@professional_required
def add_pricing(request):
    professional = get_object_or_404(Professional, user=request.user)
    if request.method == 'POST':
        form = ServicePricingForm(request.POST)
        if form.is_valid():
            pricing = form.save(commit=False)
            pricing.professional = professional
            pricing.save()
            messages.success(request, 'Service pricing added!')
            return redirect('professionals:dashboard')
    else:
        form = ServicePricingForm()
    return render(request, 'professionals/add_pricing.html', {'form': form})

@professional_required
def delete_pricing(request, pk):
    professional = get_object_or_404(Professional, user=request.user)
    pricing = get_object_or_404(ServicePricing, pk=pk, professional=professional)
    pricing.delete()
    messages.success(request, 'Service pricing deleted!')
    return redirect('professionals:dashboard')
