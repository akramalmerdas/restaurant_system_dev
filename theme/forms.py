from django import forms
from .models import Branding
from PIL import Image
from django.core.exceptions import ValidationError

class BrandingForm(forms.ModelForm):
    class Meta:
        model = Branding
        fields = '__all__'

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            try:
                # Open the image to verify it's a valid image file
                img = Image.open(logo)
                img.verify()
            except (IOError, SyntaxError) as e:
                raise ValidationError("The uploaded file is not a valid image.")
        return logo
