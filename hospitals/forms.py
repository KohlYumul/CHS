# hospitals/forms.py
from django import forms
from .models import Hospital, Department

class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = '__all__'

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
