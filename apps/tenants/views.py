"""
Tenant Views - API endpoints for tenant management.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # PENTING: Jangan lupa ini
from django_tenants.utils import get_tenant
from django.db import connection

from .models import Tenant, Domain
from .serializers import TenantSerializer, TenantCreateSerializer, DomainSerializer

@extend_schema_view(
    list=extend_schema(tags=['Tenants'], summary='Daftar semua tenant', description='Mengambil daftar semua tenant (sekolah/pesantren).'),
    create=extend_schema(tags=['Tenants'], summary='Buat tenant', description='Membuat tenant baru.'),
    retrieve=extend_schema(tags=['Tenants'], summary='Detail tenant', description='Mengambil informasi detail tenant tertentu.'),
    update=extend_schema(tags=['Tenants'], summary='Perbarui tenant', description='Memperbarui informasi tenant.'),
    destroy=extend_schema(tags=['Tenants'], summary='Hapus tenant', description='Menghapus tenant.'),
)
class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenants (schools/pesantren).
    """
    
    queryset = Tenant.objects.all()
    # Default: Semua endpoint di sini butuh Login
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Custom permission logic.
        """
        # super_admin dapat mengakses semua action
        if getattr(self.request.user, 'role', None) == 'super_admin':
            return [IsAuthenticated()]
        
        # Untuk action 'current', tetap perlu IsAuthenticated
        if self.action == 'current':
            return [IsAuthenticated()]
        
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TenantCreateSerializer
        return TenantSerializer
    
    @extend_schema(
        tags=['Tenants'],
        summary='Tenant saat ini',
        description='Mengambil atau memperbarui informasi tenant saat ini. PATCH hanya untuk super_admin.'
    )
    @action(detail=False, methods=['get', 'patch'], url_path='current')
    def current(self, request):
        """
        Handler untuk GET dan PATCH /tenants/current/
        """
        # Debug: Print user info
        print(f"DEBUG: request.user = {request.user}, is_authenticated = {request.user.is_authenticated if hasattr(request.user, 'is_authenticated') else 'N/A'}")
        print(f"DEBUG: user role = {getattr(request.user, 'role', 'NO_ROLE_ATTR')}")
        
        # 1. Proteksi Awal: Pastikan User Login
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication credentials were not provided.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. Ambil Objek Tenant
        # Jika super_admin, kita ambil tenant pertama sebagai default management
        user_role = getattr(request.user, 'role', None)
        print(f"DEBUG: user_role = {user_role}")
        
        if user_role == 'super_admin':
            tenant = Tenant.objects.first()
        else:
            # Untuk user biasa, ambil tenant dari context django-tenants
            tenant = get_tenant()

        if not tenant:
            return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        # 3. Logika Jika Method-nya PATCH (Update Data)
        if request.method == 'PATCH':
            # Hanya super_admin yang boleh edit data Tenant (Warna, Nama, Logo)
            # Gunakan string comparison karena role mungkin string, bukan constant
            user_role = str(getattr(request.user, 'role', ''))
            print(f"DEBUG PATCH: user_role = {user_role}, type = {type(user_role)}")
            
            if user_role != 'super_admin':
                return Response(
                    {'error': 'Hanya Super Admin yang bisa mengubah data instansi.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = self.get_serializer(tenant, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # 4. Logika Jika Method-nya GET (Ambil Data)
        serializer = self.get_serializer(tenant)
        return Response(serializer.data)

    # --- Action Lainnya ---

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        tenant = self.get_object()
        tenant.is_active = True
        tenant.save()
        return Response({'status': 'tenant activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        tenant = self.get_object()
        tenant.is_active = False
        tenant.save()
        return Response({'status': 'tenant deactivated'})

class DomainViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tenant domains."""
    
    queryset = Domain.objects.all()
    # Hanya admin Django yang biasanya mengelola domain
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DomainSerializer
    
    def get_queryset(self):
        # Mengambil domain berdasarkan tenant yang sedang diakses lewat URL
        return Domain.objects.filter(tenant_id=self.kwargs.get('tenant_pk'))