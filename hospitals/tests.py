from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from hospitals.models import Hospital


class HospitalSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hospital = Hospital.objects.create(
            name="General Hospital",
            address="123 Health Ave",
            contact_number="555-0100",
            email="general@hospital.com",
            description="Main facility"
        )
        self.admin = CustomUser.objects.create_user(
            email="admin@hospital.com",
            password="adminpassword123",
            role="Admin",
            first_name="Super",
            last_name="Admin"
        )
        self.staff = CustomUser.objects.create_user(
            email="staff@hospital.com",
            password="staffpassword123",
            role="Staff",
            hospital=self.hospital,
            first_name="Staff",
            last_name="Member"
        )
        self.patient = CustomUser.objects.create_user(
            email="patient@hospital.com",
            password="patientpassword123",
            role="Patient",
            hospital=self.hospital,
            first_name="John",
            last_name="Patient"
        )

    def test_anonymous_cannot_create_hospital(self):
        url = reverse('hospitals:hospital_create')
        response = self.client.post(url, {'name': 'Rogue Hospital'})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Hospital.objects.filter(name='Rogue Hospital').exists())

    def test_anonymous_cannot_update_hospital(self):
        url = reverse('hospitals:hospital_update', kwargs={'pk': self.hospital.pk})
        response = self.client.post(url, {'name': 'Hacked Hospital'})
        self.assertEqual(response.status_code, 403)
        self.hospital.refresh_from_db()
        self.assertEqual(self.hospital.name, "General Hospital")

    def test_anonymous_cannot_delete_hospital(self):
        url = reverse('hospitals:hospital_delete', kwargs={'pk': self.hospital.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Hospital.objects.filter(pk=self.hospital.pk).exists())

    def test_staff_cannot_create_or_delete_hospital(self):
        self.client.login(email="staff@hospital.com", password="staffpassword123")
        create_res = self.client.post(reverse('hospitals:hospital_create'), {'name': 'Staff Hospital'})
        self.assertEqual(create_res.status_code, 403)
        del_res = self.client.post(reverse('hospitals:hospital_delete', kwargs={'pk': self.hospital.pk}))
        self.assertEqual(del_res.status_code, 403)
        self.assertTrue(Hospital.objects.filter(pk=self.hospital.pk).exists())

    def test_patient_cannot_delete_hospital(self):
        self.client.login(email="patient@hospital.com", password="patientpassword123")
        del_res = self.client.post(reverse('hospitals:hospital_delete', kwargs={'pk': self.hospital.pk}))
        self.assertEqual(del_res.status_code, 403)
        self.assertTrue(Hospital.objects.filter(pk=self.hospital.pk).exists())

    def test_admin_can_manage_hospital(self):
        self.client.login(email="admin@hospital.com", password="adminpassword123")
        
        # Create
        create_res = self.client.post(reverse('hospitals:hospital_create'), {
            'name': 'New Hospital',
            'address': '456 Clinic Rd'
        })
        self.assertEqual(create_res.status_code, 302)
        new_hosp = Hospital.objects.get(name='New Hospital')
        
        # Update
        update_res = self.client.post(reverse('hospitals:hospital_update', kwargs={'pk': new_hosp.pk}), {
            'name': 'Updated Hospital',
            'address': '789 Clinic Rd'
        })
        self.assertEqual(update_res.status_code, 302)
        new_hosp.refresh_from_db()
        self.assertEqual(new_hosp.name, 'Updated Hospital')

        # Delete
        del_res = self.client.post(reverse('hospitals:hospital_delete', kwargs={'pk': new_hosp.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Hospital.objects.filter(pk=new_hosp.pk).exists())

