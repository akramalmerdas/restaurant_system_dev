from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum

class Invoice(models.Model):
    INVOICE_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("partial", "Partial Payment")
    ]
    table = models.ForeignKey('reservations.Table', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default="pending")
    inHold = models.BooleanField(default=False)
    display_id = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice #{self.id} for Table {self.table.number}"

    @property
    def amount_paid(self):
        result = self.payments.filter(inHold=False).aggregate(total=Sum("amount"))
        return result["total"] or Decimal("0.00")

    @property
    def balance_due(self):
        return max(Decimal("0.00"), self.total_amount - self.amount_paid)

    @property
    def is_fully_paid(self):
        return self.balance_due <= 0

    def update_payment_status(self):
        if self.is_fully_paid:
            self.is_paid = True
            self.status = "paid"
        elif self.amount_paid > Decimal("0.00"):
            self.is_paid = False
            self.status = "partial"
        else:
            self.is_paid = False
            self.status = "pending"
        self.save(update_fields=["is_paid", "status"])

class Payment(models.Model):
    PAYMENT_METHODS = [
        ("CASH", "Cash"),
        ("BANK", "Bank Transfer"),
        ("MOMO", "Momo"),
        ("CARD", "Card"),
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
        self.invoice.update_payment_status()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.update_payment_status()

class UnpaidReasonLog(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
