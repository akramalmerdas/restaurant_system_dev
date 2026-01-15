import time
import webbrowser
from django.core.management.base import BaseCommand
from orders.models import Order, OrderStatus


class Command(BaseCommand):
    help = 'Continuously check for orders ready to print'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=10,
            help='Check interval in seconds (default: 10)',
        )

    def handle(self, *args, **options):
        interval = options['interval']
        base_url = "http://localhost:8000/orders/print_order_view/"
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting print service (checking every {interval} seconds)')
        )
        
        while True:
            try:
                # Fetch orders ready to print
                orders = Order.objects.filter(order_status__name="readytoprint")
                
                if orders.exists():
                    for order in orders:
                        self.stdout.write(f"Processing Order ID: {order.id}")
                        
                        # Open print page
                        try:
                            print_url = f"{base_url}{order.id}/"
                            webbrowser.open(print_url)
                            self.stdout.write(f"Opened print page for Order ID: {order.id}")
                            
                            # Update status to printing
                            printing_status = OrderStatus.objects.get(name="printing")
                            order.order_status = printing_status
                            order.save()
                            self.stdout.write(f"Updated status to 'printing' for Order ID: {order.id}")
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"Failed to process Order ID {order.id}: {e}")
                            )
                else:
                    self.stdout.write("No orders ready to print.")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error in print service: {e}")
                )
            
            # Wait before next check
            time.sleep(interval)