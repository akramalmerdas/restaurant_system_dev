from django import forms
from .models import Item, Category, Extra # Import necessary models

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

