from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class OrderStatus(models.Model):
    statues=[
        ('readytoprint', 'Ready to Print'),
        ('printed', 'Printed'),
        ('printing', 'Printing'),
        ('completed','Completed'),
        ('pending','Pending'),
        ('delivered','Delivered'),
        ('served','Served')
    ]
    name = models.CharField(max_length=100, choices=statues, default='readytoprint')
    description = models.TextField(null=True, blank=True)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Order Status'

class Order(models.Model):
    customer = models.ForeignKey('users.Customer', on_delete=models.CASCADE, null=True, blank=True)
    ordered_at = models.DateTimeField(default=timezone.now)
    printed_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    served_at = models.DateTimeField(null=True, blank=True)
    delivery_address = models.TextField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    special_instructions = models.TextField(null=True, blank=True)
    inHold = models.BooleanField(default=False)
    table = models.ForeignKey('reservations.Table', on_delete=models.SET_NULL, null=True, blank=True)
    table_number = models.CharField(default='Take Away', max_length=50)
    deleted_by = models.ForeignKey(User, related_name='new_deleted_orders', on_delete=models.SET_NULL, null=True, blank=True)
    deleted_reason = models.TextField(null=True, blank=True)
    waiter = models.ForeignKey('users.Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_taken')
    display_id = models.CharField(max_length=20, blank=True, null=True)
    previous_table = models.TextField(null=True, blank=True)

    def calculate_total_amount(self):
        if not self.pk:
            return 0
        else:
            return sum(item.price for item in self.orderitem_set.all())

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total_amount()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey('menu.Item', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    item_name = models.CharField(max_length=255, null=True)
    item_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    customizations = models.TextField(null=True, blank=True)
    selected_extras = models.ManyToManyField('menu.Extra', blank=True)
    invoice = models.ForeignKey('payments.Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    inHold = models.BooleanField(default=False)

    def calculate_total_price(self):
        base_price = self.item.price
        extras_price = sum(extra.calculate_price() for extra in self.orderitemextra_set.all())
        return base_price + extras_price

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.item.price
        super().save(*args, **kwargs)

        if self.pk:
            self.price = self.calculate_total_price()
        super().save(*args, update_fields=['price'])

    def __str__(self):
        return f"{self.item.name}"

class OrderItemExtra(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    extra = models.ForeignKey('menu.Extra', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    extra_name = models.CharField(max_length=255, null=True)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def calculate_price(self):
        return self.extra.price * self.quantity

class DailyOrderCounter(models.Model):
    date = models.DateField(unique=True)
    counter = models.IntegerField(default=0)

class Discount(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    discount_code = models.CharField(max_length=50)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"Discount {self.discount_code} for Order {self.order.id}"
