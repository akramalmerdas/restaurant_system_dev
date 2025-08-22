from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.name}"

class Item(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='items', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='Item_Images')
    availability = models.CharField(default='All Week', max_length=100)
    inHold = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='new_menu_items', on_delete=models.CASCADE, default=1)
    extras = models.ManyToManyField('Extra', blank=True, related_name='items')

    def __str__(self):
        return self.name

class Extra(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"
