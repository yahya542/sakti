"""
Finance Admin Configuration.
"""

from django.contrib import admin
from .models import Invoice, Payment, PaymentGatewayConfig


class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number',
        'student',
        'invoice_type',
        'title',
        'amount',
        'due_date',
        'status',
    ]
    list_filter = [
        'invoice_type',
        'status',
        'month',
        'year',
    ]
    search_fields = [
        'invoice_number',
        'student__first_name',
        'student__last_name',
        'title',
    ]
    raw_id_fields = ['student', 'parent', 'created_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    actions = ['mark_as_paid', 'mark_as_overdue']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
        self.message_user(request, f'{queryset.count()} invoice ditandai lunas.')
    
    mark_as_paid.short_description = 'Tandai lunas'
    
    def mark_as_overdue(self, queryset):
        queryset.update(status='overdue')
        self.message_user(request, f'{queryset.count()} invoice ditandai jatuh tempo.')
    
    mark_as_overdue.short_description = 'Tandai jatuh tempo'


class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_number',
        'invoice',
        'amount',
        'payment_method',
        'status',
        'gateway',
        'paid_by',
    ]
    list_filter = [
        'status',
        'payment_method',
        'gateway',
    ]
    search_fields = [
        'payment_number',
        'invoice__invoice_number',
    ]
    raw_id_fields = ['invoice', 'paid_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


class PaymentGatewayConfigAdmin(admin.ModelAdmin):
    list_display = [
        'tenant',
        'midtrans_enabled',
        'xendit_enabled',
        'is_active',
    ]
    list_filter = [
        'midtrans_enabled',
        'xendit_enabled',
        'is_active',
    ]
    
    fieldsets = (
        ('Midtrans', {
            'fields': (
                'midtrans_merchant_id',
                'midtrans_client_key',
                'midtrans_server_key',
                'midtrans_is_production',
                'midtrans_enabled',
            )
        }),
        ('Xendit', {
            'fields': (
                'xendit_api_key',
                'xendit_is_production',
                'xendit_enabled',
            )
        }),
        ('Settings', {
            'fields': (
                'tenant',
                'callback_secret',
                'is_active',
            )
        }),
    )


admin.register(Invoice, InvoiceAdmin)
admin.register(Payment, PaymentAdmin)
admin.register(PaymentGatewayConfig, PaymentGatewayConfigAdmin)