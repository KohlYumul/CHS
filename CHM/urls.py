from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from .views import serve_protected_media

urlpatterns = [
    path('', lambda request: redirect('accounts:login')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('hospitals/', include('hospitals.urls', namespace='hospitals')),
    path('pharmacy/', include('pharmacy.urls', namespace='pharmacy')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('patients/', include('patients.urls', namespace='patients')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('media/<path:file_path>', serve_protected_media, name='serve_protected_media'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

