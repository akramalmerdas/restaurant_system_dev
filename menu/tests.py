from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Item, Category
from users.models import Staff

class ItemCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='staffuser', password='password')
        self.staff = Staff.objects.create(user=self.user, role='admin')
        self.client.login(username='staffuser', password='password')
        self.category = Category.objects.create(name='Test Category')
        self.item = Item.objects.create(
            name='Test Item',
            category=self.category,
            price=10.00,
            created_by=self.user
        )

    def test_item_create_view(self):
        """
        Test that an item can be created via the form.
        """
        response = self.client.post(reverse('menu:item_create'), {
            'name': 'New Item',
            'category': self.category.id,
            'price': 15.00,
        })
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.assertTrue(Item.objects.filter(name='New Item').exists())

    def test_item_update_view(self):
        """
        Test that an item can be updated via the form.
        """
        response = self.client.post(reverse('menu:item_update', args=[self.item.id]), {
            'name': 'Updated Item',
            'category': self.category.id,
            'price': 20.00,
        })
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Updated Item')

    def test_item_delete_view(self):
        """
        Test that an item can be soft-deleted.
        """
        response = self.client.post(reverse('menu:item_delete', args=[self.item.id]))
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.item.refresh_from_db()
        self.assertTrue(self.item.inHold)

    def test_item_dashboard_view(self):
        """
        Test that the item dashboard can be accessed.
        """
        response = self.client.get(reverse('menu:item_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.name)
