from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = 'Resets the primary key sequence for all tables in the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Attempting to reset all primary key sequences..."))

        all_models = apps.get_models()

        with connection.cursor() as cursor:
            for model in all_models:
                table_name = model._meta.db_table

                # Skip models that are not managed by Django's migration framework
                if not model._meta.managed:
                    self.stdout.write(self.style.NOTICE(f"Skipping unmanaged model: {table_name}"))
                    continue

                # Skip models that don't have an 'id' field
                if 'id' not in [field.name for field in model._meta.fields]:
                    self.stdout.write(self.style.NOTICE(f"Skipping model without 'id' field: {table_name}"))
                    continue

                self.stdout.write(f"Processing table: {table_name}")

                # Construct the SQL command
                sql = f"""
                SELECT setval(
                    pg_get_serial_sequence('"{table_name}"', 'id'),
                    COALESCE((SELECT MAX(id) + 1 FROM "{table_name}"), 1),
                    false
                );
                """

                try:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f"  -> Successfully reset sequence for table: {table_name}"))
                except Exception as e:
                    # This can fail if the table doesn't have a sequence (e.g., proxy models, some m2m tables)
                    # or if the table name is incorrect, which shouldn't happen here.
                    self.stdout.write(self.style.ERROR(f"  -> Could not reset sequence for table: {table_name}. Reason: {e}"))

        self.stdout.write(self.style.SUCCESS("Finished resetting sequences."))
