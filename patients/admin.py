from django.contrib import admin
from . import models

admin.site.register(models.PatientProfile)
admin.site.register(models.MedicalRecord)
admin.site.register(models.Comment)
