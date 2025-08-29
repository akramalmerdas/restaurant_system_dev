from django import forms
from .models import Branding

class BrandingForm(forms.ModelForm):
    class Meta:
        model = Branding
        fields = '__all__'
