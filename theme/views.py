from django.shortcuts import render, redirect
from core.decorators import staff_member_required
from django.contrib import messages
from .models import Branding
from .forms import BrandingForm

@staff_member_required
def edit_branding(request):
    branding, created = Branding.objects.get_or_create(id=1, defaults={'name': 'Default'})
    if request.method == 'POST':
        form = BrandingForm(request.POST, request.FILES, instance=branding)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branding updated successfully!')
            return redirect('edit_branding')
    else:
        form = BrandingForm(instance=branding)

    return render(request, 'theme/edit_branding.html', {'form': form})
