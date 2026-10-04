from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from hospitals.models import Hospital
from reports.models import Report


class ReportTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hospital_a = Hospital.objects.create(name="City Hospital")
        self.hospital_b = Hospital.objects.create(name="County Hospital")

        self.staff_a = CustomUser.objects.create_user(
            email="staff_a@city.com", password="password123", role="Staff",
            hospital=self.hospital_a, first_name="A", last_name="Staff"
        )
        self.staff_b = CustomUser.objects.create_user(
            email="staff_b@county.com", password="password123", role="Staff",
            hospital=self.hospital_b, first_name="B", last_name="Staff"
        )
        self.patient = CustomUser.objects.create_user(
            email="patient@city.com", password="password123", role="Patient",
            hospital=self.hospital_a, first_name="P", last_name="Patient"
        )
        self.report_a = Report.objects.create(
            hospital=self.hospital_a,
            title="City Hospital Audit",
            generated_by=self.staff_a,
            description="Annual equipment audit"
        )

    def test_patient_cannot_view_report_list(self):
        self.client.login(email="patient@city.com", password="password123")
        response = self.client.get(reverse('reports:report_list'))
        self.assertEqual(response.status_code, 403)

    def test_staff_can_view_own_hospital_reports(self):
        self.client.login(email="staff_a@city.com", password="password123")
        response = self.client.get(reverse('reports:report_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "City Hospital Audit")

    def test_staff_cannot_edit_other_hospital_report(self):
        self.client.login(email="staff_b@county.com", password="password123")
        edit_url = reverse('reports:report_update', kwargs={'pk': self.report_a.pk})
        response = self.client.post(edit_url, {'title': 'Tampered Report'})
        self.assertEqual(response.status_code, 302)
        self.report_a.refresh_from_db()
        self.assertEqual(self.report_a.title, "City Hospital Audit")

