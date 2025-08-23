from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    This template tag is used to replace or add GET parameters to the current URL.
    It's perfect for pagination links that need to preserve filters.
    
    Usage in template:
    <a href="?{% url_replace page=page_obj.next_page_number %}">
    """
    # Start with a copy of the current GET parameters
    query = context['request'].GET.copy()
    
    # Update the copy with any new parameters passed to the tag
    for key, value in kwargs.items():
        query[key] = value
        
    # Return the URL-encoded string of the modified parameters
    return query.urlencode()
