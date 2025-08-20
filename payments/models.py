from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Customer, Staff
from reservations.models import Table
from orders.models import Order
from decimal import Decimal
from django.db.models import Q, Sum, Avg, F, Count

class Invoice(models.Model):
    INVOICE_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("partial", "Partial Payment") # Added 'partial' status for clarity
    ]
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default="pending")
    inHold = models.BooleanField(default=False)
    display_id = models.CharField(max_length=20, blank=True, null=True)
    class Meta:
        # Add ordering for invoices, e.g., by creation date descending
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice #{self.id} for Table {self.table.number}"

    @property
    def amount_paid(self):
        """Calculates the total amount paid for this invoice from associated payments."""
        # Use .all() to ensure all related payments are considered
        result = self.payments.filter(inHold=False).aggregate(total=Sum("amount"))
        return result["total"] or Decimal("0.00")

    @property
    def balance_due(self):
        """Calculates the remaining balance due for the invoice."""
        return max(Decimal("0.00"), self.total_amount - self.amount_paid)

    @property
    def is_fully_paid(self):
        """Checks if the invoice is fully paid."""
        # Consider a small tolerance for floating point comparisons if necessary, though Decimal helps
        return self.balance_due <= 0

    def update_payment_status(self):
        """Updates the invoice's payment status based on the amount paid.
        This method should be called after any payment is made or updated.
        """
        if self.is_fully_paid:
            self.is_paid = True
            self.status = "paid"
        elif self.amount_paid > Decimal("0.00"):
            # If some amount is paid but not fully paid
            self.is_paid = False
            self.status = "partial"
        else:
            # No payments made yet
            self.is_paid = False
            self.status = "pending"
        # Ensure these fields are explicitly saved to the database
        self.save(update_fields=["is_paid", "status"])


class Payment(models.Model):
    PAYMENT_METHODS = [
        ("CASH", "Cash"),
        ("BANK", "Bank Transfer"),
        ("MOMO", "Momo"),
        ("CARD", "Card"), # Added 'CARD' method as it was in HTML but not in model
        ("OTHER", "Other")
    ]

    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    inHold = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment of {self.amount} via {self.get_method_display()} for Invoice #{self.invoice.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ensure invoice status is updated whenever a payment is saved
        self.invoice.update_payment_status()

    def delete(self, *args, **kwargs):
        # Get the invoice before deletion to update its status afterwards
        invoice = self.invoice
        super().delete(*args, **kwargs)
        # Ensure invoice status is updated whenever a payment is deleted
        invoice.update_payment_status()


class UnpaidReasonLog(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Discount(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    discount_code = models.CharField(max_length=50)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"Discount {self.discount_code} for Order {self.order.id}"
