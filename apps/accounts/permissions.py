"""
Custom permissions for SAKTI.
"""

from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admins to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.role in [User.ROLE_SUPER_ADMIN, User.ROLE_ADMIN]:
            return True
        
        # Owner can access their own objects
        return obj == request.user or obj.user == request.user


class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admins.
    """
    
    def has_permission(self, request, view):
        return request.user.role in [User.ROLE_SUPER_ADMIN, User.ROLE_ADMIN]


class IsTeacher(permissions.BasePermission):
    """
    Permission to only allow teachers.
    """
    
    def has_permission(self, request, view):
        return request.user.role == User.ROLE_TEACHER


class IsStudent(permissions.BasePermission):
    """
    Permission to only allow students.
    """
    
    def has_permission(self, request, view):
        return request.user.role == User.ROLE_STUDENT


class IsParent(permissions.BasePermission):
    """
    Permission to only allow parents.
    """
    
    def has_permission(self, request, view):
        return request.user.role == User.ROLE_PARENT


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Permission for teachers and admins.
    """
    
    def has_permission(self, request, view):
        return request.user.role in [
            User.ROLE_TEACHER, User.ROLE_ADMIN, User.ROLE_SUPER_ADMIN
        ]


class IsStudentOrParent(permissions.BasePermission):
    """
    Permission for students and parents.
    """
    
    def has_permission(self, request, view):
        return request.user.role in [User.ROLE_STUDENT, User.ROLE_PARENT]


class CanManageUsers(permissions.BasePermission):
    """
    Permission to manage users - for admins only.
    """
    
    def has_permission(self, request, view):
        return request.user.role in [User.ROLE_SUPER_ADMIN, User.ROLE_ADMIN]
    
    def has_object_permission(self, request, view, obj):
        # Super admin can manage all
        if request.user.role == User.ROLE_SUPER_ADMIN:
            return True
        
        # Admin can manage users in their tenant
        if request.user.role == User.ROLE_ADMIN:
            if hasattr(obj, 'tenant'):
                return obj.tenant == request.user.tenant
            if hasattr(obj, 'user') and hasattr(obj.user, 'tenant'):
                return obj.user.tenant == request.user.tenant
            return True
        
        return False