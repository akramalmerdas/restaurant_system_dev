from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from item.models import Staff, Order, OrderStatus, Table

class SecurityTests(TestCase):

    def setUp(self):
        # Create users
        self.staff_user = User.objects.create_user(username='staffuser', password='password')
        self.admin_user = User.objects.create_user(username='adminuser', password='password')
        self.normal_user = User.objects.create_user(username='normaluser', password='password')

        # Create staff members
        self.staff_member = Staff.objects.create(user=self.staff_user, role='waiter')
        self.admin_member = Staff.objects.create(user=self.admin_user, role='admin')

        # Create a client
        self.client = Client()

        # Create an order for testing deletion
        self.table = Table.objects.create(number='T1')
        self.status = OrderStatus.objects.create(name='pending')
        self.order = Order.objects.create(order_status=self.status, table=self.table)

    def test_admin_dashboard_unauthenticated_redirect(self):
        """Test that unauthenticated users are redirected from the admin dashboard."""
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_admin_dashboard_non_staff_redirect(self):
        """Test that non-staff users are redirected from the admin dashboard."""
        self.client.login(username='normaluser', password='password')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('index'), response.url)

    def test_admin_dashboard_staff_access(self):
        """Test that staff users can access the admin dashboard."""
        self.client.login(username='staffuser', password='password')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_delete_order_csrf_protection(self):
        """Test that the deleteOrder view is protected from CSRF attacks."""
        self.client.login(username='staffuser', password='password')
        # Note: The `enforce_csrf_checks` flag is True by default in the test client for POST requests.
        # A request without a CSRF token will result in a 403 Forbidden.
        response = self.client.post(reverse('delete_order', args=[self.order.id]), {'reason': 'test'})
        self.assertEqual(response.status_code, 403)

    def test_sales_report_staff_redirect(self):
        """Test that non-admin staff are redirected from the sales report."""
        self.client.login(username='staffuser', password='password')
        response = self.client.get(reverse('sales_report'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin_dashboard'), response.url)

    def test_sales_report_admin_access(self):
        """Test that admin users can access the sales report."""
        self.client.login(username='adminuser', password='password')
        response = self.client.get(reverse('sales_report'))
        self.assertEqual(response.status_code, 200)
