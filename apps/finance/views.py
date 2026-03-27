"""
Finance Views.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Invoice, Payment, PaymentGatewayConfig
from .serializers import (
    InvoiceSerializer,
    InvoiceCreateSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentGatewayConfigSerializer,
    GenerateSPPSerializer,
    PaymentGatewayInitSerializer,
)
from .signals import generate_monthly_spp


@extend_schema_view(
    list=extend_schema(
        tags=['Finance'],
        summary='List invoices',
        description='Get a paginated list of all invoices. Filter by status, type, month, or year.'
    ),
    create=extend_schema(
        tags=['Finance'],
        summary='Create invoice',
        description='Create a new invoice. Requires admin privileges.'
    ),
    retrieve=extend_schema(
        tags=['Finance'],
        summary='Get invoice details',
        description='Get detailed information about a specific invoice.'
    ),
    update=extend_schema(
        tags=['Finance'],
        summary='Update invoice',
        description='Update invoice information. Requires admin privileges.'
    ),
    destroy=extend_schema(
        tags=['Finance'],
        summary='Delete invoice',
        description='Delete an invoice. Requires admin privileges.'
    )
)

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invoices.
    
    Admins can create and manage all invoices.
    Parents can view their children's invoices.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'invoice_type', 'month', 'year']
    search_fields = ['invoice_number', 'student__first_name', 'student__last_name', 'title']
    ordering_fields = ['created_at', 'due_date', 'amount']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Get tenant
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return Invoice.objects.none()
        
        queryset = Invoice.objects.filter(tenant=tenant)
        
        # Filter based on role
        if user.role == 'parent':
            # Parents can see their children's invoices
            from apps.smart_linking.models import ParentStudentLink
            student_ids = ParentStudentLink.objects.filter(
                parent=user
            ).values_list('student_id', flat=True)
            queryset = queryset.filter(student_id__in=student_ids)
        
        elif user.role == 'student':
            # Students can only see their own invoices
            queryset = queryset.filter(student=user)
        
        return queryset
    
    @extend_schema(
        tags=['Finance'],
        summary='Generate SPP invoices',
        description='Generate SPP invoices for all students in the current month/year.'
    )
    @action(detail=False, methods=['post'])
    def generate_spp(self, request):
        """
        Generate SPP invoices for all students.
        """
        if request.user.role not in ['admin', 'super_admin']:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = GenerateSPPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response(
                {'error': 'Tenant not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update SPP amount if provided
        if serializer.validated_data.get('amount'):
            tenant.spp_amount = serializer.validated_data['amount']
            tenant.save(update_fields=['spp_amount'])
        
        invoices_created = generate_monthly_spp(
            tenant,
            serializer.validated_data['month'],
            serializer.validated_data['year']
        )
        
        return Response(
            {'message': f'{invoices_created} invoice SPP dibuat'},
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        tags=['Finance'],
        summary='Get invoice payments',
        description='Get all payments for a specific invoice.'
    )
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all payments for an invoice."""
        try:
            invoice = self.get_queryset().get(pk=pk)
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        payments = invoice.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['Finance'],
        summary='List payments',
        description='Get a paginated list of all payments. Filter by status, method, or gateway.'
    ),
    create=extend_schema(
        tags=['Finance'],
        summary='Create payment',
        description='Record a new payment.'
    ),
    retrieve=extend_schema(
        tags=['Finance'],
        summary='Get payment details',
        description='Get detailed information about a specific payment.'
    ),
    update=extend_schema(
        tags=['Finance'],
        summary='Update payment',
        description='Update payment information.'
    ),
    destroy=extend_schema(
        tags=['Finance'],
        summary='Delete payment',
        description='Delete a payment record.'
    )
)
class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payments.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'gateway']
    search_fields = ['payment_number', 'invoice__invoice_number']
    ordering_fields = ['created_at', 'paid_at']
    
    def get_queryset(self):
        user = self.request.user
        
        # Get tenant
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return Payment.objects.none()
        
        queryset = Payment.objects.filter(tenant=tenant)
        
        # Filter based on role
        if user.role == 'parent':
            # Parents can see their own payments
            queryset = queryset.filter(paid_by=user)
        
        elif user.role == 'student':
            # Students can see payments for their invoices
            queryset = queryset.filter(invoice__student=user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    @extend_schema(
        tags=['Finance'],
        summary='Initialize payment gateway',
        description='Initialize payment via Midtrans or Xendit gateway.'
    )
    @action(detail=False, methods=['post'])
    def init_gateway(self, request):
        """
        Initialize payment via gateway (Midtrans/Xendit).
        """
        serializer = PaymentGatewayInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get invoice
        invoice = Invoice.objects.get(id=serializer.validated_data['invoice_id'])
        
        # Get payment config
        try:
            config = PaymentGatewayConfig.objects.get(
                tenant=invoice.tenant,
                is_active=True
            )
        except PaymentGatewayConfig.DoesNotExist:
            return Response(
                {'error': 'Payment gateway not configured'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine which gateway to use
        gateway = None
        if config.midtrans_enabled:
            gateway = 'midtrans'
        elif config.xendit_enabled:
            gateway = 'xendit'
        
        if not gateway:
            return Response(
                {'error': 'No payment gateway enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment record
        payment = Payment.objects.create(
            tenant=invoice.tenant,
            invoice=invoice,
            amount=invoice.amount,
            payment_method=serializer.validated_data['payment_method'],
            gateway=gateway,
            status='pending'
        )
        
        # Call gateway API (placeholder - implement actual integration)
        gateway_response = _initiate_gateway_payment(payment, config, gateway)
        
        if gateway_response:
            payment.gateway_order_id = gateway_response.get('order_id')
            payment.gateway_payment_id = gateway_response.get('payment_id')
            payment.gateway_response = gateway_response
            payment.save()
            
            return Response({
                'payment_number': payment.payment_number,
                'gateway': gateway,
                'payment_url': gateway_response.get('payment_url'),
                'va_number': gateway_response.get('va_number'),
            })
        
        payment.status = 'failed'
        payment.save()
        
        return Response(
            {'error': 'Failed to initiate payment'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _initiate_gateway_payment(payment, config, gateway):
    """
    Helper function to initiate payment with the gateway.
    This is a placeholder - implement actual Midtrans/Xendit integration.
    """
    if gateway == 'midtrans':
        return _initiate_midtrans(payment, config)
    elif gateway == 'xendit':
        return _initiate_xendit(payment, config)
    return None


def _initiate_midtrans(payment, config):
    """Placeholder for Midtrans integration."""
    # Implement actual Midtrans API call here
    # https://docs.midtrans.com/reference/create-transaction
    return {
        'order_id': f'INV-{payment.payment_number}',
        'payment_id': f'PAY-{payment.payment_number}',
        'payment_url': 'https://app.midtrans.com/some-payment-page',
    }


def _initiate_xendit(payment, config):
    """Placeholder for Xendit integration."""
    # Implement actual Xendit API call here
    # https://docs.xendit.co/id/reference/create-invoice
    return {
        'order_id': payment.payment_number,
        'payment_id': f'PAY-{payment.payment_number}',
        'payment_url': 'https://checkout.xendit.co/some-invoice',
    }


@extend_schema_view(
    list=extend_schema(
        tags=['Finance'],
        summary='List payment gateway configs',
        description='Get a list of payment gateway configurations.'
    ),
    create=extend_schema(
        tags=['Finance'],
        summary='Create payment gateway config',
        description='Create a new payment gateway configuration.'
    ),
    retrieve=extend_schema(
        tags=['Finance'],
        summary='Get payment gateway config',
        description='Get detailed information about a payment gateway configuration.'
    ),
    update=extend_schema(
        tags=['Finance'],
        summary='Update payment gateway config',
        description='Update payment gateway configuration.'
    ),
    destroy=extend_schema(
        tags=['Finance'],
        summary='Delete payment gateway config',
        description='Delete a payment gateway configuration.'
    )
)
class PaymentGatewayConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment gateway configuration.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentGatewayConfigSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role not in ['admin', 'super_admin']:
            return PaymentGatewayConfig.objects.none()
        
        tenant = getattr(user, 'tenant', None)
        if not tenant:
            return PaymentGatewayConfig.objects.none()
        
        return PaymentGatewayConfig.objects.filter(tenant=tenant)
    
    def perform_create(self, serializer):
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)