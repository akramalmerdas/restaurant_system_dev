from django.contrib import admin
from .models import Table, Reservation

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'status', 'section')
    list_filter = ('status', 'section')
    search_fields = ('number',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'reservation_date', 'number_of_guests', 'status')
    list_filter = ('status', 'reservation_date')
    search_fields = ('customer__user__username',)
