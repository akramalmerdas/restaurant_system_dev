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
        # When saving a Table, we only want to validate a new QR code image file.
        # An existing file path in the database might not correspond to a file on disk
        # in a development environment, which would cause a FileNotFoundError.
        if self.qr_code:
            try:
                # The hasattr check itself can trigger the FileNotFoundError if the file is missing.
                is_new_upload = hasattr(self.qr_code.file, 'content_type')
                if is_new_upload:
                    # This is a new file upload, so we should validate it.
                    self.qr_code.file.seek(0)
                    img = Image.open(self.qr_code.file)
                    img.verify()
            except FileNotFoundError:
                # The file doesn't exist on disk. This is acceptable in a dev environment
                # where the database might have paths to files that don't exist locally.
                # We pass silently to allow the save operation to continue.
                pass
            except Exception as e:
                # Any other exception during validation is a genuine error.
                raise ValidationError(f"The uploaded QR code is not a valid image: {e}")

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
