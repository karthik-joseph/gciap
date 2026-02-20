from django.urls import path
from . import views

app_name = 'professionals'

urlpatterns = [
    path('', views.professional_list, name='professional_list'),
    path('<int:pk>/', views.professional_detail, name='professional_detail'),
    path('create/', views.create_professional, name='create_professional'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('portfolio/add/', views.add_portfolio, name='add_portfolio'),
    path('portfolio/delete/<int:pk>/', views.delete_portfolio, name='delete_portfolio'),
    path('pricing/add/', views.add_pricing, name='add_pricing'),
    path('pricing/delete/<int:pk>/', views.delete_pricing, name='delete_pricing'),
]
