"""
Activities URL Configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceViewSet,
    ScoreViewSet,
    TimelineEventViewSet,
    TimelineNotificationViewSet,
)

router = DefaultRouter()

router.register(r'attendances', AttendanceViewSet, basename='attendance')
router.register(r'scores', ScoreViewSet, basename='score')
router.register(r'timeline', TimelineEventViewSet, basename='timeline-event')
router.register(r'notifications', TimelineNotificationViewSet, basename='timeline-notification')

urlpatterns = [
    path('', include(router.urls)),
]