"""
Tenant Serializers - API serialization for tenant data.
"""

from rest_framework import serializers
from .models import Tenant, Domain


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model."""
    
    full_brand = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'kode_instansi', 'slug', 'sub_brand_name',
            'email', 'phone', 'address', 'logo', 'favicon',
            'primary_color', 'secondary_color', 'theme_config',
            'custom_domain', 'is_active', 'plan', 'paid_until', 'spp_amount',
            'full_brand', 'display_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_brand', 'kode_instansi', 'slug']


class TenantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new tenants."""
    
    class Meta:
        model = Tenant
        fields = [
            'name', 'kode_instansi', 'slug', 'sub_brand_name',
            'email', 'phone', 'address', 'primary_color', 'secondary_color',
            'plan'
        ]
    
    def validate_kode_instansi(self, value):
        """Validate kode_instansi format."""
        value = value.upper()
        if not value.isalnum():
            raise serializers.ValidationError(
                "Kode Instansi harus alphanumeric (huruf dan angka saja)"
            )
        return value
    
    def create(self, validated_data):
        """Create tenant and default domain."""
        tenant = Tenant.objects.create(**validated_data)
        
        # Create default domain
        domain = f"{validated_data['slug']}.sakti.id"
        Domain.objects.create(
            tenant=tenant,
            domain=domain,
            is_primary=True
        )
        
        return tenant


class DomainSerializer(serializers.ModelSerializer):
    """Serializer for Domain model."""
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Domain
        fields = ['id', 'domain', 'tenant', 'tenant_name', 'is_primary']
        read_only_fields = ['id']