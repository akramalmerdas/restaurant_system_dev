from django.db import models
from menu.models import Item

# Inventory Model
class Inventory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity_in_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_quantity = models.IntegerField(null=True, blank=True)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return self.item.name

# Supplier Model
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return self.name
