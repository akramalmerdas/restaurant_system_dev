from django.contrib import admin
from .models import Inventory, Supplier

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity_in_stock', 'reorder_level', 'expiration_date')
    list_filter = ('expiration_date',)
    search_fields = ('item__name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone_number')
    search_fields = ('name', 'contact_person')
