from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from hospitals.models import Hospital
from inventory.models import Medication, MedicalSupply, Equipment


class InventoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hospital = Hospital.objects.create(name="Metro Hospital")
        self.admin = CustomUser.objects.create_user(
            email="admin@metro.com", password="password123", role="Admin", first_name="A", last_name="Admin"
        )
        self.staff = CustomUser.objects.create_user(
            email="staff@metro.com", password="password123", role="Staff",
            hospital=self.hospital, first_name="S", last_name="Staff"
        )

    def test_staff_medication_crud(self):
        self.client.login(email="staff@metro.com", password="password123")
        
        # Create
        add_url = reverse('inventory:medication_create')
        res = self.client.post(add_url, {
            'name': 'Ibuprofen',
            'description': 'Anti-inflammatory',
            'quantity': 100,
            'unit': 'tablets',
            'price': '8.50',
            'prescription_required': False
        })
        self.assertEqual(res.status_code, 302)
        med = Medication.objects.get(name='Ibuprofen')
        self.assertEqual(med.hospital, self.hospital)

        # Update
        edit_url = reverse('inventory:medication_update', kwargs={'pk': med.pk})
        res2 = self.client.post(edit_url, {
            'name': 'Ibuprofen 400mg',
            'description': 'Anti-inflammatory',
            'quantity': 90,
            'unit': 'tablets',
            'price': '9.00',
            'prescription_required': False
        })
        self.assertEqual(res2.status_code, 302)
        med.refresh_from_db()
        self.assertEqual(med.name, 'Ibuprofen 400mg')

        # Delete
        del_url = reverse('inventory:medication_delete', kwargs={'pk': med.pk})
        res3 = self.client.post(del_url)
        self.assertEqual(res3.status_code, 302)
        self.assertFalse(Medication.objects.filter(pk=med.pk).exists())

    def test_staff_supply_and_equipment_crud(self):
        self.client.login(email="staff@metro.com", password="password123")

        # Supply
        res = self.client.post(reverse('inventory:supply_create'), {
            'name': 'Surgical Gloves',
            'description': 'Latex gloves size M',
            'quantity': 500,
            'unit': 'pairs'
        })
        self.assertEqual(res.status_code, 302)
        supply = MedicalSupply.objects.get(name='Surgical Gloves')
        self.assertEqual(supply.hospital, self.hospital)

        # Equipment
        res2 = self.client.post(reverse('inventory:equipment_create'), {
            'name': 'Ultrasound Machine',
            'description': 'Room 302 scanner',
            'quantity': 2,
            'status': 'working'
        })
        self.assertEqual(res2.status_code, 302)
        equip = Equipment.objects.get(name='Ultrasound Machine')
        self.assertEqual(equip.hospital, self.hospital)

