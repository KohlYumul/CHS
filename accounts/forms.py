from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class PatientRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'hospital', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'Patient'
        if commit:
            user.save()
        return user


class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'role', 'password1', 'password2', 'hospital']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit role field to only Admin and Staff
        self.fields['role'].choices = [
            ('Admin', 'Admin'),
            ('Staff', 'Staff')
        ]
        self.fields['hospital'].required = False  # Make optional until role is 'Staff'

class PatientUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'hospital']  # no role/hospital

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "Patient"  # force role to Patient
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    password = None  # hide password field
    
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'role', 'hospital', 'is_active']
