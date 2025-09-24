from django import forms
from .models import Item, Category, Extra # Import necessary models
from PIL import Image
from django.core.exceptions import ValidationError

class ItemForm(forms.ModelForm):
    # Optional: Customize widgets or fields if needed
    extras = forms.ModelMultipleChoiceField(
        queryset=Extra.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(inHold=False),
        required=True
    )

    class Meta:
        model = Item
        fields = [
            'name',
            'category',
            'price',
            'description',
            'image',
            'availability',
            'extras',

        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            try:
                # Open the image to verify it's a valid image file
                img = Image.open(image)
                img.verify()
            except (IOError, SyntaxError) as e:
                raise ValidationError("The uploaded file is not a valid image.")
        return image
