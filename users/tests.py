from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Staff, Leave, FinancialTransaction, Loan

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

class StaffAdvancedManagementTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', password='password', is_staff=True)
        self.staff_user = User.objects.create_user(username='staffer', password='password', email='staffer@example.com')

        self.admin_staff = Staff.objects.create(user=self.admin_user, role='admin')
        self.test_staff = Staff.objects.create(user=self.staff_user, role='waiter')

        self.client.login(username='admin', password='password')

    def test_add_loan_and_repayment(self):
        # Add a loan
        self.client.post(reverse('users:add_loan', args=[self.test_staff.id]), {'amount': '1000.00', 'date': '2025-10-12', 'description': 'Test Loan'})
        transaction = FinancialTransaction.objects.get(staff=self.test_staff, transaction_type='loan')
        self.assertEqual(transaction.amount, 1000)

        # Add a repayment
        self.client.post(reverse('users:add_repayment', args=[self.test_staff.id]), {'amount': '200.00', 'date': '2025-10-12', 'description': 'Repayment'})

        self.assertEqual(FinancialTransaction.objects.filter(staff=self.test_staff, transaction_type='repayment').count(), 1)

    def test_add_loan(self):
        response = self.client.post(reverse('users:add_loan', args=[self.test_staff.id]), {
            'amount': '1000.00',
            'date': '2025-10-12',
            'description': 'Test loan'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(FinancialTransaction.objects.filter(staff=self.test_staff, amount='1000.00', transaction_type='loan').exists())

    def test_add_deduction(self):
        response = self.client.post(reverse('users:add_deduction', args=[self.test_staff.id]), {
            'amount': '50.00',
            'date': '2025-10-08',
            'description': 'Uniform fee'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(FinancialTransaction.objects.filter(staff=self.test_staff, amount='50.00', transaction_type='deduction').exists())

    def test_add_leave(self):
        response = self.client.post(reverse('users:add_leave', args=[self.test_staff.id]), {
            'start_date': '2025-10-20',
            'end_date': '2025-10-22',
            'leave_type': 'sick',
            'reason': 'Flu'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Leave.objects.filter(staff=self.test_staff, reason='Flu').exists())

    def test_staff_detail_view(self):
        FinancialTransaction.objects.create(staff=self.test_staff, amount=500, transaction_type='loan', date='2025-01-01', description='Loan')
        FinancialTransaction.objects.create(staff=self.test_staff, amount=25, transaction_type='deduction', date='2025-01-01', description='Late')
        Leave.objects.create(staff=self.test_staff, start_date='2025-02-01', end_date='2025-02-02', leave_type='vacation', reason='Holiday')

        response = self.client.get(reverse('users:staff_detail', args=[self.test_staff.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '500')
        self.assertContains(response, 'Late')
        self.assertContains(response, 'Holiday')

    def test_leave_filtering_and_editing(self):
        # Create some leave records
        leave1 = Leave.objects.create(staff=self.test_staff, start_date='2025-03-01', end_date='2025-03-05', leave_type='vacation', reason='Trip')
        leave2 = Leave.objects.create(staff=self.test_staff, start_date='2025-04-10', end_date='2025-04-11', leave_type='sick', reason='Flu')

        # Test filtering
        response = self.client.get(reverse('users:staff_detail', args=[self.test_staff.id]), {'start_date': '2025-03-01', 'end_date': '2025-03-31'})
        self.assertContains(response, 'Trip')
        self.assertNotContains(response, 'Flu')
        self.assertEqual(response.context['total_filtered_leave_days'], 5)

        # Test editing a leave entry
        response = self.client.post(reverse('users:manage_leave_entry', args=[leave1.id]), {
            'start_date': '2025-03-02',
            'end_date': '2025-03-06',
            'leave_type': 'vacation',
            'reason': 'Extended Trip'
        })
        self.assertEqual(response.status_code, 302)
        leave1.refresh_from_db()
        self.assertEqual(leave1.reason, 'Extended Trip')

        # Test deleting a leave entry
        response = self.client.post(reverse('users:manage_leave_entry', args=[leave2.id]), {'delete': '1'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Leave.objects.filter(id=leave2.id).exists())