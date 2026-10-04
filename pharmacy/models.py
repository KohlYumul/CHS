from django.db import models
from django.conf import settings
from inventory.models import Medication
from hospitals.models import Hospital

class Prescription(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    prescribed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='issued_prescriptions')
    quantity = models.PositiveIntegerField(default=1)  # ✅ NEW
    date_prescribed = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medication.name} ({self.quantity} units) for {self.patient.email}"

class Purchase(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date_purchased = models.DateTimeField(auto_now_add=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.medication.name} x {self.quantity} by {self.patient.email}"
