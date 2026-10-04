from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Medication
    path('medications/', views.medication_list, name='medication_list'),
    path('medications/add/', views.medication_create, name='medication_create'),
    path('medications/<int:pk>/edit/', views.medication_update, name='medication_update'),
    path('medications/<int:pk>/delete/', views.medication_delete, name='medication_delete'),

    # Supplies
    path('supplies/', views.supply_list, name='supply_list'),
    path('supplies/add/', views.supply_create, name='supply_create'),
    path('supplies/<int:pk>/edit/', views.supply_update, name='supply_update'),
    path('supplies/<int:pk>/delete/', views.supply_delete, name='supply_delete'),

    # Equipment
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/add/', views.equipment_create, name='equipment_create'),
    path('equipment/<int:pk>/edit/', views.equipment_update, name='equipment_update'),
    path('equipment/<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
]
