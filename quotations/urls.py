from django.urls import path
from . import views

app_name = 'quotations'

urlpatterns = [
    path('', views.quotation_list, name='quotation_list'),
    path('<int:pk>/', views.quotation_detail, name='quotation_detail'),
    path('create/', views.create_quotation, name='create_quotation'),
    path('<int:pk>/add-item/', views.add_quotation_item, name='add_quotation_item'),
    path('<int:pk>/delete/', views.delete_quotation, name='delete_quotation'),
]
