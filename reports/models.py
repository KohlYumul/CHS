# reports/models.py
from django.db import models
from hospitals.models import Hospital
from accounts.models import CustomUser
class Report(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.hospital.name})"
