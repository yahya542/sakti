"""
SAKTI URL Configuration
Main URL routing with API versioning support.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.tenants.urls')),
    path('api/v1/', include('apps.academic.urls')),
    path('api/v1/', include('apps.activities.urls')),
    path('api/v1/', include('apps.finance.urls')),
    path('api/v1/', include('apps.rbac.urls')),
    path('api/v1/', include('apps.smart_linking.urls')),
    
    # Health check
    path('health/', TemplateView.as_view(template_name='health.html'), name='health'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)