# patients/forms.py
from django import forms
from .models import MedicalRecord, Comment, PatientProfile

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = '__all__'

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

# patients/forms.py
from django import forms
from .models import PatientProfile
from accounts.models import CustomUser

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = [
            'user',
            'date_of_birth',
            'gender',
            'blood_type',
            'phone_number',
            'address',
            'allergies',
            'chronic_conditions',
            'medications',
            'emergency_contact_name',
            'emergency_contact_number',
            'emergency_contact_relation',
        ]

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'blood_type': forms.Select(choices=PatientProfile.BLOOD_TYPES),
        }

    def __init__(self, *args, **kwargs):
        # Pop a custom keyword to detect update
        is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)

        if is_update:
            # If updating, remove user field
            self.fields.pop('user')
        else:
            # Limit user choices to patients without a profile yet
            self.fields['user'].queryset = CustomUser.objects.filter(role='Patient', patientprofile__isnull=True)
