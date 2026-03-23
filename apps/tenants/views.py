"""
Tenant Views - API endpoints for tenant management.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_tenants.utils import get_tenant
from django.db import connection

from .models import Tenant, Domain
from .serializers import TenantSerializer, TenantCreateSerializer, DomainSerializer


class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenants (schools/pesantren).
    Only accessible by Super Admin.
    """
    
    queryset = Tenant.objects.all()
    permission_classes = [permissions.IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TenantCreateSerializer
        return TenantSerializer
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current tenant info."""
        tenant = get_tenant()
        serializer = self.get_serializer(tenant)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a tenant."""
        tenant = self.get_object()
        tenant.is_active = True
        tenant.save()
        return Response({'status': 'tenant activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a tenant."""
        tenant = self.get_object()
        tenant.is_active = False
        tenant.save()
        return Response({'status': 'tenant deactivated'})
    
    @action(detail=True, methods=['get'])
    def schema_info(self, request, pk=None):
        """Get database schema info for tenant."""
        tenant = self.get_object()
        return Response({
            'schema_name': tenant.schema_name,
            'name': tenant.name,
            'kode_instansi': tenant.kode_instansi
        })


class DomainViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tenant domains."""
    
    queryset = Domain.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DomainSerializer
    
    def get_queryset(self):
        return Domain.objects.filter(tenant_id=self.kwargs.get('tenant_pk'))