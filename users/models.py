from django.db import models
from django.contrib.auth.models import User

class Staff(models.Model):
    ROLE_CHOICES = [
        ('chef', 'Chef'),
        ('waiter', 'Waiter'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
        ('cleaner', 'Cleaner'),
        ('barista', 'Barista'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    hire_date = models.DateField(auto_now_add=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loan = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"{full_name or self.user.username} - {self.role.capitalize()}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    loyalty_points = models.IntegerField(default=0)
    inHold = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"{full_name or self.user.username}"

    @property
    def total_debt(self):
        from payments.models import Invoice
        from decimal import Decimal

        total = Decimal('0.00')
        # We only consider invoices that are not fully paid
        for invoice in self.invoices.filter(is_paid=False):
            total += invoice.balance_due
        return total
