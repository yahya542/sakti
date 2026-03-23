"""
Smart Linking URL Configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParentStudentLinkViewSet, LinkRequestViewSet, StudentLinkViewSet

router = DefaultRouter()

# Main endpoints
router.register(r'links', ParentStudentLinkViewSet, basename='parent-student-link')
router.register(r'requests', LinkRequestViewSet, basename='link-request')

# Student specific endpoint
router.register(r'student/links', StudentLinkViewSet, basename='student-link')

urlpatterns = [
    path('', include(router.urls)),
]