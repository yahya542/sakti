"""
RBAC URL Configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PermissionViewSet, check_permission, my_permissions

router = DefaultRouter()
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    path('check/', check_permission, name='check_permission'),
    path('my-permissions/', my_permissions, name='my_permissions'),
    path('', include(router.urls)),
]