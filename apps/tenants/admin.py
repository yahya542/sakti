"""
Tenant Admin Configuration
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Tenant, Domain


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model."""
    
    list_display = ['name', 'kode_instansi', 'slug', 'plan', 'is_active', 'created_at']
    list_filter = ['is_active', 'plan', 'created_at']
    search_fields = ['name', 'kode_instansi', 'slug', 'email']
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Informasi Dasar'), {
            'fields': ('name', 'kode_instansi', 'slug', 'sub_brand_name')
        }),
        (_('Kontak'), {
            'fields': ('email', 'phone', 'address', 'custom_domain')
        }),
        (_('Branding'), {
            'fields': ('logo', 'favicon', 'primary_color', 'secondary_color', 'theme_config')
        }),
        (_('Status & Paket'), {
            'fields': ('is_active', 'plan', 'paid_until')
        }),
    )
    
    prepopulated_fields = {'slug': ('kode_instansi',)}


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """Admin interface for Domain model."""
    
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['domain', 'tenant__name']