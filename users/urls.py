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
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/add/', views.manage_staff, name='add_staff'),
    path('staff/<int:staff_id>/edit/', views.manage_staff, name='edit_staff'),
    path('staff/<int:staff_id>/delete/', views.delete_staff, name='delete_staff'),
    path('staff/<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('staff/<int:staff_id>/loan/add/', views.manage_loan, name='add_loan'),
    path('staff/<int:staff_id>/deduction/add/', views.manage_deduction, name='add_deduction'),
    path('staff/<int:staff_id>/leave/add/', views.manage_leave, name='add_leave'),
    path('staff/<int:staff_id>/repayment/add/', views.add_repayment, name='add_repayment'),
    path('leave/<int:leave_id>/manage/', views.manage_leave_entry, name='manage_leave_entry'),
]