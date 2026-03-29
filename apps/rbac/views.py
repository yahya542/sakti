"""
RBAC Views - Permission management endpoints.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Permission, RolePermission, get_default_permissions
from .serializers import PermissionSerializer, RolePermissionSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['RBAC'],
        summary='Daftar izin',
        description='Mengambil daftar semua izin.'
    ),
    create=extend_schema(
        tags=['RBAC'],
        summary='Buat izin',
        description='Membuat izin baru.'
    ),
    retrieve=extend_schema(
        tags=['RBAC'],
        summary='Detail izin',
        description='Mengambil informasi detail izin tertentu.'
    ),
    update=extend_schema(
        tags=['RBAC'],
        summary='Perbarui izin',
        description='Memperbarui informasi izin.'
    ),
    destroy=extend_schema(
        tags=['RBAC'],
        summary='Hapus izin',
        description='Menghapus izin.'
    )
)
class PermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for Permission CRUD operations."""
    
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['RBAC'],
        summary='Izin peran',
        description='Mengambil izin untuk peran tertentu.'
    )
    @action(detail=False, methods=['get'])
    def role_permissions(self, request):
        """Get permissions for current user's role."""
        role = request.query_params.get('role', request.user.role)
        
        perms = get_default_permissions()
        role_perms = perms.get(role, [])
        
        # Get permission objects
        permissions = Permission.objects.filter(code__in=role_perms)
        serializer = self.get_serializer(permissions, many=True)
        
        return Response({
            'role': role,
            'permissions': serializer.data
        })


@extend_schema(
    tags=['RBAC'],
    summary='Cek izin',
    description='Memeriksa apakah pengguna saat ini memiliki izin tertentu.'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_permission(request):
    """Check if user has specific permission."""
    resource = request.data.get('resource')
    action = request.data.get('action')
    
    if not resource or not action:
        return Response(
            {'error': 'Resource dan action diperlukan.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    perms = get_default_permissions()
    user_perms = perms.get(request.user.role, [])
    perm_code = f"{resource}:{action}"
    
    return Response({
        'has_permission': perm_code in user_perms
    })


@extend_schema(
    tags=['RBAC'],
    summary='Izin saya',
    description='Mengambil semua izin untuk pengguna saat ini.'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_permissions(request):
    """Get all permissions for current user."""
    perms = get_default_permissions()
    user_perms = perms.get(request.user.role, [])
    
    permissions = Permission.objects.filter(code__in=user_perms)
    serializer = PermissionSerializer(permissions, many=True)
    
    return Response({
        'role': request.user.role,
        'permissions': serializer.data
    })