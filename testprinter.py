import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MochaCafe.settings')  

from django.utils.timezone import now
import django

django.setup()
from item.models import Order, OrderStatus

from escpos.printer import Usb

class PrintOrders:
    def __init__(self):
        self.printer = Usb(0x1FC9, 0x2016)  # Replace with your printer's USB vendor and product ID

    def fetch_orders(self):
        """Fetch all orders with 'readytoprint' status."""
        return Order.objects.filter(order_status__name="readytoprint")

    def print_order(self, order):
        """Send the order details to the printer."""
        try:
            self.printer.text("Mocha Mocha Cafe\n")
            self.printer.text(f"Order ID: {order.id}\n")
            self.printer.text(f"Date: {now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.printer.text("------------------------------------------\n")
            
            for item in order.orderitem_set.all():
                self.printer.text(f"{item.quantity} x {item.item.name} - {item.price} RWF\n")

            self.printer.text("------------------------------------------\n")
            self.printer.text(f"Total: {order.total_amount} RWF\n")
            self.printer.text("Thank you for visiting Mocha Mocha Cafe!\n")
            self.printer.cut()

        except Exception as e:
            print(f"Failed to print Order ID {order.id}: {e}")

    def update_order_status(self, order):
        """Update the order status to 'printed'."""
        try:
            printed_status = OrderStatus.objects.get(name="printed")
            order.order_status = printed_status
            order.save()
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
            self.update_order_status(order)

if __name__ == "__main__":
    try:
        printer_service = PrintOrders()
        printer_service.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")


