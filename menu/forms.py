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

    def save(self, commit=True):
        """
        Override the save method to add custom functionality
        when the form is saved.
        """
        # Get the instance from the parent save method
        instance = super().save(commit=False)

        # Add your custom logic here
        # For example, you could modify fields before saving:
        # instance.name = instance.name.title()  # Capitalize the name

        if commit:
            # Save the instance to the database
            instance.save()
            # Save many-to-many relationships if needed
            self.save_m2m()

        return instance
