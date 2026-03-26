"""
Tenant Views - API endpoints for tenant management.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_tenants.utils import get_tenant
from django.db import connection

from .models import Tenant, Domain
from .serializers import TenantSerializer, TenantCreateSerializer, DomainSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Tenants'],
        summary='List all tenants',
        description='Get a list of all tenants (schools/pesantren). Super admin only.'
    ),
    create=extend_schema(
        tags=['Tenants'],
        summary='Create new tenant',
        description='Create a new tenant with schema. Super admin only.'
    ),
    retrieve=extend_schema(
        tags=['Tenants'],
        summary='Get tenant details',
        description='Get detailed information about a specific tenant.'
    ),
    update=extend_schema(
        tags=['Tenants'],
        summary='Update tenant',
        description='Update tenant information. Super admin only.'
    ),
    destroy=extend_schema(
        tags=['Tenants'],
        summary='Delete tenant',
        description='Delete a tenant. Super admin only.'
    )
)
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
    
    @extend_schema(
        tags=['Tenants'],
        summary='Get current tenant',
        description='Get current tenant information based on the request context.'
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current tenant info."""
        tenant = get_tenant()
        serializer = self.get_serializer(tenant)
        return Response(serializer.data)
    
    @extend_schema(
        tags=['Tenants'],
        summary='Activate tenant',
        description='Activate a tenant (enable their schema). Super admin only.'
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a tenant."""
        tenant = self.get_object()
        tenant.is_active = True
        tenant.save()
        return Response({'status': 'tenant activated'})
    
    @extend_schema(
        tags=['Tenants'],
        summary='Deactivate tenant',
        description='Deactivate a tenant (disable their schema). Super admin only.'
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a tenant."""
        tenant = self.get_object()
        tenant.is_active = False
        tenant.save()
        return Response({'status': 'tenant deactivated'})
    
    @extend_schema(
        tags=['Tenants'],
        summary='Get tenant schema info',
        description='Get database schema information for a tenant. Super admin only.'
    )
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