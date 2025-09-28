from django.db import models
from PIL import Image
from django.core.exceptions import ValidationError

class Table(models.Model):
    TABLE_STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance')
    ]

    number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField(default=4)
    status = models.CharField(max_length=20, choices=TABLE_STATUS_CHOICES, default='available')
    qr_code = models.ImageField(upload_to='table_qr_codes/', null=True, blank=True)
    section = models.CharField(max_length=50, default='Main', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    inHold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.id}  {self.number} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # The validation should only run when a new file is uploaded.
        # A newly uploaded file will have a 'content_type' attribute,
        # while a file read from storage will not.
        if self.qr_code and hasattr(self.qr_code.file, 'content_type'):
            try:
                # Open the image from the uploaded file to verify it
                self.qr_code.file.seek(0)
                img = Image.open(self.qr_code.file)
                img.verify()
            except Exception:
                # If the file is not a valid image, raise a validation error.
                raise ValidationError("The uploaded QR code is not a valid image.")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['number']

class Reservation(models.Model):
    customer = models.ForeignKey('users.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    reservation_date = models.DateTimeField()
    number_of_guests = models.IntegerField()
    status = models.CharField(max_length=100)  # 'confirmed', 'canceled'
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"Reservation for {self.number_of_guests} on {self.reservation_date}"
