from django.core.management.base import BaseCommand
from faker import Faker
from item.models import Table
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Populates the Table model with dummy data and generates QR codes'

    def handle(self, *args, **kwargs):
        fake = Faker()

        for i in range(15):  # Adjust the range for the number of tables
            table_number = f"T-{i+1}"  # Unique table number
            table_capacity = fake.random_int(min=2, max=8)
            table_status = fake.random_element(['available', 'occupied', 'reserved', 'maintenance'])
            section = fake.random_element(['Main', 'Outdoor', 'VIP'])

            # Create the table entry
            table = Table.objects.create(
                number=table_number,
                capacity=table_capacity,
                status=table_status,
                section=section
            )

            # Generate QR code for the table
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            url = f"http://192.168.1.149:8000/?table_id={table_number}"
            qr.add_data(url)
            qr.make(fit=True)

            # Save QR code image to the table model
            qr_image = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            qr_image.save(buffer, format="PNG")
            table.qr_code.save(f"table_{table_number}.png", ContentFile(buffer.getvalue()), save=True)

            self.stdout.write(self.style.SUCCESS(f"Table {table_number} created with QR code."))
