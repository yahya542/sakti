"""
Account Views - Authentication and User management endpoints.
"""

from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.db.models import Q

from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, LoginSerializer, TokenSerializer
)
from .authentication import (
    generate_access_token, generate_refresh_token, verify_refresh_token
)
from .permissions import IsOwnerOrAdmin

User = get_user_model()


class LoginView(APIView):
    """User login endpoint."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Authenticate user and return tokens."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            return Response(
                {'error': 'Email atau password salah.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Akun dinonaktifkan.'},
                status=status.HTTP_401_UNAUTHORIZED
        )
        
        # Update login info
        user.last_login_at = timezone.now()
        user.last_login_ip = self.get_client_ip(request)
        user.save(update_fields=['last_login_at', 'last_login_ip'])
        
        # Generate tokens
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        
        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': UserSerializer(user).data
        })
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RefreshTokenView(APIView):
    """Refresh access token endpoint."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Refresh access token using refresh token."""
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token diperlukan.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = verify_refresh_token(refresh_token)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        access_token = generate_access_token(user)
        
        return Response({
            'access': access_token,
            'user': UserSerializer(user).data
        })


class UserViewSet(viewsets.ModelViewSet):
    """
    User ViewSet for CRUD operations.
    Only accessible by authenticated users.
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        
        # Super admin sees all users
        if user.role == User.ROLE_SUPER_ADMIN:
            return User.objects.all()
        
        # Admin sees users in their tenant
        if user.role == User.ROLE_ADMIN:
            return User.objects.filter(
                Q(tenant=user.tenant) | Q(role=User.ROLE_SUPER_ADMIN)
            ).exclude(role=User.ROLE_SUPER_ADMIN)
        
        # Others see only their own
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user info."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password berhasil diubah.'
        })


class UserListView(generics.ListAPIView):
    """
    List users with filtering capabilities.
    """
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter users based on role and search query."""
        queryset = User.objects.all()
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset


class RegisterView(generics.CreateAPIView):
    """
    Public registration endpoint for new users.
    Requires admin approval for student/parent accounts.
    """
    
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create new user account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Generate tokens for auto-login
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        
        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': UserSerializer(user).data,
            'message': 'Akun berhasil dibuat. Silakan login.'
        }, status=status.HTTP_201_CREATED)