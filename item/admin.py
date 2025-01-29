from django.contrib import admin


from .models import *
# Register your models here.
class OrderItemExtraInline(admin.TabularInline):
    model = OrderItemExtra
    extra = 1 

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty ItemOrder forms to display
    fields = ['item', 'selected_extras']  # Display item and selected extras
    filter_horizontal = ('selected_extras',)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id','user__username')
    search_fields = ['name']
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'inHold')
    list_filter = ('category', 'inHold')
    search_fields = ('name',)
    filter_horizontal = ('extras',) 
class orderItemAdmin(admin.ModelAdmin):
    inlines=[OrderItemExtraInline]
    search_fields = ['order__customer__name']
    # list_display=['item','quantity','price']
    list_display = ('id', 'item__name')

    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Save the OrderItem to recalculate total price with selected extras
        order_item = form.instance
        order_item.save()  # Recalculate price based on extras

class ExtraAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'inHold')
    search_fields = ('name',)

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'ordered_at','order_status')
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Recalculate each OrderItem price and update Order's total amount
        order = form.instance
        for order_item in order.orderitem_set.all():
            order_item.save()
        
        # Recalculate and save Order total amount
        order.total_amount = order.calculate_total_amount()
        order.save(update_fields=["total_amount"])

admin.site.register(OrderItem,orderItemAdmin)
admin.site.register(Item,ItemAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(Customer,CustomerAdmin)
admin.site.register(Inventory)
admin.site.register(Category)
admin.site.register(Staff)
admin.site.register(OrderStatus)
admin.site.register(DeliveryDetail)
admin.site.register(Discount)
admin.site.register(Reservation)
admin.site.register(Supplier)
admin.site.register(Extra,ExtraAdmin)
admin.site.register(OrderItemExtra)
admin.site.register(Table)