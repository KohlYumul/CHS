from django.db import models
from hospitals.models import Hospital

class Medication(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)  # Stock in inventory
    unit = models.CharField(max_length=50, default="pcs")  # e.g., tablets, bottles
    price = models.DecimalField(max_digits=10, decimal_places=2)
    prescription_required = models.BooleanField(default=False)  # ✅ New field
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name="medication")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"


class MedicalSupply(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=50, default="pcs")  # ✅ New field
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name="medical_supply")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"


class Equipment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(  # ✅ New field
        max_length=50,
        choices=[("working", "Working"), ("maintenance", "Maintenance"), ("broken", "Broken")],
        default="working"
    )
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name="equipment")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} units - {self.status})"
