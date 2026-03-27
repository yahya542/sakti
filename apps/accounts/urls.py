"""
Account URL Configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView, RefreshTokenView, RegisterView,
    UserViewSet, UserListView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Authentication endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # User endpoints
    path('users/list/', UserListView.as_view(), name='user_list'),
    
    # Router URLs
    path('', include(router.urls)),
]