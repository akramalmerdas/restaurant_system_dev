from .models import Branding

def branding_context(request):
    branding = Branding.objects.first()
    return {'branding': branding}
