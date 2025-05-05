# from django.core.management.base import BaseCommand
# from faker import Faker
# from item.models import Table
# import qrcode
# from io import BytesIO
# from django.core.files.base import ContentFile

# class Command(BaseCommand):
#     help = 'Populates the Table model with dummy data and generates QR codes'

#     def handle(self, *args, **kwargs):
#         fake = Faker()

#         for i in range(15):  # Adjust the range for the number of tables
#             table_number = f"T-{i+1}"  # Unique table number
#             table_capacity = fake.random_int(min=2, max=8)
#             table_status = fake.random_element(['available', 'occupied', 'reserved', 'maintenance'])
#             section = fake.random_element(['Main', 'Outdoor', 'VIP'])

#             # Use update_or_create instead of create
#             table, created = Table.objects.update_or_create(
#                 number=table_number,
#                 defaults={
#                     'capacity': table_capacity,
#                     'status': table_status,
#                     'section': section
#                     # Add other fields with default values if necessary
#                 }
#             )

#             if created:
#                 self.stdout.write(f"Table {table_number} created.")
#                 # Generate QR code only for newly created tables or if needed for updates
#                 qr = qrcode.QRCode(
#                     version=1,
#                     error_correction=qrcode.constants.ERROR_CORRECT_L,
#                     box_size=10,
#                     border=4,
#                 )
#                 # Ensure the URL is correct for your setup
#                 url = f"http://192.168.1.149:8000/?table_id={table.id}" # Use table.id for consistency
#                 qr.add_data(url)
#                 qr.make(fit=True)

#                 # Save QR code image to the table model
#                 qr_image = qr.make_image(fill_color="black", back_color="white")
#                 buffer = BytesIO()
#                 qr_image.save(buffer, format="PNG")
#                 # Use table.id in the filename for uniqueness if needed
#                 table.qr_code.save(f"table_{table.id}.png", ContentFile(buffer.getvalue()), save=True)
#                 self.stdout.write(self.style.SUCCESS(f"QR code generated and saved for Table {table_number}."))
#             else:
#                 self.stdout.write(f"Table {table_number} already exists. Skipping QR generation or updating as needed.")

#         self.stdout.write(self.style.SUCCESS("Finished table population."))
#         # --- End of commented-out table population section ---


# --- Item Population Section (Starts Here) ---
# Ensure necessary imports are at the top if combining logic
import random # Already likely imported if combining
from decimal import Decimal # Already imported above
from django.core.management.base import BaseCommand # Already imported above
from django.contrib.auth.models import User # Already imported above
from item.models import Item, Category, Extra, Table # Ensure all needed models are imported

