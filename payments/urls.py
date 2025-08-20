from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('generate-invoice-by-table/', views.generate_invoice_by_table, name='generate_invoice_table'),
    path('generate-invoice-by-item/', views.generateInvoiceByItem, name='generate_invoice_item'),
    path('invoices/', views.invoice_dashboard, name='invoice_dashboard'),
    path('invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path('invoiceA4/<int:invoice_id>/', views.view_invoiceA4, name='view_invoice_A4'),
    path("invoice/<int:invoice_id>/update-status/", views.update_invoice_status, name="update_invoice_status"),
    path("invoice/<int:invoice_id>/pay/", views.process_payment, name="process_payment"),
    path('mark-unpaid/', views.mark_unpaid, name='mark_unpaid'),
    path('print_invoice/<int:invoice_id>/', views.print_invoice_view, name='print_invoice'),
]
