from django import forms
from .models import Medication, MedicalSupply, Equipment

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'description', 'quantity', 'unit', 'price', 'prescription_required']

class MedicalSupplyForm(forms.ModelForm):
    class Meta:
        model = MedicalSupply
        fields = ['name', 'description', 'quantity', 'unit']

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'description', 'quantity', 'status']
