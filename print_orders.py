import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MochaCafe.settings')  

import django
import webbrowser

django.setup()

from item.models import Order, OrderStatus


class PrintOrders:
    def __init__(self):
        self.base_url = "http://localhost:8000/orders/print_order_view/"  # Adjust if needed

    def fetch_orders(self):
        """Fetch all orders with 'readytoprint' status."""
        return Order.objects.filter(order_status__name="readytoprint")

    def print_order(self, order):
        """Open the order's print page in the browser."""
        try:
            print_url = f"{self.base_url}{order.id}/"
            webbrowser.open(print_url)
            print(f"Opened print page for Order ID: {order.id}")
        except Exception as e:
            print(f"Failed to open print page for Order ID {order.id}: {e}")

    def update_order_status_to_printing(self, order):
        """Update the order status to 'printing'."""
        try:
            printing_status = OrderStatus.objects.get(name="printing")
            order.order_status = printing_status
            order.save()
            print(f"Updated status to 'printing' for Order ID: {order.id}")
        except Exception as e:
            print(f"Failed to update status for Order ID {order.id}: {e}")

    def run(self):
        """Fetch, print, and update orders."""
        orders = self.fetch_orders()
        if not orders:
            print("No orders ready to print.")
            return

        for order in orders:
            print(f"Processing Order ID: {order.id}")
            self.print_order(order)
            self.update_order_status_to_printing(order)


if __name__ == "__main__":
    try:
        printer_service = PrintOrders()
        printer_service.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
