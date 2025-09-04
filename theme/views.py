from django.shortcuts import render, redirect
from core.decorators import staff_member_required
from django.contrib import messages
from .models import Branding
from .forms import BrandingForm

@staff_member_required
def edit_branding(request):
    branding, created = Branding.objects.get_or_create(id=1, defaults={'name': 'Default'})

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
        default_branding = Branding.objects.get(name='Default Settings')
        active_branding = Branding.objects.get(id=1)

        active_branding.primary_color = default_branding.primary_color
        active_branding.secondary_color = default_branding.secondary_color
        active_branding.slogan = default_branding.slogan
        active_branding.name = default_branding.name
        active_branding.logo = default_branding.logo
        active_branding.save()

        messages.success(request, 'Branding has been restored to the saved default.')
    except Branding.DoesNotExist:
        messages.error(request, "The 'Default Settings' profile has not been set up. Please create it in the admin dashboard.")

    return redirect('theme:edit_branding')
