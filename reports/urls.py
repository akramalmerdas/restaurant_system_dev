from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('sales_report/', views.sales_report, name='sales_report'),
    path('payment_report/', views.payment_report, name='payment_report'),
    path('staff_report/', views.staff_report, name='staff_report'),
]
