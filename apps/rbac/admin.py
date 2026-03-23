"""
RBAC Admin Configuration.
"""

from django.contrib import admin
from .models import Permission, RolePermission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'resource', 'action']
    list_filter = ['resource', 'action']
    search_fields = ['name', 'code']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'is_granted']
    list_filter = ['role', 'is_granted']
    raw_id_fields = ['permission']