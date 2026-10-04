from django import forms
from .models import Report

from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ['hospital', 'generated_by']

