"""
Finance Models - Invoicing, Payments, Payment Gateway Integration.
"""

from django.db import models
from django.conf import settings
import uuid


class Invoice(models.Model):
    """
    Model for invoices/bills to parents.
    Supports automatic SPP billing and manual invoices.
    """
    INVOICE_TYPES = [
        ('spp', 'SPP Bulanan'),
        ('registration', 'Registrasi'),
        ('book', 'Buku'),
        ('uniform', 'Seragam'),
        ('activity', ' Kegiatan'),
        ('other', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Menunggu Pembayaran'),
        ('paid', 'Lunas'),
        ('overdue', 'Jatuh Tempo'),
        ('cancelled', 'Dibatalkan'),
    ]
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    invoice_number = models.CharField(
        max_length=50,
        unique=True
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices',
        limit_choices_to={'role': 'student'}
    )
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_invoices',
        limit_choices_to={'role': 'parent'}
    )
    invoice_type = models.CharField(
        max_length=20,
        choices=INVOICE_TYPES,
        default='spp'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # For SPP - month and year
    month = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Bulan (1-12) untuk SPP'
    )
    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Tahun untuk SPP'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'finance_invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoice'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['student']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.student.get_full_name()} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate unique invoice number."""
        prefix = f"INV-{self.tenant.sub_brand_slug.upper() if self.tenant else 'SCH'}"
        year = timezone.now().year
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"{prefix}-{year}-{unique_id}"


class Payment(models.Model):
    """
    Model for payment transactions.
    Integrates with Midtrans/Xendit.
    """
    PAYMENT_METHODS = [
        ('transfer', 'Transfer Bank'),
        ('va', 'Virtual Account'),
        ('credit_card', 'Kartu Kredit'),
        ('e_wallet', 'E-Wallet'),
        ('qris', 'QRIS'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('processing', 'Diproses'),
        ('success', 'Berhasil'),
        ('failed', 'Gagal'),
        ('refunded', 'Dikembalikan'),
    ]
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payment_number = models.CharField(
        max_length=50,
        unique=True
    )
    
    # Payment details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Payment gateway integration
    gateway = models.CharField(
        max_length=20,
        choices=[
            ('midtrans', 'Midtrans'),
            ('xendit', 'Xendit'),
        ],
        null=True,
        blank=True
    )
    gateway_order_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Order ID dari payment gateway'
    )
    gateway_payment_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Payment ID dari payment gateway'
    )
    gateway_response = models.JSONField(
        null=True,
        blank=True,
        help_text='Response lengkap dari payment gateway'
    )
    
    # Payment evidence
    payment_proof = models.ImageField(
        upload_to='payment_proofs/',
        null=True,
        blank=True
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Parent who made the payment
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments_made'
    )
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'finance_payments'
        verbose_name = 'Pembayaran'
        verbose_name_plural = 'Pembayaran'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_number']),
            models.Index(fields=['status']),
            models.Index(fields=['gateway']),
            models.Index(fields=['invoice']),
            models.Index(fields=['paid_by']),
        ]
    
    def __str__(self):
        return f"{self.payment_number} - {self.invoice.invoice_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = self.generate_payment_number()
        super().save(*args, **kwargs)
    
    def generate_payment_number(self):
        """Generate unique payment number."""
        prefix = f"PAY-{self.tenant.sub_brand_slug.upper() if self.tenant else 'SCH'}"
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"{prefix}-{unique_id}"


class PaymentGatewayConfig(models.Model):
    """
    Model to store payment gateway configuration per tenant.
    Supports Midtrans and Xendit.
    """
    tenant = models.OneToOneField(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='payment_config'
    )
    
    # Midtrans configuration
    midtrans_merchant_id = models.CharField(
        max_length=100,
        blank=True
    )
    midtrans_client_key = models.CharField(
        max_length=200,
        blank=True
    )
    midtrans_server_key = models.CharField(
        max_length=200,
        blank=True
    )
    midtrans_is_production = models.BooleanField(
        default=False
    )
    midtrans_enabled = models.BooleanField(
        default=False
    )
    
    # Xendit configuration
    xendit_api_key = models.CharField(
        max_length=200,
        blank=True
    )
    xendit_is_production = models.BooleanField(
        default=False
    )
    xendit_enabled = models.BooleanField(
        default=False
    )
    
    # Common settings
    callback_secret = models.CharField(
        max_length=100,
        blank=True,
        help_text='Secret untuk verifikasi callback'
    )
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'finance_payment_config'
        verbose_name = 'Konfigurasi Payment Gateway'
        verbose_name_plural = 'Konfigurasi Payment Gateway'
    
    def __str__(self):
        return f"Payment Config - {self.tenant.name}"


# Import timezone
from django.utils import timezone