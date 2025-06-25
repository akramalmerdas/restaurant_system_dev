# your_app/management/commands/populate_menu.py
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from item.models import Category, Item, Extra, User

class Command(BaseCommand):
    help = 'Populates the database with Mocha Cafe menu items'
    
    def handle(self, *args, **options):
        self.stdout.write("Starting database population...")
        self.create_categories_and_items()
        self.stdout.write(self.style.SUCCESS("Successfully populated database with menu items!"))
    
    def convert_price(self, price_str):
        """Convert price string like '13K' to Decimal (13000.00)"""
        try:
            clean_str = price_str.replace('K', '').replace('+', '').replace('RWF', '').strip()
            if '-' in clean_str:
                clean_str = clean_str.split('-')[0]
            return Decimal(clean_str) * 1000
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Price conversion error for '{price_str}': {str(e)}"))
            return Decimal('0.00')
    
    def create_categories_and_items(self):
        # Get or create default user
        user, created = User.objects.get_or_create(
            id=1,
            defaults={
                'username': 'admin', 
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            user.set_password('adminpassword')
            user.save()
        
        # PASTE YOUR FULL 145-ITEM DICTIONARY HERE
        mocha_menu =  {
    # "Breakfast": [
    #     {"name": "Mocha Arabic Plate", "price": "13K", "description": "Crispy falafel, hummus, labneh, salad, kofta with choice of eggs"},
    #     {"name": "English Breakfast", "price": "13K", "description": "Beans, eggs, mushrooms, onions, salad, pita/bread with kofta or chicken"},
    #     {"name": "Shakshuka", "price": "6.5K", "description": "Poached eggs in spicy tomato sauce with peppers/onions, pita bread"},
    #     {"name": "Fasoulia Pot", "price": "8K", "description": "White bean stew cooked in clay pot"},
    #     {"name": "Plain Omelette", "price": "5.5K", "description": "Served with pita bread"},    
    # ],
    # "Smoothie Bowls": [
    #     {"name": "Mango Bowl", "price": "9K", "description": "Mango smoothie bowl with fruits/seeds/oats"},
    #     {"name": "Pineapple Bowl", "price": "9K", "description": "Pineapple smoothie bowl with fruits/seeds/oats"},
    #     {"name": "Pineapple Banana Bowl", "price": "9K", "description": "Pineapple-banana smoothie bowl"},
    #     {"name": "Mango Banana Bowl", "price": "9K", "description": "Mango-banana smoothie bowl"},
    #     {"name": "Banana Peanut Bowl", "price": "9K", "description": "Banana-peanut smoothie bowl"},
    #     {"name": "Banana Peanut Chocolate Bowl", "price": "10K", "description": "Banana-peanut-chocolate smoothie bowl"},
    #     {"name": "Green Smoothie Bowl", "price": "10K", "description": "Healthy green smoothie bowl"},
    #     {"name": "Custom Smoothie Bowl", "price": "10K", "description": "Make-your-own smoothie bowl"}
    # ],
    # "Lunch": [
    #     {"name": "Chicken Zurbian", "price": "12K", "description": "Yemeni marinated chicken with rice/potatoes/spices"},
    #     {"name": "Bechamel Pasta", "price": "10K", "description": "Pasta with minced meat in creamy bechamel sauce"},
    #     {"name": "Kebda Pot", "price": "10K", "description": "Sautéed liver with onions/tomatoes in clay pot"},
    #     {"name": "Kofta with Tomato", "price": "10K", "description": "Meatballs in tomato sauce"},
    #     {"name": "Musaqaa", "price": "10K", "description": "Baked eggplant, onions, potato, minced meat"}
    # ],
    # "Pot": [
    #     {"name": "Adas (Lentil) Pot", "price": "9K", "description": "Spiced red lentils in clay pot with pita"},
    #     {"name": "Falafel Pot", "price": "9K", "description": "Falafel in tomato sauce with pita"},
    #     {"name": "Yemeni Fasoulia Pot", "price": "8K", "description": "Yemeni spiced beans with pita"},
    #     {"name": "Yemeni Foul Pot", "price": "8K", "description": "Fava beans in tomato sauce with pita"},
    #     {"name": "Shakshuka", "price": "6.5K", "description": "Eggs poached in tomato sauce with pita"},
    #     {"name": "Shakshuka with Chicken", "price": "11K", "description": "Shakshuka with added chicken"},
    #     {"name": "Shakshuka with Minced Meat", "price": "10K", "description": "Shakshuka with added minced meat"},
    #     {"name": "Daqqa Pot", "price": "8K", "description": "Slow-cooked minced meat with pita"}
    # ],
    # "Bowls": [
    #     {"name": "Falafel Bowl", "price": "9K", "description": "Salad, hummus, falafel, chickpeas with pita/rice"},
    #     {"name": "Hummus Bowl", "price": "7.5K", "description": "Salad, hummus, chickpeas, lentils with pita/rice"},
    #     {"name": "Chicken Bowl", "price": "11K", "description": "Grilled chicken, hummus, salad, chickpeas, avocado"},
    #     {"name": "Kofta Bowl", "price": "10K", "description": "Grilled kofta, salad, hummus, chickpeas, avocado"},
    # ],
    # "Yemeni Sweets": [
    #     {"name": "Yemeni Sosi", "price": "9K", "description": "Bread layered with eggs/milk, topped with honey"},
    #     {"name": "Tawa Fatta", "price": "6K", "description": "Tawa bread boiled in milk with butter/honey"},
    #     {"name": "Dates Fatta", "price": "8K", "description": "Shredded bread with dates, honey, seeds"},
    #     {"name": "Masoub", "price": "8K", "description": "Bananas, bread, milk with honey/seeds"}
    # ],
    # "Sandwiches": [
    #     {"name": "Omelette Wrap", "price": "5.5K", "description": "Omelette and hummus in chapati"},
    #     {"name": "Hummus Mushroom Wrap", "price": "7K", "description": "Hummus and mushrooms in chapati"},
    #     {"name": "Chicken Mushroom Wrap", "price": "8.5K", "description": "Chicken, hummus, mushrooms in chapati"},
    #     {"name": "Kofta Hummus Wrap", "price": "8K", "description": "Kofta and hummus in chapati"},
    #     {"name": "Omelette Pita Sandwich", "price": "5.5K", "description": "Omelette, veggies, hummus in pita"},
    #     {"name": "Veggie Pita Sandwich", "price": "5K", "description": "Lettuce, tomatoes, cucumbers, avocado in pita"},
    #     {"name": "Falafel Sandwich", "price": "6K", "description": "Falafel, hummus, veggies, garlic sauce"},
    #     {"name": "Chicken Shawarma", "price": "7.5K", "description": "Chicken shawarma with lettuce/pickles/white sauce"},
    #     {"name": "Chicken Pita Sandwich", "price": "8K", "description": "Grilled chicken, lettuce, tomatoes, onions in pita"},
    #     {"name": "Kofta Pita Sandwich", "price": "7.5K", "description": "Grilled kofta, lettuce, tomatoes, onions in pita"},
    #     {"name": "Omelette Baguette", "price": "6K", "description": "Omelette, veggies, garlic sauce in baguette"},
    #     {"name": "Chicken Baguette", "price": "9.5K", "description": "Grilled chicken, veggies, garlic sauce in baguette"},
    #     {"name": "Kofta Baguette", "price": "9K", "description": "Kofta, veggies, hummus in baguette"},
    #     {"name": "Falafel Baguette", "price": "9K", "description": "Falafel, veggies, hummus in baguette"},
    #     {"name": "Avocado Veggie Toast", "price": "5.5K", "description": "Hummus/labneh, avocado, tomato, lettuce on toast"},
    #     {"name": "Avocado Egg Toast", "price": "6.5K", "description": "Hummus/labneh, avocado, tomato, lettuce, egg on toast"},
    #     {"name": "Labneh, Strawberry & Honey Toast", "price": "7.5K", "description": "Labneh, strawberries, honey on toast"},
    #     {"name": "Labneh, Banana & Honey Toast", "price": "7K", "description": "Labneh, banana, honey on toast"},
    #     {"name": "Banana Peanut Chocolate Toast", "price": "8K", "description": "Peanut butter, banana, chocolate syrup on toast"}
    # ],
    # "Salads": [
    #     {"name": "Green Salad", "price": "5.5K", "description": "Lettuce, cucumbers, tomatoes with dressing"},
    #     {"name": "Avocado Salad", "price": "6.5K", "description": "Lettuce, cucumbers, tomatoes, avocado with dressing"},
    #     {"name": "Chickpeas Salad", "price": "8K", "description": "Chickpeas, lettuce, cucumbers, tomatoes, celery"},
    #     {"name": "Eggs Salad", "price": "8K", "description": "Boiled eggs, lettuce, cucumbers, tomatoes, celery"},
    #     {"name": "Chicken Salad", "price": "8.5K", "description": "Grilled chicken, celery, onions, lettuce, cucumbers"}
    # ],
    # "dips": [
    #     {"name": "Classic Labneh Plate", "price": "6K", "description": "Strained yogurt with tangy flavor"},
    #     {"name": "Labneh & Side Salad", "price": "7K", "description": "Labneh with fresh salad"},
    #     {"name": "Labneh & Omelette", "price": "8K", "description": "Labneh with omelette"},
    #     {"name": "Spiced Labneh with Garlic", "price": "7K", "description": "Labneh with garlic and tomato"},
    #     {"name": "Hummus Plate", "price": "5.5K", "description": "Chickpeas with tahini, olive oil, lemon"},
    #     {"name": "Hummus with Shakshuka", "price": "8K", "description": "Hummus served with shakshuka"},
    #     {"name": "Hummus with Chicken", "price": "9.5K", "description": "Hummus served with chicken"},
    #     {"name": "Hummus with Minced Meat", "price": "9K", "description": "Hummus served with minced meat"},
    #     {"name": "Hummus with Kebda", "price": "9K", "description": "Hummus served with liver"}
    # ],
    # "Soups": [
    #     {"name": "Veggie Soup", "price": "6.5K", "description": "Broth with seasonal vegetables"},
    #     {"name": "Vegan Soup", "price": "6.5K", "description": "Dairy-free vegetable soup"},
    #     {"name": "Lentil Soup", "price": "7K", "description": "Lentils and vegetables with herbs/spices"},
    #     {"name": "Chicken Soup", "price": "8K", "description": "Chicken and vegetables with herbs/spices"}
    # ],
    # "Pizza and Burgers": [
    #     {"name": "Margherita Pizza", "price": "9.5K", "description": "Classic cheese pizza"},
    #     {"name": "Chicken Pizza", "price": "12K", "description": "Pizza with chicken toppings"},
    #     {"name": "Veggie Burger", "price": "6K", "description": "Vegetable patty burger"},
    #     {"name": "Beef Burger", "price": "6K", "description": "Beef patty burger"},
    #     {"name": "Chicken Burger", "price": "7.5K", "description": "Chicken patty burger"}
    # ],

    # "Sweets": [
    #     {"name": "Tiramisu Cake", "price": "6K", "description": "Coffee-soaked ladyfingers with mascarpone"},
    #     {"name": "Chocolate Cake", "price": "5K", "description": "Rich chocolate dessert"},
    #     {"name": "Cheese Cake", "price": "5K", "description": "Creamy cheesecake with berry topping"},
    #     {"name": "Plain Pancake/Crepe", "price": "5K", "description": "Basic pancake/crepe"},
    #     {"name": "Pancake with Honey", "price": "6K", "description": "Pancake/crepe with honey"},
    #     {"name": "Pancake with Chocolate", "price": "7.5K", "description": "Pancake/crepe with chocolate"},
    #     {"name": "Pancake with Nutella", "price": "9K", "description": "Pancake/crepe with Nutella"},
    #     {"name": "Plain Zalabia", "price": "6K", "description": "Fried dough balls"},
    #     {"name": "Zalabia with Honey", "price": "7K", "description": "Fried dough with honey"},
    #     {"name": "Zalabia with Chocolate", "price": "8K", "description": "Fried dough with chocolate"},
    #     {"name": "Zalabia with Nutella", "price": "9K", "description": "Fried dough with Nutella"},
    # ],
    "Side Orders": [
        {"name": "Chicken Breast", "price": "5K", "description": "Extra Chicken Breast"},
        {"name": "Boild Eggs", "price": "1.5K", "description": "Extra Boild Eggs"},
        {"name": "Cheese", "price": "1.5K", "description": "Extra cheese"},
        {"name": "Veggies", "price": "0.5K", "description": "Extra veggies with the omelette"},
        {"name": "Veggies and Spinach", "price": "1.5K", "description": "Extra veggies and spincah with the omelette"},
        # {"name": "French Fries", "price": "3.5K", "description": "Side of fries"},
        # {"name": "Cheesy French Fries", "price": "5.5K", "description": "Fries with cheese"},
        # {"name": "Extra Chicken/Meat", "price": "5K", "description": "Additional protein"},
        # {"name": "Extra Egg", "price": "1.5K", "description": "Additional egg"},
        # {"name": "Extra Kofta", "price": "4K", "description": "Additional kofta"},
        # {"name": "Plain Falafel Side", "price": "6K", "description": "Side of falafel"},
        # {"name": "Extra Honey", "price": "1.5K", "description": "Additional honey"}
    ],
    # "Drinks": [
    #     {"name": "Sparkling Hibiscus (Glass)", "price": "4.5K", "description": "Refreshing hibiscus drink"},
    #     {"name": "Sparkling Hibiscus (1L)", "price": "9.5K", "description": "1L hibiscus drink"},
    #     {"name": "Virgin Mojito (Glass)", "price": "3.5K", "description": "Mint lime refresher"},
    #     {"name": "Virgin Mojito (1L)", "price": "9K", "description": "1L mojito"},
    #     {"name": "Sparkling Passion Mojito (Glass)", "price": "4.5K", "description": "Passion fruit mojito"},
    #     {"name": "Sparkling Passion Mojito (1L)", "price": "9.5K", "description": "1L passion mojito"},
    #     {"name": "Espresso", "price": "2.5K", "description": "Strong black coffee"},
    #     {"name": "Cappuccino/Latte", "price": "3K", "description": "Espresso with steamed milk"},
    #     {"name": "Americano", "price": "3K", "description": "Diluted espresso"},
    #     {"name": "Mocha Coffee", "price": "3.5K", "description": "Chocolate-flavored coffee"},
    #     {"name": "Turkish Coffee", "price": "3K", "description": "Traditional unfiltered coffee"},
    #     {"name": "African Coffee", "price": "3.5K", "description": "Spiced African-style coffee"},
    #     {"name": "Mango Juice", "price": "5K", "description": "Fresh mango juice"},
    #     {"name": "Pineapple Juice", "price": "5K", "description": "Fresh pineapple juice"},
    #     {"name": "Orange Juice", "price": "5K", "description": "Fresh orange juice"},
    #     {"name": "Lemon & Mint Juice", "price": "5K", "description": "Refreshing lemon-mint blend"},
    #     {"name": "Passion Fruit & Mint", "price": "5K", "description": "Tropical passion-mint juice"},
    #     {"name": "Vanilla Shake", "price": "4.5K", "description": "Creamy vanilla milkshake"},
    #     {"name": "Chocolate Shake", "price": "4.5K", "description": "Chocolate milkshake"},
    #     {"name": "Banana Vanilla Shake", "price": "4.5K", "description": "Banana-vanilla milkshake"},
    #     {"name": "Black Tea with Mint", "price": "2.5K", "description": "Tea with fresh mint"},
    #     {"name": "Green Tea", "price": "3K", "description": "Traditional green tea"},
    #     {"name": "Dawa Tea", "price": "4K", "description": "Ginger, lemon, honey tea"},
    #     {"name": "Hot Chocolate", "price": "3.5K", "description": "Creamy chocolate drink"},
    #     {"name": "Mango & Pineapple Smoothie", "price": "6K", "description": "Tropical fruit smoothie"},
    #     {"name": "Banana Peanut Smoothie", "price": "6.5K", "description": "Nutty banana smoothie"},
    #     {"name": "Soda", "price": "1.5K", "description": "Carbonated soft drink"},
    #     {"name": "Water", "price": "1.5K", "description": "Bottled water"},
    #     {"name": "Detox Water (1L)", "price": "2K", "description": "Infused detox water"}
    # ]
}
        
        # Create extras from side orders
        side_orders = mocha_menu.get("Side Orders", [])
        extras_mapping = {}
        
        for item in side_orders:
            # Create extra without description field
            extra, created = Extra.objects.get_or_create(
                name=item['name'],
                defaults={
                    'price': self.convert_price(item['price']),
                }
            )
            extras_mapping[item['name']] = extra
        
        # Process all categories and items
        for category_name, items in mocha_menu.items():
            if category_name == "Side Orders":
                continue
                
            category, _ = Category.objects.get_or_create(name=category_name)
            
            for item_data in items:
                # Create main item
                item = Item.objects.create(
                    name=item_data['name'],
                    category=category,
                    price=self.convert_price(item_data['price']),
                    description=item_data.get('description', ''),
                    created_by=user
                )
                
                # Add extras for items with add-ons
                if '+' in item_data['name']:
                    item_name_clean = item_data['name'].replace('+', '').strip()
                    if item_name_clean in extras_mapping:
                        item.extras.add(extras_mapping[item_name_clean])