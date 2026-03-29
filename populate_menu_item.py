import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MochaCafe.settings")  # adjust if needed
django.setup()

from orders.models import OrderStatus


STATUSES = [
    ("readytoprint", "Order ready to be printed", False),
    ("printing", "Order currently printing", False),
    ("printed", "Order printed successfully", False),
    ("pending", "Order waiting to be processed", True),
    ("completed", "Order completed", False),
    ("delivered", "Order delivered to customer", False),
    ("served", "Order served to table", False),
]


for name, description, hold in STATUSES:
    obj, created = OrderStatus.objects.get_or_create(
        name=name,
        defaults={
            "description": description,
            "inHold": hold
        }
    )

    if created:
        print(f"Created: {name}")
    else:
        print(f"Already exists: {name}")

print("Finished populating order statuses.")