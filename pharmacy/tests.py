from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from accounts.models import CustomUser
from hospitals.models import Hospital
from inventory.models import Medication
from pharmacy.models import Prescription, Purchase


class PharmacyTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hospital = Hospital.objects.create(name="St. Jude Hospital")
        self.admin = CustomUser.objects.create_user(
            email="admin@test.com", password="password123", role="Admin", first_name="A", last_name="Admin"
        )
        self.patient = CustomUser.objects.create_user(
            email="patient@test.com", password="password123", role="Patient",
            hospital=self.hospital, first_name="P", last_name="Patient"
        )
        self.otc_med = Medication.objects.create(
            name="Paracetamol",
            description="Pain reliever",
            quantity=50,
            unit="tablets",
            price=Decimal("5.00"),
            prescription_required=False,
            hospital=self.hospital
        )
        self.rx_med = Medication.objects.create(
            name="Amoxicillin",
            description="Antibiotic",
            quantity=20,
            unit="capsules",
            price=Decimal("15.00"),
            prescription_required=True,
            hospital=self.hospital
        )

    def test_otc_medication_list_renders_without_crash(self):
        self.client.login(email="patient@test.com", password="password123")
        response = self.client.get(reverse('pharmacy:medication_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paracetamol")

    def test_admin_medication_list_with_hospital_filter(self):
        self.client.login(email="admin@test.com", password="password123")
        url = f"{reverse('pharmacy:medication_list')}?hospital_id={self.hospital.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paracetamol")

    def test_patient_can_buy_otc_medication(self):
        self.client.login(email="patient@test.com", password="password123")
        url = reverse('pharmacy:buy_medication', kwargs={'medication_id': self.otc_med.id})
        
        # GET purchase form
        get_res = self.client.get(url)
        self.assertEqual(get_res.status_code, 200)

        # POST purchase
        post_res = self.client.post(url, {'quantity': 5})
        self.assertEqual(post_res.status_code, 302)
        
        self.otc_med.refresh_from_db()
        self.assertEqual(self.otc_med.quantity, 45)
        self.assertTrue(Purchase.objects.filter(patient=self.patient, medication=self.otc_med, quantity=5).exists())

    def test_insufficient_stock_purchase_denied(self):
        self.client.login(email="patient@test.com", password="password123")
        url = reverse('pharmacy:buy_medication', kwargs={'medication_id': self.otc_med.id})
        post_res = self.client.post(url, {'quantity': 100})
        self.assertEqual(post_res.status_code, 200)
        self.assertContains(post_res, "Not enough stock available")
        self.otc_med.refresh_from_db()
        self.assertEqual(self.otc_med.quantity, 50)

