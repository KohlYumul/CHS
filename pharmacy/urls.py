from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.pharmacy_medication_list, name='medication_list'),
    path('prescribe/', views.prescribe_medication, name='prescribe_medication'),
    path('buy/<int:medication_id>/', views.buy_medication, name='buy_medication'),
    path('my-prescriptions/', views.my_prescriptions, name='my_prescriptions'),
    path('purchase-history/', views.purchase_history, name='purchase_history'),
    path('buy-from-prescription/<int:prescription_id>/', views.buy_from_prescription, name='buy_from_prescription'),
]
