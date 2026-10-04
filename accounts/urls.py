from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Patient self-registration
    path('register/patient/', views.register_patient, name='register_patient'),

    # Admin creating Admin or Staff
    path('create/admin-staff/', views.create_admin_or_staff, name='create_admin_or_staff'),

    path('create/patient/', views.create_patient, name='create_patient'),

    path('users/', views.user_list, name='user_list'),

    # Login & Logout
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Profile update
    path('profile/<int:pk>/edit/', views.profile_update, name='profile_edit'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    # accounts/urls.py
]
