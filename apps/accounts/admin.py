"""
Account Admin Configuration.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin with role management."""
    
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'last_login_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone', 'photo')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important Dates'), {'fields': ('last_login_at', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ['last_login_at', 'date_joined']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile."""
    
    list_display = ['user', 'employee_id', 'student_id', 'date_of_birth', 'gender']
    search_fields = ['user__email', 'employee_id', 'student_id']
    list_filter = ['gender']
    
    raw_id_fields = ['user']