from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, Notification
from .forms import BookingForm
from professionals.models import Professional, ServicePricing

@login_required
def create_booking(request, professional_id, service_id):
    professional = get_object_or_404(Professional, pk=professional_id)
    service = get_object_or_404(ServicePricing, pk=service_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.professional = professional
            booking.service = service
            booking.save()
            Notification.objects.create(
                user=professional.user,
                booking=booking,
                message=f'New booking from {request.user.username}'
            )
            messages.success(request, 'Booking created successfully!')
            return redirect('users:booking_history')
    else:
        form = BookingForm()
    
    return render(request, 'bookings/create_booking.html', {
        'form': form,
        'professional': professional,
        'service': service
    })

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.user != request.user and booking.professional.user != request.user:
        messages.error(request, 'Access denied!')
        return redirect('home')
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def update_booking_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk, professional__user=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Booking.STATUS_CHOICES):
            booking.status = status
            booking.save()
            Notification.objects.create(
                user=booking.user,
                booking=booking,
                message=f'Your booking status updated to {status}'
            )
            messages.success(request, 'Booking status updated!')
    return redirect('professionals:dashboard')

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, 'Booking cancelled!')
    return redirect('users:booking_history')

@login_required
def notifications(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'bookings/notifications.html', {'notifications': notifications})
