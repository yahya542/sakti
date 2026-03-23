"""
RBAC Views - Permission management endpoints.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Permission, RolePermission, get_default_permissions
from .serializers import PermissionSerializer, RolePermissionSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for Permission CRUD operations."""
    
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    
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