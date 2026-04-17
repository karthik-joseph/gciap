from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('', views.admin_dashboard, name='dashboard'),
    
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/delete-ajax/', views.user_delete_ajax, name='user_delete_ajax'),
    path('users/<int:pk>/convert-to-professional/', views.convert_to_professional, name='convert_to_professional'),
    
    # Upgrade Requests
    path('upgrade-requests/', views.upgrade_request_list, name='upgrade_request_list'),
    path('upgrade-requests/<int:pk>/', views.upgrade_request_detail, name='upgrade_request_detail'),
    path('upgrade-requests/<int:pk>/approve/', views.upgrade_request_approve, name='upgrade_request_approve'),
    path('upgrade-requests/<int:pk>/reject/', views.upgrade_request_reject, name='upgrade_request_reject'),
    
    path('professionals/', views.professional_list, name='professional_list'),
    path('professionals/<int:pk>/', views.professional_detail, name='professional_detail'),
    path('professionals/<int:pk>/edit/', views.professional_edit, name='professional_edit'),
    path('professionals/<int:pk>/delete/', views.professional_delete, name='professional_delete'),
    
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/update-status/', views.booking_update_status, name='booking_update_status'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    
    path('quotations/', views.quotation_list, name='quotation_list'),
    path('quotations/<int:pk>/', views.quotation_detail, name='quotation_detail'),
    path('quotations/<int:pk>/update-status/', views.quotation_update_status, name='quotation_update_status'),
    path('quotations/<int:pk>/delete/', views.quotation_delete, name='quotation_delete'),
    
    path('delivery/', views.delivery_list, name='delivery_list'),
    path('delivery/create/<int:order_id>/', views.delivery_create, name='delivery_create'),
    path('delivery/<int:pk>/edit/', views.delivery_edit, name='delivery_edit'),
    path('delivery/<int:pk>/add-tracking/', views.delivery_add_tracking, name='delivery_add_tracking'),
]
