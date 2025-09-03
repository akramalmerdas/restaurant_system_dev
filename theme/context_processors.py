from .models import Branding

def branding_context(request):
    # Consistently use the branding object with id=1
    branding = Branding.objects.filter(id=1).first()
    return {'branding': branding}
