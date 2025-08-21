from django.contrib import admin
from .models import Staff, Customer

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'phone_number')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'loyalty_points')
    search_fields = ('user__username', 'phone_number')
