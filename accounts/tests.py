from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured
from accounts.models import CustomUser
from hospitals.models import Hospital


class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hospital = Hospital.objects.create(name="Hope Clinic")
        self.admin = CustomUser.objects.create_user(
            email="admin@hope.com", password="password123", role="Admin", first_name="Admin", last_name="User"
        )
        self.staff = CustomUser.objects.create_user(
            email="staff@hope.com", password="password123", role="Staff",
            hospital=self.hospital, first_name="Staff", last_name="User"
        )
        self.patient = CustomUser.objects.create_user(
            email="patient@hope.com", password="password123", role="Patient",
            hospital=self.hospital, first_name="Patient", last_name="User"
        )

    def test_create_superuser_assigns_admin_role(self):
        superuser = CustomUser.objects.create_superuser(
            email="root@hope.com", password="rootpassword123", first_name="Root", last_name="Super"
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.role, "Admin")

    def test_user_login_redirects_by_role(self):
        # Admin
        res_admin = self.client.post(reverse('accounts:login'), {
            'username': 'admin@hope.com',
            'password': 'password123'
        })
        self.assertRedirects(res_admin, reverse('accounts:admin_dashboard'))

        self.client.logout()

        # Staff
        res_staff = self.client.post(reverse('accounts:login'), {
            'username': 'staff@hope.com',
            'password': 'password123'
        })
        self.assertRedirects(res_staff, reverse('accounts:staff_dashboard'))

        self.client.logout()

        # Patient
        res_patient = self.client.post(reverse('accounts:login'), {
            'username': 'patient@hope.com',
            'password': 'password123'
        })
        self.assertRedirects(res_patient, reverse('accounts:patient_dashboard'))

    def test_user_login_with_next_parameter(self):
        target_url = reverse('pharmacy:medication_list')
        login_url = f"{reverse('accounts:login')}?next={target_url}"
        response = self.client.post(login_url, {
            'username': 'patient@hope.com',
            'password': 'password123'
        })
        self.assertRedirects(response, target_url)

    def test_get_full_name_and_get_short_name(self):
        self.assertEqual(self.admin.get_full_name(), "Admin User")
        self.assertEqual(self.admin.get_short_name(), "Admin")

