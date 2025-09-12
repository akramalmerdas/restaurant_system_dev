from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('api/get-customers/', views.get_customers_api, name='get_customers_api'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('customer_signup/', views.customerSignup, name='customer_signup'),
    path('profile/', views.customerProfile, name='customer_profile'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/add/', views.manage_customer, name='add_customer'),
    path('customer/<int:customer_id>/edit/', views.manage_customer, name='edit_customer'),
    path('customer/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),
]
