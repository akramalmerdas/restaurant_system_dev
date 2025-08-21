from django.contrib import admin
from .models import Order, OrderItem, OrderStatus, OrderItemExtra, DailyOrderCounter, Discount

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'table_number', 'order_status', 'total_amount', 'ordered_at')
    list_filter = ('order_status', 'ordered_at')
    search_fields = ('id', 'customer__user__username', 'table_number')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'item', 'price')
    search_fields = ('order__id', 'item__name')

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(OrderItemExtra)
class OrderItemExtraAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_item', 'extra', 'quantity')

@admin.register(DailyOrderCounter)
class DailyOrderCounterAdmin(admin.ModelAdmin):
    list_display = ('date', 'counter')

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('order', 'discount_code', 'discount_amount')
