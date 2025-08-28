from django.shortcuts import render, redirect
from .forms import RestaurantConfigForm
from .models import RestaurantConfig
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def edit_branding(request):
    config, created = RestaurantConfig.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = RestaurantConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('branding:edit_branding')
    else:
        form = RestaurantConfigForm(instance=config)
    return render(request, 'branding/edit_branding.html', {'form': form})
