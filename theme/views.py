from django.shortcuts import render, redirect
from core.decorators import staff_member_required
from django.contrib import messages
from .models import Branding
from .forms import BrandingForm

@staff_member_required
def edit_branding(request):
    print("--- Entering edit_branding view ---")
    branding, created = Branding.objects.get_or_create(id=1, defaults={'name': 'Default'})

    if created:
        print("New branding object created. Setting default colors.")
        branding.primary_color = '#d54b27'
        branding.secondary_color = '#ffa012'
        branding.save()

    if request.method == 'POST':
        print("--- POST request detected ---")
        form = BrandingForm(request.POST, request.FILES, instance=branding)
        if form.is_valid():
            print("Form is valid. Saving form.")
            form.save()
            print(f"Saved primary_color: {branding.primary_color}")
            messages.success(request, 'Branding updated successfully!')
            return redirect('edit_branding')
        else:
            print("Form is invalid. Errors:", form.errors)
    else:
        print("--- GET request detected ---")
        form = BrandingForm(instance=branding)
        print(f"Loading form with primary_color: {branding.primary_color}")

    return render(request, 'theme/edit_branding.html', {'form': form})
