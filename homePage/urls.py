from django.urls import path

from . import views

urlpatterns =[
    path('',views.index,name='index'),
    path('meal/<int:menu_item_id>/',views.orderPage,name='orderPage'),
    path('get-extras/<int:menu_item_id>/', views.get_extras, name='get_extras'),
    path('order_details/', views.orderDetails, name='orderDetails'),
    path('order_view/<int:order_id>/',views.orderView , name='orderView'),
    path('orders/', views.orderList, name='orderList'),
    path('add_to_order/', views.addToOrder, name='add_to_order'),
    path('order_details/delete_item/<int:item_id>/', views.delete_order_item, name='delete_order_item'),
    path('submit_order/', views.submitOrder, name='submit_order'),
    path('print_order/', views.printOrder, name='print_order'),
    path('login/', views.login_view, name='login'),
    path('admin_dashboard/', views.adminDashboard, name='admin_dashboard'),  # Example redirect
 #   path('customer_home/', views.customer_home, name='customer_home'),  
    path('customer_signup/', views.customerSignup, name='customer_signup'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.customerProfile, name='customer_profile'),
    path('delete_order/<int:order_id>/', views.deleteOrder, name='delete_order'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('print_order_view/<int:order_id>/', views.print_order_view, name='print_order'),
    path('generate_invoice/<int:table_id>/', views.generate_invoice, name='generate_invoice'),  
    path('invoices/', views.invoice_dashboard, name='invoice_dashboard'),
    path('invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path("invoice/<int:invoice_id>/change-status/", views.change_invoice_status, name="change_invoice_status"),
  


]