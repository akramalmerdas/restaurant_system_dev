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

    @property
    def total_leave_days(self):
        total_days = 0
        for leave in self.leaves.all():
            total_days += (leave.end_date - leave.start_date).days + 1
        return total_days

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

class Loan(models.Model):
    REPAYMENT_STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('paid', 'Paid'),
    ]
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_issued = models.DateField(auto_now_add=True)
    repayment_status = models.CharField(max_length=20, choices=REPAYMENT_STATUS_CHOICES, default='ongoing')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Loan of {self.amount} for {self.staff.user.username} on {self.date_issued}"

class FinancialTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('loan', 'Loan'),
        ('deduction', 'Deduction'),
        ('repayment', 'Repayment'),
    ]
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='financial_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255)
    related_loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True, help_text="Link to the original loan if this is a repayment.")

    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} for {self.staff.user.username} on {self.date}"

class Leave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('sick', 'Sick Leave'),
        ('vacation', 'Vacation'),
        ('unpaid', 'Unpaid Leave'),
        ('other', 'Other'),
    ]
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    reason = models.TextField()
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return f"Leave for {self.staff.user.username} from {self.start_date} to {self.end_date}"
