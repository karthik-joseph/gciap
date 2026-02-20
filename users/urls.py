from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('check-username/', views.check_username, name='check_username'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('booking-history/', views.booking_history, name='booking_history'),
    path('role-status/', views.role_status, name='role_status'),
    path('request-upgrade/', views.request_upgrade, name='request_upgrade'),
    path('upgrade-status/', views.upgrade_status, name='upgrade_status'),
]
