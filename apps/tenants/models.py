"""
Tenant Models - Multi-tenancy support for SAKTI
Each tenant represents a school/pesantren with isolated data.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_tenants.models import TenantMixin, DomainMixin


class Tenant(TenantMixin):
    """
    Tenant model representing a school/pesantren.
    Uses schema-based multi-tenancy with PostgreSQL.
    """
    
    # Auto-generated schema will be: SAKTI-[KODE_INSTANSI]
    # Example: SAKTI-UIM, SAKTI-UNESA, SAKTI-ALFALAH
    
    name = models.CharField(
        verbose_name=_('Nama Instansi'),
        max_length=255,
        help_text=_('Nama lengkap sekolah/pesantren')
    )
    
    kode_instansi = models.CharField(
        verbose_name=_('Kode Instansi'),
        max_length=20,
        unique=True,
        help_text=_('Kode unik untuk instansii. Contoh: UIM, UNESA, ALFALAH')
    )
    
    slug = models.SlugField(
        verbose_name=_('Slug'),
        unique=True,
        max_length=50,
        help_text=_('URL-friendly identifier. Contoh: uim, unesa, al-falah')
    )
    
    sub_brand_name = models.CharField(
        verbose_name=_('Nama Sub-brand'),
        max_length=100,
        blank=True,
        help_text=_('Nama brand alternatif yang ditampilkan di dashboard')
    )
    
    # Contact Information
    email = models.EmailField(
        verbose_name=_('Email'),
        blank=True
    )
    phone = models.CharField(
        verbose_name=_('Telepon'),
        max_length=20,
        blank=True
    )
    address = models.TextField(
        verbose_name=_('Alamat'),
        blank=True
    )
    
    # Branding
    logo = models.ImageField(
        verbose_name=_('Logo'),
        upload_to='tenants/logos/',
        blank=True,
        null=True
    )
    favicon = models.ImageField(
        verbose_name=_('Favicon'),
        upload_to='tenants/favicons/',
        blank=True,
        null=True
    )
    
    # Theme Configuration (JSON for dynamic theming)
    primary_color = models.CharField(
        verbose_name=_('Warna Primer'),
        max_length=7,
        default='#3B82F6',
        help_text=_('Hex color code. Contoh: #3B82F6')
    )
    
    secondary_color = models.CharField(
        verbose_name=_('Warna Sekunder'),
        max_length=7,
        default='#8B5CF6',
        help_text=_('Hex color code. Contoh: #8B5CF6')
    )
    
    theme_config = models.JSONField(
        verbose_name=_('Konfigurasi Tema'),
        default=dict,
        blank=True,
        help_text=_('Konfigurasi tema tambahan untuk white-labeling')
    )
    
    # Custom Domain
    custom_domain = models.CharField(
        verbose_name=_('Custom Domain'),
        max_length=255,
        blank=True,
        help_text=_('Domain kustom. Contoh: sakti.uim.ac.id')
    )
    
    # Status
    is_active = models.BooleanField(
        verbose_name=_('Aktif'),
        default=True,
        help_text=_('Non-aktifkan untuk menonaktifkan akses')
    )
    
    # Metadata
    created_at = models.DateTimeField(
        verbose_name=_('Dibuat'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_('Diperbarui'),
        auto_now=True
    )
    
    # Paid Plan
    plan = models.CharField(
        verbose_name=_('Paket Langganan'),
        max_length=50,
        choices=[
            ('free', _('Gratis')),
            ('basic', _('Basic')),
            ('premium', _('Premium')),
            ('enterprise', _('Enterprise')),
        ],
        default='free'
    )
    
    # Grace period for deactivated tenants
    paid_until = models.DateField(
        verbose_name=_('Dibayar Sampai'),
        null=True,
        blank=True
    )
    
    # SPP Configuration
    spp_amount = models.DecimalField(
        verbose_name=_('Jumlah SPP Bulanan'),
        max_digits=12,
        decimal_places=2,
        default=500000,
        help_text=_('Jumlah SPP default per bulan')
    )
    
    class Meta:
        verbose_name = _('Tenant')
        verbose_name_plural = _('Tenants')
        ordering = ['name']
    
    def __str__(self):
        return f"SAKTI-{self.kode_instansi}"
    
    def save(self, *args, **kwargs):
        if not self.schema_name:
            self.schema_name = f"SAKTI-{self.kode_instansi.upper()}"
        super().save(*args, **kwargs)
    
    @property
    def display_name(self):
        """Return the brand name for display."""
        return self.sub_brand_name or self.name
    
    @property
    def full_brand(self):
        """Return full SAKTI brand with kode."""
        return f"SAKTI-{self.kode_instansi}"


class Domain(DomainMixin):
    """
    Domain configuration for each tenant.
    Maps subdomain to tenant.
    """
    
    is_primary = models.BooleanField(
        verbose_name=_('Domain Utama'),
        default=True
    )
    
    class Meta:
        verbose_name = _('Domain')
        verbose_name_plural = _('Domains')
    
    def __str__(self):
        return self.domain