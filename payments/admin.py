from django.contrib import admin
from .models import Invoice, Payment, UnpaidReasonLog

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'table__number')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'amount', 'method', 'created_at')
    list_filter = ('method', 'created_at')
    search_fields = ('invoice__id',)

@admin.register(UnpaidReasonLog)
class UnpaidReasonLogAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'user', 'created_at')
    search_fields = ('invoice__id', 'user__username')
