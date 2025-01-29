from django.test import TestCase
from django.urls import reverse
from .models import Item, Category, Extra

# Model Tests
class ItemModelTestCase(TestCase):
    def setUp(self):
        # Create a category and extra for testing
        self.category = Category.objects.create(name='Beverages')
        self.extra = Extra.objects.create(name='Extra Shot', price=0.50)
        
        # Create an item
        self.item = Item.objects.create(
            name='Espresso',
            category=self.category,
            price=2.50
        )
        self.item.extras.add(self.extra)

    def test_item_creation(self):
        # Test item creation
        self.assertEqual(self.item.name, 'Espresso')
        self.assertEqual(self.item.category.name, 'Beverages')
        self.assertIn(self.extra, self.item.extras.all())

    def test_item_update(self):
        # Test item update
        self.item.price = 3.00
        self.item.save()
        self.assertEqual(self.item.price, 3.00)

    def test_item_deletion(self):
        # Test item deletion
        item_id = self.item.id
        self.item.delete()
        with self.assertRaises(Item.DoesNotExist):
            Item.objects.get(id=item_id)

    def test_item_string_representation(self):
        # Test the string representation of the item
        self.assertEqual(str(self.item), 'Espresso')

    def test_category_creation(self):
        # Test category creation
        self.assertEqual(self.category.name, 'Beverages')

    def test_category_update(self):
        # Test category update
        self.category.name = 'Food'
        self.category.save()
        self.assertEqual(self.category.name, 'Food')

    def test_category_deletion(self):
        # Test category deletion
        category_id = self.category.id
        self.category.delete()
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=category_id)

    def test_category_string_representation(self):
        # Test the string representation of the category
        self.assertEqual(str(self.category), 'Beverages')

    def test_extra_creation(self):
        # Test extra creation
        self.assertEqual(self.extra.name, 'Extra Shot')
        self.assertEqual(self.extra.price, 0.50)

    def test_extra_update(self):
        # Test extra update
        self.extra.price = 0.75
        self.extra.save()
        self.assertEqual(self.extra.price, 0.75)

    def test_extra_deletion(self):
        # Test extra deletion
        extra_id = self.extra.id
        self.extra.delete()
        with self.assertRaises(Extra.DoesNotExist):
            Extra.objects.get(id=extra_id)

    def test_extra_string_representation(self):
        # Test the string representation of the extra
        self.assertEqual(str(self.extra), 'Extra Shot')

# View Tests
class ItemViewTestCase(TestCase):
    def setUp(self):
        # Create a category and an item for testing
        self.category = Category.objects.create(name='Beverages')
        self.item = Item.objects.create(name='Espresso', category=self.category, price=2.50)

    def test_item_list_view(self):
        # Test the item list view
        response = self.client.get(reverse('item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_list.html')
        self.assertContains(response, 'Espresso')

    def test_item_detail_view(self):
        # Test the item detail view
        response = self.client.get(reverse('item_detail', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_detail.html')
        self.assertContains(response, 'Espresso')

    def test_item_create_view(self):
        # Test the item create view
        data = {
            'name': 'Cappuccino',
            'category': self.category.id,
            'price': 3.50
        }
        response = self.client.post(reverse('item_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(name='Cappuccino').exists())

    def test_item_update_view(self):
        # Test the item update view
        data = {
            'name': 'Latte',
            'category': self.category.id,
            'price': 3.00
        }
        response = self.client.post(reverse('item_update', args=[self.item.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(name='Latte').exists())

    def test_item_delete_view(self):
        # Test the item delete view
        response = self.client.post(reverse('item_delete', args=[self.item.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())