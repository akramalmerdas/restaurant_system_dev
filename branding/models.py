from django.db import models

class RestaurantConfig(models.Model):
    name = models.CharField(max_length=255, default="Mocah Cafe")
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    slogan = models.CharField(max_length=255, default="Memories of joy and happiness.")
    primary_color = models.CharField(max_length=7, default='#FF5733')
    secondary_color = models.CharField(max_length=7, default='#33FF57')

    def __str__(self):
        return self.name
