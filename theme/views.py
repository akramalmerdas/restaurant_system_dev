from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import staff_member_required
from django.contrib import messages
from .models import Branding
from .forms import BrandingForm

@staff_member_required
def manage_branding(request):
    branding_profiles = Branding.objects.all()
    return render(request, 'theme/manage_branding.html', {'branding_profiles': branding_profiles})

@staff_member_required
def create_branding(request):
    if request.method == 'POST':
        form = BrandingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branding profile created successfully!')
            return redirect('theme:manage_branding')
    else:
        form = BrandingForm()
    return render(request, 'theme/branding_form.html', {'form': form})

@staff_member_required
def edit_branding(request, profile_id=None):
    if profile_id:
        branding = get_object_or_404(Branding, id=profile_id)
    else:
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
            return redirect('theme:manage_branding')
    else:
        form = BrandingForm(instance=branding)

    return render(request, 'theme/branding_form.html', {'form': form, 'branding': branding})

@staff_member_required
def delete_branding(request, profile_id):
    branding = get_object_or_404(Branding, id=profile_id)
    if branding.is_active:
        messages.error(request, 'Cannot delete an active branding profile.')
    elif branding.is_default_profile:
        messages.error(request, 'Cannot delete the default branding profile.')
    else:
        branding.delete()
        messages.success(request, 'Branding profile deleted successfully!')
    return redirect('theme:manage_branding')

@staff_member_required
def set_active_branding(request, profile_id):
    branding = get_object_or_404(Branding, id=profile_id)
    branding.is_active = True
    branding.save()
    messages.success(request, f'Branding profile "{branding.name}" has been set as active.')
    return redirect('theme:manage_branding')

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
