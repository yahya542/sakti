"""
SAKTI URL Configuration
Main URL routing with API versioning support.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('auth/', include('apps.accounts.urls')),   # Jadi: /api/auth/login/
    path('rbac/', include('apps.rbac.urls')),       # Jadi: /api/rbac/roles/
    path('tenants/', include('apps.tenants.urls')), # Jadi: /api/tenants/list/
    path('academic/', include('apps.academic.urls')),
    path('activities/', include('apps.activities.urls')),
    path('finance/', include('apps.finance.urls')),
    path('smart-linking/', include('apps.smart_linking.urls')),
    
    # Swagger / API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path("", SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Health check
    path('health/', TemplateView.as_view(template_name='health.html'), name='health'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)