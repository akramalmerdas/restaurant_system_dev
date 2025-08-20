from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('tables/', views.table_dashboard, name='table_dashboard'),
    path('tables/<int:table_id>/update/', views.update_table_status, name='update_table_status'),
    path('tables/<int:table_id>/delete/', views.delete_table, name='delete_table'),
    path('tables/<int:table_id>/edit/', views.edit_table, name='edit_table'),
    path('tables/<int:table_id>/history/', views.get_table_history, name='get_table_history'),
    path('set_table/', views.setTableNumber, name='set_table_number'),
    path('table_landing/', views.tableLanding, name='table_landing_page'),
    path('get_order_by_table/<int:table_id>/',views.getOrderByTable , name='get_order_by_table'),
    path('move_table_view/', views.moveTable, name='move_table_view'),
]
