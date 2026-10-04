# pharmacy/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Prescription
from inventory.models import Medication

User = get_user_model()

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'medication', 'quantity', 'is_active']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow patients in patient field
        self.fields['patient'].queryset = User.objects.filter(role='Patient', is_active=True)
        # Usually you only prescribe meds that require a prescription
        self.fields['medication'].queryset = Medication.objects.filter(prescription_required=True)


class PurchaseForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label="Quantity")
