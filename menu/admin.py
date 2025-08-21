from django.contrib import admin
from .models import Category, Item, Extra

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'inHold')
    list_filter = ('inHold',)
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'availability', 'inHold')
    list_filter = ('category', 'availability', 'inHold')
    search_fields = ('name', 'category__name')

@admin.register(Extra)
class ExtraAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'inHold')
    list_filter = ('inHold',)
    search_fields = ('name',)
