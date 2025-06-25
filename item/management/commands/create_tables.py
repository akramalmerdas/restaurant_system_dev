import os
import qrcode
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from item.models import Table  # Replace 'your_app' with your actual app name


class Command(BaseCommand):
    help = 'Populate database with 14 tables and generate QR codes'

    def handle(self, *args, **options):
        # Define the base URL for QR codes
        base_url = "http://192.168.1.149:8000/?table_id="
        
        # Define the QR code storage path
        qr_code_storage_path = r"E:\Django\MochaSystem\MochaCafe\table_qr_codes"
        
        # Create the directory if it doesn't exist
        os.makedirs(qr_code_storage_path, exist_ok=True)
        
        # Table configurations
        table_configs = [
            {"number": "T-1", "capacity": 2, "section": "Main"},
            {"number": "T-2", "capacity": 4, "section": "Main"},
            {"number": "T-3", "capacity": 4, "section": "Main"},
            {"number": "T-4", "capacity": 6, "section": "Main"},
            {"number": "T-5", "capacity": 2, "section": "Outdoor"},
            {"number": "T-6", "capacity": 4, "section": "Outdoor"},
            {"number": "T-7", "capacity": 4, "section": "Outdoor"},
            {"number": "T-8", "capacity": 8, "section": "VIP"},
            {"number": "T-9", "capacity": 6, "section": "VIP"},
            {"number": "T-10", "capacity": 4, "section": "Main"},
            {"number": "T-11", "capacity": 2, "section": "Main"},
            {"number": "T-12", "capacity": 4, "section": "Outdoor"},
            {"number": "T-13", "capacity": 6, "section": "Main"},
            {"number": "T-14", "capacity": 8, "section": "VIP"},
        ]
        
        self.stdout.write("Starting to create tables and QR codes...")
        
        for config in table_configs:
            table_number = config["number"]
            
            # Check if table already exists
            if Table.objects.filter(number=table_number).exists():
                self.stdout.write(
                    self.style.WARNING(f'Table {table_number} already exists. Skipping...')
                )
                continue
            
            # Create QR code
            qr_url = f"{base_url}{table_number}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code to specified directory
            qr_filename = f"table_{table_number}_qr.png"
            qr_filepath = os.path.join(qr_code_storage_path, qr_filename)
            qr_image.save(qr_filepath)
            
            # Create table instance
            table = Table(
                number=table_number,
                capacity=config["capacity"],
                section=config["section"],
                status='available',
                is_active=True,
                inHold=False
            )
            
            # Open the saved QR code file and assign it to the model
            with open(qr_filepath, 'rb') as qr_file:
                table.qr_code.save(
                    qr_filename,
                    File(qr_file),
                    save=False
                )
            
            # Save the table
            table.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created table {table_number} with QR code')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created all tables! QR codes saved to: {qr_code_storage_path}')
        )
        
        # Display summary
        total_tables = Table.objects.count()
        self.stdout.write(f'Total tables in database: {total_tables}')
        
        # Display table distribution by section
        sections = Table.objects.values_list('section', flat=True).distinct()
        for section in sections:
            count = Table.objects.filter(section=section).count()
            self.stdout.write(f'{section} section: {count} tables')