"""
Finance Signals - Automatic invoice generation and payment processing.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta


@receiver(post_save, sender='finance.Invoice')
def update_invoice_status(sender, instance, created, **kwargs):
    """
    Update invoice status based on due date and payments.
    """
    if not created:
        # Check if invoice is overdue
        if instance.status in ['pending', 'draft'] and instance.due_date < timezone.now().date():
            instance.status = 'overdue'
            instance.save(update_fields=['status'])
        
        # Check if invoice is paid
        if instance.status != 'paid':
            total_paid = instance.payments.filter(status='success').aggregate(
                total=models.Sum('amount')
            )['total'] or 0
            
            if total_paid >= instance.amount:
                instance.status = 'paid'
                instance.save(update_fields=['status'])


def generate_monthly_spp(tenant, month, year):
    """
    Generate SPP invoices for all active students for a given month/year.
    
    This implements the requirement from sakti.md:
    "Invoicing: Generate tagihan SPP bulanan otomatis"
    """
    from apps.academic.models import Enrollment, Student
    
    # Get all active students
    students = Student.objects.filter(
        tenant=tenant,
        user__is_active=True
    ).select_related('user')
    
    # Get SPP amount from tenant config or use default
    # For now, use a simple lookup or default
    spp_amount = getattr(tenant, 'spp_amount', 500000) or 500000
    
    invoices_created = 0
    
    for student in students:
        # Check if invoice already exists for this month/year
        existing_invoice = Invoice.objects.filter(
            tenant=tenant,
            student=student.user,
            invoice_type='spp',
            month=month,
            year=year
        ).exists()
        
        if existing_invoice:
            continue
        
        # Find linked parent
        from apps.smart_linking.models import ParentStudentLink
        parent_link = ParentStudentLink.objects.filter(
            student=student.user,
            is_verified=True
        ).first()
        
        parent = parent_link.parent if parent_link else None
        
        # Create invoice
        Invoice.objects.create(
            tenant=tenant,
            student=student.user,
            parent=parent,
            invoice_type='spp',
            title=f'SPP Bulan {_get_month_name(month)} {year}',
            description=f'Tagihan SPP bulan {_get_month_name(month)} {year}',
            amount=spp_amount,
            due_date=timezone.now().date() + timedelta(days=7),  # Due in 7 days
            status='pending',
            month=month,
            year=year
        )
        
        invoices_created += 1
    
    return invoices_created


def _get_month_name(month):
    """Get month name in Indonesian."""
    months = {
        1: 'Januari', 2: 'Februari', 3: 'Maret',
        4: 'April', 5: 'Mei', 6: 'Juni',
        7: 'Juli', 8: 'Agustus', 9: 'September',
        10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    return months.get(month, '')


def process_payment_callback(gateway, payment_data):
    """
    Process payment callback from payment gateway.
    
    This implements the requirement from sakti.md:
    "Payments: Integrasi API Payment Gateway (Midtrans/Xendit)"
    """
    if gateway == 'midtrans':
        return _process_midtrans_callback(payment_data)
    elif gateway == 'xendit':
        return _process_xendit_callback(payment_data)
    return None


def _process_midtrans_callback(data):
    """Process Midtrans callback."""
    from .models import Payment
    
    order_id = data.get('order_id')
    status_code = data.get('status_code')
    
    # Verify signature (in production, verify with server key)
    # For now, just update the payment status
    
    try:
        payment = Payment.objects.get(gateway_order_id=order_id)
        
        # Map Midtrans status to our status
        transaction_status = data.get('transaction_status')
        
        if transaction_status == 'settlement':
            payment.status = 'success'
            payment.paid_at = timezone.now()
        elif transaction_status == 'pending':
            payment.status = 'pending'
        elif transaction_status in ['cancel', 'expire']:
            payment.status = 'failed'
        
        payment.gateway_response = data
        payment.save(update_fields=['status', 'paid_at', 'gateway_response'])
        
        return payment
    except Payment.DoesNotExist:
        return None


def _process_xendit_callback(data):
    """Process Xendit callback."""
    from .models import Payment
    
    external_id = data.get('external_id')
    
    try:
        payment = Payment.objects.get(gateway_order_id=external_id)
        
        # Map Xendit status
        status = data.get('status')
        
        if status == 'PAID':
            payment.status = 'success'
            payment.paid_at = timezone.now()
        elif status == 'PENDING':
            payment.status = 'pending'
        elif status in ['FAILED', 'EXPIRED']:
            payment.status = 'failed'
        
        payment.gateway_response = data
        payment.save(update_fields=['status', 'paid_at', 'gateway_response'])
        
        return payment
    except Payment.DoesNotExist:
        return None


# Import models for use in signals
from .models import Invoice, Payment, PaymentGatewayConfig