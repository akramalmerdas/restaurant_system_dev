from django.db import models
from colorfield.fields import ColorField

class Branding(models.Model):
    name = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    slogan = models.CharField(max_length=255, blank=True, null=True)
    primary_color = ColorField(default='#FFFFFF', blank=True, null=True)
    secondary_color = ColorField(default='#000000', blank=True, null=True)
    is_default_profile = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_active:
            # Unset other active profiles
            Branding.objects.filter(is_active=True).update(is_active=False)
        super(Branding, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
