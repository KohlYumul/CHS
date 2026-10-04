import os
import gc
from pathlib import Path
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

from accounts.models import CustomUser
from hospitals.models import Hospital
from patients.models import PatientProfile, MedicalRecord
from reports.models import Report


class ProtectedMediaAndRecordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.open_responses = []

        # Create two distinct hospitals
        self.hospital_a = Hospital.objects.create(name="Hospital Alpha")
        self.hospital_b = Hospital.objects.create(name="Hospital Beta")

        # Admin user
        self.admin = CustomUser.objects.create_user(
            email="admin@test.com", password="password123", role="Admin", first_name="A", last_name="Admin"
        )

        # Staff in Hospital A
        self.staff_a = CustomUser.objects.create_user(
            email="staff_a@test.com", password="password123", role="Staff",
            hospital=self.hospital_a, first_name="Staff", last_name="Alpha"
        )

        # Staff in Hospital B
        self.staff_b = CustomUser.objects.create_user(
            email="staff_b@test.com", password="password123", role="Staff",
            hospital=self.hospital_b, first_name="Staff", last_name="Beta"
        )

        # Patient 1 in Hospital A
        self.patient_user_1 = CustomUser.objects.create_user(
            email="patient1@test.com", password="password123", role="Patient",
            hospital=self.hospital_a, first_name="Patient", last_name="One"
        )
        self.patient_profile_1 = PatientProfile.objects.create(
            user=self.patient_user_1, date_of_birth="1990-01-01", gender="male"
        )

        # Patient 2 in Hospital B
        self.patient_user_2 = CustomUser.objects.create_user(
            email="patient2@test.com", password="password123", role="Patient",
            hospital=self.hospital_b, first_name="Patient", last_name="Two"
        )
        self.patient_profile_2 = PatientProfile.objects.create(
            user=self.patient_user_2, date_of_birth="1995-05-05", gender="female"
        )

        # Create a test file on disk in MEDIA_ROOT
        media_root = Path(settings.MEDIA_ROOT)
        (media_root / "medical_records").mkdir(parents=True, exist_ok=True)
        (media_root / "reports").mkdir(parents=True, exist_ok=True)

        self.record1_filename = "medical_records/test_record_1.pdf"
        self.record1_path = media_root / self.record1_filename
        self.record1_path.write_bytes(b"%PDF-1.4 Mock Medical Record Content")

        self.record_1 = MedicalRecord.objects.create(
            patient=self.patient_profile_1,
            description="Blood Test Report",
            file=self.record1_filename
        )

        self.report_a_filename = "reports/test_report_a.pdf"
        self.report_a_path = media_root / self.report_a_filename
        self.report_a_path.write_bytes(b"%PDF-1.4 Mock Hospital Alpha Report")

        self.report_a = Report.objects.create(
            hospital=self.hospital_a,
            title="Q1 Alpha Report",
            file=self.report_a_filename,
            generated_by=self.staff_a
        )

    def tearDown(self):
        for resp in self.open_responses:
            try:
                resp.close()
            except Exception:
                pass
        self.open_responses.clear()
        gc.collect()

        # Clean up test files safely
        for path in [self.record1_path, self.report_a_path]:
            if path.exists():
                try:
                    path.unlink()
                except PermissionError:
                    pass

    def get_and_track(self, url):
        response = self.client.get(url)
        self.open_responses.append(response)
        return response

    def test_anonymous_cannot_access_media(self):
        url = f"/media/{self.record1_filename}"
        response = self.get_and_track(url)
        self.assertEqual(response.status_code, 403)

    def test_patient_can_access_own_medical_record(self):
        self.client.login(email="patient1@test.com", password="password123")
        url = f"/media/{self.record1_filename}"
        response = self.get_and_track(url)
        self.assertEqual(response.status_code, 200)

    def test_patient_cannot_access_other_patient_record(self):
        self.client.login(email="patient2@test.com", password="password123")
        url = f"/media/{self.record1_filename}"
        response = self.get_and_track(url)
        self.assertEqual(response.status_code, 403)

    def test_patient_cannot_access_hospital_reports(self):
        self.client.login(email="patient1@test.com", password="password123")
        url = f"/media/{self.report_a_filename}"
        response = self.get_and_track(url)
        self.assertEqual(response.status_code, 403)

    def test_staff_can_access_records_from_own_hospital(self):
        self.client.login(email="staff_a@test.com", password="password123")
        url = f"/media/{self.record1_filename}"
        response = self.get_and_track(url)
        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_access_records_from_other_hospital(self):
        self.client.login(email="staff_b@test.com", password="password123")
        url = f"/media/{self.record1_filename}"
        response = self.get_and_track(url)
        self.assertEqual(response.status_code, 403)

    def test_staff_can_access_reports_from_own_hospital(self):
        self.client.login(email="staff_a@test.com", password="password123")
        url = f"/media/{self.report_a_filename}"
        response = self.get_and_track(url)
        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_access_reports_from_other_hospital(self):
        self.client.login(email="staff_b@test.com", password="password123")
        url = f"/media/{self.report_a_filename}"
        response = self.get_and_track(url)
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_any_media_file(self):
        self.client.login(email="admin@test.com", password="password123")
        res1 = self.get_and_track(f"/media/{self.record1_filename}")
        self.assertEqual(res1.status_code, 200)
        res2 = self.get_and_track(f"/media/{self.report_a_filename}")
        self.assertEqual(res2.status_code, 200)

    def test_path_traversal_is_blocked(self):
        self.client.login(email="admin@test.com", password="password123")
        response = self.get_and_track("/media/../manage.py")
        self.assertIn(response.status_code, [403, 404])

        response2 = self.get_and_track("/media/../../../../windows/system.ini")
        self.assertIn(response2.status_code, [403, 404])

    def test_record_form_renders_without_crash(self):
        self.client.login(email="admin@test.com", password="password123")
        # Add form
        add_res = self.get_and_track(reverse('patients:record_create'))
        self.assertEqual(add_res.status_code, 200)

        # Edit form
        edit_res = self.get_and_track(reverse('patients:record_update', kwargs={'pk': self.record_1.pk}))
        self.assertEqual(edit_res.status_code, 200)

