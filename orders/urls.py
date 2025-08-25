from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('order_details/', views.orderDetails, name='orderDetails'),
    path('order_details_api/<int:order_id>/', views.orderDetailApi, name='orderDetailsApi'),
    path('order_view/<int:order_id>/',views.orderView , name='orderView'),
    path('orders/', views.orderList, name='orderList'),
    path('add_to_order/', views.addToOrder, name='add_to_order'),
    path('order_details/delete_item/<int:item_id>/', views.delete_order_item, name='delete_order_item'),
    path('submit_order/', views.submitOrder, name='submit_order'),
    path('print_order/', views.printOrder, name='print_order'),
    path('admin_dashboard/', views.adminDashboard, name='admin_dashboard'),
    path('delete_order/<int:order_id>/', views.deleteOrder, name='delete_order'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('print_order_view/<int:order_id>/', views.print_order_view, name='print_order_view_url'),
    path('order/update-item/', views.updateOrderItem, name='update_order_item'),
    path('order_detail/empty_order/', views.emptyOrder, name='empty_order_item'),
    path('cancelled_orders/', views.cancelled_orders, name='cancelled_orders'),
    path('meal/<int:menu_item_id>/',views.orderPage,name='orderPage'),
    path('get-extras/<int:menu_item_id>/', views.get_extras, name='get_extras'),
]
