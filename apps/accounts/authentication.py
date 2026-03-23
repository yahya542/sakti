"""
Custom JWT Authentication for SAKTI.
"""

import jwt
from datetime import datetime, timedelta
from rest_framework import authentication, exceptions
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT Authentication.
    Token format: { "user_id": xxx, "exp": xxx, "type": "access" }
    """
    
    def authenticate(self, request):
        """Authenticate the request and return (user, token)."""
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            return None
        
        return self.authenticate_token(token)
    
    def authenticate_token(self, token):
        """Validate token and return user."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token telah kedaluwarsa.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Token tidak valid.')
        
        if payload.get('type') != 'access':
            raise exceptions.AuthenticationFailed('Token tidak valid.')
        
        user_id = payload.get('user_id')
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User tidak ditemukan.')
        
        return (user, token)


def generate_access_token(user):
    """Generate JWT access token for user."""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_LIFETIME),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def generate_refresh_token(user):
    """Generate JWT refresh token for user."""
    payload = {
        'user_id': user.id,
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_LIFETIME),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def verify_refresh_token(token):
    """Verify refresh token and return user."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed('Refresh token telah kedaluwarsa.')
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed('Refresh token tidak valid.')
    
    if payload.get('type') != 'refresh':
        raise exceptions.AuthenticationFailed('Token tidak valid.')
    
    user_id = payload.get('user_id')
    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        raise exceptions.AuthenticationFailed('User tidak ditemukan.')
    
    return user