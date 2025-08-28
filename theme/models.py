from django.db import models
from colorfield.fields import ColorField

class Branding(models.Model):
    name = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='logos/')
    slogan = models.CharField(max_length=255, blank=True)
    primary_color = ColorField(default='#FFFFFF')
    secondary_color = ColorField(default='#000000')

    def __str__(self):
        return self.name
