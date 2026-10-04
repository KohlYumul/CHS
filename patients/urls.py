from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.record_list, name='record_list'),
    path('add/', views.record_create, name='record_create'),
    path('<int:pk>/edit/', views.record_update, name='record_update'),
    path('<int:pk>/delete/', views.record_delete, name='record_delete'),

    path('<int:record_id>/comment/add/', views.comment_create, name='comment_create'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('my-record/', views.my_record, name='my_record'),

    path('my-profile/', views.my_profile, name='my_profile'),
    path('list/', views.patient_list, name='patient_list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/create/', views.patientprofile_create, name='patientprofile_create'),
    path('patients/<int:pk>/edit/', views.patientprofile_update, name='patientprofile_update'),
]
