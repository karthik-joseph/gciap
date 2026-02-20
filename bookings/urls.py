from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:professional_id>/<int:service_id>/', views.create_booking, name='create_booking'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/update-status/', views.update_booking_status, name='update_booking_status'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('notifications/', views.notifications, name='notifications'),
]
