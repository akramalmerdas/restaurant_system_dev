from .models import RestaurantConfig

def restaurant_config(request):
    """
    Adds the restaurant configuration to the context.
    """
    config, created = RestaurantConfig.objects.get_or_create(pk=1)
    return {'restaurant_config': config}
