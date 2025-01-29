import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MochaCafe.settings')  

from django.utils.timezone import now
import django
import webbrowser

django.setup()
from item.models import Order, OrderStatus

class PrintOrders:
    def __init__(self):
        self.base_url = "http://localhost:8000/print_order_view/"  # Replace with your actual server URL

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

    # def update_order_status(self, order):
    #     """Update the order status to 'printed'."""
    #     try:
    #         printed_status = OrderStatus.objects.get(name="printed")
    #         order.order_status = printed_status
    #         order.save()
    #         print(f"Updated status to 'printed' for Order ID: {order.id}")
    #     except Exception as e:
    #         print(f"Failed to update status for Order ID {order.id}: {e}")

    def run(self):
        """Fetch, print, and update orders."""
        orders = self.fetch_orders()
        if not orders:
            print("No orders ready to print.")
            return

        for order in orders:

            print(f"Processing Order ID: {order.id}")
            self.print_order(order)
            # self.update_order_status(order)

if __name__ == "__main__":
    try:
        printer_service = PrintOrders()
        printer_service.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
