"""
Account Views - Authentication and User management endpoints.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
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

User = get_user_model()

# --- 1. AUTHENTICATION SECTION ---
# Mengelompokkan semua yang berkaitan dengan akses (Login, Register, Token)

@extend_schema(tags=['Authentication'])
class LoginView(APIView):
    """User login endpoint."""
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary='User login',
        description='Authenticate user with email and password.',
        request=LoginSerializer,
        responses={200: TokenSerializer}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if not user or not user.is_active:
            return Response({'error': 'Kredensial tidak valid.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login_at'])
        
        return Response({
            'access': generate_access_token(user),
            'refresh': generate_refresh_token(user),
            'user': UserSerializer(user).data
        })

@extend_schema(tags=['Authentication'])
class RefreshTokenView(APIView):
    """Refresh access token endpoint."""
    permission_classes = [AllowAny]
    
    @extend_schema(summary='Refresh access token', responses={200: TokenSerializer})
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token diperlukan.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = verify_refresh_token(refresh_token)
            return Response({
                'access': generate_access_token(user),
                'user': UserSerializer(user).data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(tags=['Authentication'])
class RegisterView(generics.CreateAPIView):
    """Public registration endpoint."""
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(summary='User registration')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


# --- 2. ACCOUNTS SECTION ---
# Mengelompokkan manajemen profil dan data user

@extend_schema_view(
    list=extend_schema(tags=['Accounts'], summary='List all users'),
    create=extend_schema(tags=['Accounts'], summary='Create new user'),
    retrieve=extend_schema(tags=['Accounts'], summary='Get user details'),
    update=extend_schema(tags=['Accounts'], summary='Update user'),
    partial_update=extend_schema(tags=['Accounts'], summary='Partial update user'),
    destroy=extend_schema(tags=['Accounts'], summary='Delete user'),
    me=extend_schema(tags=['Accounts'], summary='Get current user info'),
    change_password=extend_schema(tags=['Authentication'], summary='Change password') # Masuk Auth karena terkait keamanan
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create': return UserCreateSerializer
        if self.action in ['update', 'partial_update']: return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_SUPER_ADMIN:
            return User.objects.all()
        if user.role == User.ROLE_ADMIN:
            return User.objects.filter(Q(tenant=user.tenant) | Q(role=User.ROLE_SUPER_ADMIN)).exclude(role=User.ROLE_SUPER_ADMIN)
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password berhasil diubah.'})

@extend_schema(tags=['Accounts'], summary='List users with filters')
class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        search = self.request.query_params.get('search')
        if role: queryset = queryset.filter(role=role)
        if search:
            queryset = queryset.filter(Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))
        return queryset