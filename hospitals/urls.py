from django.urls import path
from . import views

app_name = 'hospitals'

urlpatterns = [
    path('add/', views.hospital_create, name='hospital_create'),
    path('list/', views.hospital_list_view, name='hospital_list'),
    path('<int:pk>/edit/', views.hospital_update, name='hospital_update'),
    path('<int:pk>/delete/', views.hospital_delete, name='hospital_delete'),
    path("<int:pk>/overview/", views.hospital_overview, name="hospital_overview"),  # new
]
