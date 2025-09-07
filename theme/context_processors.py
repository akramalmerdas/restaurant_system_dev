from .models import Branding

def branding_context(request):
    try:
        branding = Branding.objects.get(is_active=True)
    except Branding.DoesNotExist:
        branding = None
    return {'branding': branding}