class Command(BaseCommand): # Make sure there's only ONE Command class definition in the file
    help = 'Populates Items, Categories, Extras (and optionally Tables) in the database'

    def handle(self, *args, **kwargs):
        # --- Optional: Call table population logic here if desired ---
        # self.populate_tables() # Example: Refactor table logic into a method

        self.stdout.write("Starting item population with specified categories...")

        # --- 1. Get or Create Categories ---
        categories_data = [
            {'name': 'Break Fast', 'description': 'Morning meals to start your day.'},
            {'name': 'Extras', 'description': 'Side items or add-ons.'}, # Note: Distinct from the 'Extra' model for item modifications
            {'name': 'Cold Drinks', 'description': 'Refreshing cold beverages.'},
            {'name': 'Coffee and Tea', 'description': 'Hot and iced coffee and tea selections.'},
            {'name': 'Pancakes and crepes', 'description': 'Sweet and savory pancakes and crepes.'},
            {'name': 'Smoothie Bowls', 'description': 'Healthy and delicious smoothie bowls.'},
            {'name': 'Burgers', 'description': 'Classic and gourmet burgers.'},
            {'name': 'Pizza', 'description': 'Freshly baked pizzas.'},
            {'name': 'Soups', 'description': 'Warm and comforting soups.'},
            {'name': 'Sandwiches and wraps', 'description': 'Variety of sandwiches and wraps.'},
            {'name': 'Lunch', 'description': 'Midday meal options.'},
            {'name': 'Salads', 'description': 'Fresh and healthy salads.'},
        ]
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data.get('description', '')}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {category.name}"))
            else:
                self.stdout.write(f"Category already exists: {category.name}")


        # --- 2. Get or Create Extras (Model for item add-ons) ---
        extras_data = [
            {'name': 'Extra Espresso Shot', 'price': Decimal('1.50')},
            {'name': 'Soy Milk', 'price': Decimal('0.75')},
            {'name': 'Almond Milk', 'price': Decimal('0.75')},
            {'name': 'Oat Milk', 'price': Decimal('1.00')},
            {'name': 'Whipped Cream', 'price': Decimal('0.50')},
            {'name': 'Chocolate Syrup', 'price': Decimal('0.50')},
            {'name': 'Caramel Drizzle', 'price': Decimal('0.50')},
            {'name': 'Avocado', 'price': Decimal('2.00')},
            {'name': 'Bacon', 'price': Decimal('2.50')},
            {'name': 'Cheese Slice', 'price': Decimal('1.00')},
            {'name': 'Side Salad', 'price': Decimal('3.00')},
            {'name': 'Fries', 'price': Decimal('3.50')},
        ]
        extras = {}
        for extra_data in extras_data:
            extra, created = Extra.objects.get_or_create(
                name=extra_data['name'],
                defaults={'price': extra_data['price']}
            )
            extras[extra_data['name']] = extra
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created extra add-on: {extra.name}"))
            else:
                self.stdout.write(f"Extra add-on already exists: {extra.name}")


        # --- 3. Get Default User ---
        # ... (user fetching logic remains the same) ...
        try:
            default_user = User.objects.get(id=1)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Default user with ID 1 not found. Please create an admin user first."))
            return


        # --- 4. Define Menu Items ---
        # ... (menu items data remains the same) ...
        menu_items_data = [
            # Coffee and Tea
            {'name': 'Espresso', 'category': 'Coffee and Tea', 'price': Decimal('3.00'), 'description': 'A single shot of intense coffee.'},
            {'name': 'Americano', 'category': 'Coffee and Tea', 'price': Decimal('3.50'), 'description': 'Espresso diluted with hot water.'},
            {'name': 'Cappuccino', 'category': 'Coffee and Tea', 'price': Decimal('4.50'), 'description': 'Espresso with steamed milk and a deep layer of foam.', 'available_extras': ['Extra Espresso Shot', 'Soy Milk', 'Almond Milk', 'Oat Milk']},
            {'name': 'Latte', 'category': 'Coffee and Tea', 'price': Decimal('4.50'), 'description': 'Espresso with steamed milk and a light layer of foam.', 'available_extras': ['Extra Espresso Shot', 'Soy Milk', 'Almond Milk', 'Oat Milk', 'Chocolate Syrup', 'Caramel Drizzle']},
            {'name': 'Mocha', 'category': 'Coffee and Tea', 'price': Decimal('5.00'), 'description': 'Espresso with chocolate syrup and steamed milk.', 'available_extras': ['Extra Espresso Shot', 'Soy Milk', 'Almond Milk', 'Oat Milk', 'Whipped Cream']},
            {'name': 'Black Tea', 'category': 'Coffee and Tea', 'price': Decimal('3.00'), 'description': 'Classic hot black tea.'},
            {'name': 'Green Tea', 'category': 'Coffee and Tea', 'price': Decimal('3.00'), 'description': 'Refreshing hot green tea.'},
            {'name': 'Cold Brew', 'category': 'Coffee and Tea', 'price': Decimal('4.75'), 'description': 'Coffee brewed cold for a smoother, less acidic taste.'},

            # Cold Drinks
            {'name': 'Iced Americano', 'category': 'Cold Drinks', 'price': Decimal('4.00'), 'description': 'Espresso shots topped with cold water and served over ice.'},
            {'name': 'Iced Latte', 'category': 'Cold Drinks', 'price': Decimal('5.00'), 'description': 'Espresso and milk served over ice.', 'available_extras': ['Extra Espresso Shot', 'Soy Milk', 'Almond Milk', 'Oat Milk', 'Chocolate Syrup', 'Caramel Drizzle']},
            {'name': 'Iced Tea (Black)', 'category': 'Cold Drinks', 'price': Decimal('3.50'), 'description': 'Chilled black tea served over ice.'},
            {'name': 'Fresh Orange Juice', 'category': 'Cold Drinks', 'price': Decimal('4.50'), 'description': 'Squeezed fresh daily.'},
            {'name': 'Sparkling Water', 'category': 'Cold Drinks', 'price': Decimal('2.50'), 'description': 'Bottled sparkling water.'},

            # Break Fast
            {'name': 'Croissant', 'category': 'Break Fast', 'price': Decimal('3.50'), 'description': 'Flaky butter croissant.'},
            {'name': 'Muffin (Blueberry)', 'category': 'Break Fast', 'price': Decimal('3.00'), 'description': 'Moist blueberry muffin.'},
            {'name': 'Scone', 'category': 'Break Fast', 'price': Decimal('3.25'), 'description': 'Classic scone, perfect with jam.'},
            {'name': 'Full English Breakfast', 'category': 'Break Fast', 'price': Decimal('12.00'), 'description': 'Eggs, bacon, sausage, beans, tomato, mushroom, toast.', 'available_extras': ['Avocado']},
            {'name': 'Avocado Toast', 'category': 'Break Fast', 'price': Decimal('8.50'), 'description': 'Smashed avocado on sourdough toast.', 'available_extras': ['Bacon']},

            # Pancakes and crepes
            {'name': 'Classic Pancakes', 'category': 'Pancakes and crepes', 'price': Decimal('7.50'), 'description': 'Stack of fluffy pancakes with maple syrup.', 'available_extras': ['Whipped Cream', 'Chocolate Syrup', 'Caramel Drizzle']},
            {'name': 'Nutella Crepe', 'category': 'Pancakes and crepes', 'price': Decimal('8.00'), 'description': 'Thin crepe filled with Nutella.'},

            # Smoothie Bowls
            {'name': 'Acai Berry Bowl', 'category': 'Smoothie Bowls', 'price': Decimal('9.00'), 'description': 'Acai blend topped with granola, banana, and berries.'},
            {'name': 'Green Goddess Bowl', 'category': 'Smoothie Bowls', 'price': Decimal('9.50'), 'description': 'Spinach, kale, mango, banana blend topped with seeds and coconut.'},
            {'name': 'Strawberry Banana Bowl', 'category': 'Smoothie Bowls', 'price': Decimal('8.00'), 'description': 'Blend of strawberries, banana, yogurt, topped with granola.'},
            {'name': 'Mango Pineapple Bowl', 'category': 'Smoothie Bowls', 'price': Decimal('8.50'), 'description': 'Tropical blend of mango, pineapple, yogurt, topped with coconut flakes.'},

            # Sandwiches and wraps
            {'name': 'Turkey Club Sandwich', 'category': 'Sandwiches and wraps', 'price': Decimal('9.50'), 'description': 'Turkey, bacon, lettuce, tomato on toasted bread.', 'available_extras': ['Avocado', 'Cheese Slice', 'Fries']},
            {'name': 'Veggie Delight Wrap', 'category': 'Sandwiches and wraps', 'price': Decimal('8.00'), 'description': 'Hummus, cucumber, tomato, sprouts, and lettuce in a whole wheat wrap.', 'available_extras': ['Avocado', 'Fries']},
            {'name': 'Grilled Cheese Sandwich', 'category': 'Sandwiches and wraps', 'price': Decimal('7.00'), 'description': 'Classic cheddar grilled cheese.', 'available_extras': ['Bacon', 'Avocado', 'Fries']},
            {'name': 'Chicken Caesar Wrap', 'category': 'Sandwiches and wraps', 'price': Decimal('10.00'), 'description': 'Grilled chicken, romaine, parmesan, Caesar dressing in a wrap.', 'available_extras': ['Fries']},

            # Burgers
            {'name': 'Classic Beef Burger', 'category': 'Burgers', 'price': Decimal('11.00'), 'description': 'Beef patty, lettuce, tomato, onion, pickle on a bun.', 'available_extras': ['Cheese Slice', 'Bacon', 'Avocado', 'Fries']},
            {'name': 'Veggie Burger', 'category': 'Burgers', 'price': Decimal('10.50'), 'description': 'Plant-based patty, lettuce, tomato, onion, pickle on a bun.', 'available_extras': ['Cheese Slice', 'Avocado', 'Fries']},

            # Pizza
            {'name': 'Margherita Pizza (Personal)', 'category': 'Pizza', 'price': Decimal('10.00'), 'description': 'Tomato sauce, mozzarella, basil.'},
            {'name': 'Pepperoni Pizza (Personal)', 'category': 'Pizza', 'price': Decimal('11.50'), 'description': 'Tomato sauce, mozzarella, pepperoni.'},

            # Soups
            {'name': 'Tomato Soup', 'category': 'Soups', 'price': Decimal('5.50'), 'description': 'Creamy tomato soup served with croutons.'},
            {'name': 'Soup of the Day', 'category': 'Soups', 'price': Decimal('6.00'), 'description': 'Ask your server for today\'s special soup.'},

            # Salads
            {'name': 'Caesar Salad', 'category': 'Salads', 'price': Decimal('9.00'), 'description': 'Romaine lettuce, croutons, parmesan cheese, Caesar dressing.', 'available_extras': ['Bacon']},
            {'name': 'Greek Salad', 'category': 'Salads', 'price': Decimal('9.50'), 'description': 'Cucumber, tomato, olives, feta cheese, red onion, vinaigrette.'},

            # Lunch
            {'name': 'Chicken Pasta Alfredo', 'category': 'Lunch', 'price': Decimal('13.00'), 'description': 'Fettuccine pasta with grilled chicken in a creamy Alfredo sauce.'},
            {'name': 'Fish and Chips', 'category': 'Lunch', 'price': Decimal('14.00'), 'description': 'Battered fish fillet served with fries and tartar sauce.'},

            # Extras
            {'name': 'Side Fries', 'category': 'Extras', 'price': Decimal('3.50'), 'description': 'A side portion of crispy fries.'},
            {'name': 'Side Salad', 'category': 'Extras', 'price': Decimal('3.00'), 'description': 'A small mixed green salad.'},
        ]


        # --- 5. Populate Items ---
        # ... (item population loop remains the same) ...
        for item_data in menu_items_data:
            category_name = item_data['category']
            category_obj = categories.get(category_name)

            if not category_obj:
                self.stdout.write(self.style.WARNING(f"Category '{category_name}' not found for item '{item_data['name']}'. Skipping."))
                continue

            item, created = Item.objects.update_or_create(
                name=item_data['name'],
                defaults={
                    'category': category_obj,
                    'price': item_data['price'],
                    'description': item_data.get('description', ''),
                    'created_by': default_user,
                    'availability': item_data.get('availability', 'All Week'),
                    'inHold': False
                }
            )

            if 'available_extras' in item_data:
                item_extras = []
                for extra_name in item_data['available_extras']:
                    extra_obj = extras.get(extra_name)
                    if extra_obj:
                        item_extras.append(extra_obj)
                    else:
                         self.stdout.write(self.style.WARNING(f"Extra add-on '{extra_name}' not found for item '{item_data['name']}'. Skipping extra."))
                item.extras.set(item_extras)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created item: {item.name}"))
            else:
                self.stdout.write(f"Updated item: {item.name}")


        self.stdout.write(self.style.SUCCESS("Finished populating items with specified categories."))

