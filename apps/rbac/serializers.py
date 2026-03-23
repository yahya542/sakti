"""
RBAC Serializers.
"""

from rest_framework import serializers
from .models import Permission, RolePermission, get_default_permissions


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'resource', 'action', 'description']


class RolePermissionSerializer(serializers.ModelSerializer):
    permission_detail = PermissionSerializer(source='permission', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = ['id', 'role', 'permission', 'permission_detail', 'is_granted']


class RolePermissionsSerializer(serializers.Serializer):
    """Serializer for bulk role permissions."""
    
    role = serializers.CharField()
    permissions = serializers.ListField(child=serializers.CharField())


class CheckPermissionSerializer(serializers.Serializer):
    """Serializer for checking user permissions."""
    
    resource = serializers.CharField()
    action = serializers.CharField()
    
    def validate(self, attrs):
        from .models import get_default_permissions
        user = self.context['request'].user
        
        role_perms = get_default_permissions()
        perm_code = f"{attrs['resource']}:{attrs['action']}"
        
        if perm_code in role_perms.get(user.role, []):
            return attrs
        
        raise serializers.ValidationError('Anda tidak memiliki izin untuk aksi ini.')