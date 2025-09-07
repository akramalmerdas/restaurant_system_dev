from django.shortcuts import render, redirect
from core.decorators import staff_member_required
from django.contrib import messages
from .models import Branding
from .forms import BrandingForm

@staff_member_required
def edit_branding(request):
    try:
        branding = Branding.objects.get(is_active=True)
    except Branding.DoesNotExist:
        # If no active branding profile exists, create one.
        # This is a fallback for the initial setup.
        branding, created = Branding.objects.get_or_create(id=1, defaults={'name': 'Default', 'is_active': True})
        if created:
            branding.primary_color = '#d54b27'
            branding.secondary_color = '#ffa012'
            branding.save()

    if request.method == 'POST':
        form = BrandingForm(request.POST, request.FILES, instance=branding)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branding updated successfully!')
            return redirect('theme:edit_branding')
    else:
        form = BrandingForm(instance=branding)

    return render(request, 'theme/edit_branding.html', {'form': form, 'branding': branding})

@staff_member_required
def restore_default_branding(request):
    try:
        default_branding = Branding.objects.get(is_default_profile=True)
        active_branding = Branding.objects.get(is_active=True)

        active_branding.primary_color = default_branding.primary_color
        active_branding.secondary_color = default_branding.secondary_color
        active_branding.slogan = default_branding.slogan
        # Do not copy the name
        # active_branding.name = default_branding.name
        active_branding.logo = default_branding.logo
        active_branding.save()

        messages.success(request, 'Branding has been restored to the saved default.')
    except Branding.DoesNotExist:
        messages.error(request, "A default or active branding profile has not been set. Please configure one in the admin dashboard.")

    return redirect('theme:edit_branding')
