from django import forms
from .models import RestaurantConfig

class RestaurantConfigForm(forms.ModelForm):
    class Meta:
        model = RestaurantConfig
        fields = ['name', 'logo', 'slogan', 'primary_color', 'secondary_color']
