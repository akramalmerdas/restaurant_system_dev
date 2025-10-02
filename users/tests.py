from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Staff

class StaffDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', password='password', is_staff=True)
        self.staff_user = User.objects.create_user(username='staff', password='password', email='staff@example.com')
        self.customer_user = User.objects.create_user(username='customer', password='password')

        self.admin_staff = Staff.objects.create(user=self.admin_user, role='admin')
        self.waiter_staff = Staff.objects.create(user=self.staff_user, role='waiter')

    def test_admin_can_access_staff_dashboard(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('users:staff_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_access_staff_dashboard(self):
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('users:staff_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('orders:admin_dashboard'))

    def test_customer_cannot_access_staff_dashboard(self):
        self.client.login(username='customer', password='password')
        response = self.client.get(reverse('users:staff_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_user_cannot_access_staff_dashboard(self):
        response = self.client.get(reverse('users:staff_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('users:staff_dashboard')}")

    def test_add_staff_member(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('users:add_staff'), {
            'first_name': 'New',
            'last_name': 'Staff',
            'email': 'newstaff@test.com',
            'role': 'waiter',
            'phone_number': '1234567890',
            'salary': '50000',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newstaff@test.com').exists())
        self.assertTrue(Staff.objects.filter(user__email='newstaff@test.com').exists())

    def test_edit_staff_member(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('users:edit_staff', args=[self.waiter_staff.id]), {
            'first_name': 'Updated',
            'last_name': 'Staff',
            'email': self.staff_user.email,
            'role': 'chef',
            'phone_number': '1234567890',
            'salary': '60000',
        })
        self.assertEqual(response.status_code, 302)
        self.waiter_staff.refresh_from_db()
        self.assertEqual(self.waiter_staff.role, 'chef')
        self.assertEqual(self.waiter_staff.user.first_name, 'Updated')

    def test_deactivate_staff_member(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('users:delete_staff', args=[self.waiter_staff.id]))
        self.assertEqual(response.status_code, 302)
        self.waiter_staff.refresh_from_db()
        self.assertFalse(self.waiter_staff.user.is_active)
        self.assertTrue(self.waiter_staff.inHold)

    def test_search_staff_member(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('users:staff_dashboard'), {'query': 'admin'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].user.username, 'admin')

    def test_filter_staff_by_role(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('users:staff_dashboard'), {'role': 'waiter'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].role, 'waiter')