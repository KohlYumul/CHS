from django.contrib import admin
from .models import *

admin.site.register(Medication)
admin.site.register(MedicalSupply)
admin.site.register(Equipment)