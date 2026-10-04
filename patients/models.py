# patients/models.py
from django.db import models
from accounts.models import CustomUser

from django.db import models
from django.conf import settings

class PatientProfile(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'Patient'}
    )
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ])
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES, blank=True, null=True)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    allergies = models.TextField(blank=True, null=True)
    chronic_conditions = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)

    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"

class MedicalRecord(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='records')
    record_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    file = models.FileField(upload_to='medical_records/', blank=True, null=True)

    def __str__(self):
        return f"Record for {self.patient.user.first_name} {self.patient.user.last_name} on {self.record_date}"

class Comment(models.Model):
    record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.first_name} {self.author.last_name}"

