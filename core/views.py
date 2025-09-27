from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from menu.models import Item
from reservations.models import Table

def index(request):
    # Fetch table_id from the query parameter
    table_number = request.GET.get('table_id')
    table = None

    # If table_id is provided, fetch the table object
    if table_number:
        try:
            table = Table.objects.get(number=table_number)
            request.session['table_number'] = table_number
        except Table.DoesNotExist:
            table = None  # Handle invalid table_id gracefully

    # --- DIAGNOSTIC: Temporarily disable database queries ---
    # lunchItems = Item.objects.filter(category__id=3)
    # saladItems = Item.objects.filter(category__id=8)
    # drinks = Item.objects.filter(category__id=13)
    # sweets= Item.objects.filter(category__id=12)
    # breakFast = Item.objects.filter(category__id=1)
    # extras = Item.objects.filter(category__id=14)
    # yemeni_sweets = Item.objects.filter(category__id=6)
    # smoothie_bowls = Item.objects.filter(category__id=2)
    # burgers = Item.objects.filter(category__id=11)
    # dips = Item.objects.filter(category__id=9)
    # soups = Item.objects.filter(category__id=10)
    # sandwiches = Item.objects.filter(category__id=7)
    # pots = Item.objects.filter(category__id=4)
    # bowls = Item.objects.filter(category__id=5)

    # Pass the table object to the template
    return render(request, 'index.html', {
        'lunch': [],
        'salad': [],
        'drinks': [],
        'sweets': [],
        'breakFast': [],
        'extra': [],
        'yemeni_sweets': [],
        'smoothie_bowls': [],
        'burgers': [],
        'dips': [],
        'soups': [],
        'sandwiches': [],
        'pots': [],
        'bowls': [],
        'table': table,
    })
