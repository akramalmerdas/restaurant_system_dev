import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from menu.models import Item, Category
from orders.models import Order, OrderItem, OrderStatus
from reservations.models import Table
from users.models import Staff

class OrderCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='staffuser', password='password')
        self.staff = Staff.objects.create(user=self.user, role='waiter')
        self.client.login(username='staffuser', password='password')

        self.category = Category.objects.create(name='Test Category')
        self.item = Item.objects.create(name='Test Item', category=self.category, price=10.00, created_by=self.user)
        self.table = Table.objects.create(number='T1')
        OrderStatus.objects.create(name='pending')

    def test_add_to_order_view(self):
        """
        Test adding an item to the order session.
        """
        data = {
            'item_id': self.item.id,
            'quantity': 2,
            'table_number': self.table.number,
            'extras': [],
        }
        response = self.client.post(reverse('orders:add_to_order'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('order', self.client.session)
        self.assertEqual(len(self.client.session['order']), 1)

    def test_submit_order_view(self):
        """
        Test submitting an order from the session.
        """
        # First, add an item to the order session
        add_to_order_data = {
            'item_id': self.item.id,
            'quantity': 1,
            'table_number': self.table.number,
            'extras': [],
        }
        self.client.post(reverse('orders:add_to_order'), json.dumps(add_to_order_data), content_type='application/json')

        # Set table number in session, as submitOrder view requires it
        session = self.client.session
        session['table_number'] = self.table.number
        session.save()

        # Now, submit the order
        response = self.client.post(reverse('orders:submit_order'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        # Check that the order was created in the database
        self.assertTrue(Order.objects.exists())
        order = Order.objects.first()
        self.assertEqual(order.orderitem_set.count(), 1)
        self.assertEqual(order.order_status.name, 'pending')

    def test_order_detail_view(self):
        """
        Test viewing an order's detail page.
        """
        # First, create an order by adding to session and submitting
        add_to_order_data = {
            'item_id': self.item.id,
            'quantity': 1,
            'table_number': self.table.number,
            'extras': [],
        }
        self.client.post(reverse('orders:add_to_order'), json.dumps(add_to_order_data), content_type='application/json')

        session = self.client.session
        session['table_number'] = self.table.number
        session.save()

        self.client.post(reverse('orders:submit_order'))
        order = Order.objects.first()

        # Now, view the order
        response = self.client.get(reverse('orders:orderView', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.name)
