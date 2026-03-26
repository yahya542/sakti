"""
Account Serializers - DRF Serializers for User and Profile.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile."""
    
    class Meta:
        model = UserProfile
        fields = [
            'employee_id', 'student_id', 'address',
            'place_of_birth', 'date_of_birth', 'gender'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Full User serializer with profile."""
    
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'photo', 'phone', 'is_active',
            'email_verified', 'last_login_at', 'parent_account',
            'profile', 'date_joined', 
        ]
        read_only_fields = ['id', 'last_login_at', 'date_joined', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role',
            'phone', 'photo', 'profile'
        ]
    
    def validate(self, attrs):
        """Validate password match."""
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Password tidak cocok.'
            })
        return attrs
    
    def create(self, validated_data):
        """Create user and profile."""
        profile_data = validated_data.pop('profile', {})
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            **validated_data
        )
        
        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'photo', 'profile'
        ]
    
    def update(self, instance, validated_data):
        """Update user and profile."""
        profile_data = validated_data.pop('profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile
        if profile_data:
            profile = getattr(instance, 'profile', None)
            if profile:
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()
            else:
                UserProfile.objects.create(user=instance, **profile_data)
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate password match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Password baru tidak cocok.'
            })
        return attrs
    
    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Password saat ini salah.')
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if user exists."""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            # Don't reveal if email exists
            pass
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class TokenSerializer(serializers.Serializer):
    """Serializer for JWT tokens."""
    
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()