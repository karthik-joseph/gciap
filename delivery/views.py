from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Delivery, DeliveryTracking
from products.models import Order, OrderStatusHistory

@login_required
def track_delivery(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    try:
        delivery = order.delivery
        tracking_updates = delivery.tracking_updates.all()
    except Delivery.DoesNotExist:
        delivery = None
        tracking_updates = []

    status_history = order.status_history.all()  # ordered by changed_at asc

    return render(request, 'delivery/track_delivery.html', {
        'order': order,
        'delivery': delivery,
        'tracking_updates': tracking_updates,
        'status_history': status_history,
    })
