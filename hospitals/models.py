# hospitals/models.py
from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name or "Unnamed Hospital"

class Department(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments', null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    head = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        hospital_name = self.hospital.name if self.hospital else "No Hospital"
        return f"{self.name or 'Department'} - {hospital_name}"

