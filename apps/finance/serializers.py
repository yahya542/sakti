"""
Finance Serializers.
"""

from rest_framework import serializers
from .models import Invoice, Payment, PaymentGatewayConfig


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Invoice model.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    paid_amount = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id',
            'tenant',
            'invoice_number',
            'student',
            'student_name',
            'parent',
            'parent_name',
            'invoice_type',
            'title',
            'description',
            'amount',
            'due_date',
            'status',
            'month',
            'year',
            'created_by',
            'created_by_name',
            'paid_amount',
            'remaining_amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'invoice_number', 'created_at', 'updated_at'
        ]
    
    def get_paid_amount(self, obj):
        """Get total amount paid for this invoice."""
        return obj.payments.filter(status='success').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    
    def get_remaining_amount(self, obj):
        """Get remaining amount to be paid."""
        paid = self.get_paid_amount(obj)
        return obj.amount - paid


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Invoice.
    """
    student_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'student_id',
            'invoice_type',
            'title',
            'description',
            'amount',
            'due_date',
            'month',
            'year',
        ]
    
    def validate(self, data):
        """Validate that student exists and has parent link."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            student = User.objects.get(id=data['student_id'], role='student')
        except User.DoesNotExist:
            raise serializers.ValidationError("Siswa tidak ditemukan.")
        
        # Find parent link
        from apps.smart_linking.models import ParentStudentLink
        parent_link = ParentStudentLink.objects.filter(
            student=student,
            is_verified=True
        ).first()
        
        if parent_link:
            data['parent'] = parent_link.parent
        else:
            # For manual invoices, parent is optional
            pass
        
        data['student'] = student
        return data
    
    def create(self, validated_data):
        validated_data.pop('student_id', None)
        tenant = getattr(self.context['request'].user, 'tenant', None)
        validated_data['tenant'] = tenant
        validated_data['created_by'] = self.context['request'].user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model.
    """
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    student_name = serializers.CharField(source='invoice.student.get_full_name', read_only=True)
    paid_by_name = serializers.CharField(source='paid_by.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'tenant',
            'invoice',
            'invoice_number',
            'student_name',
            'payment_number',
            'amount',
            'payment_method',
            'status',
            'gateway',
            'gateway_order_id',
            'gateway_payment_id',
            'payment_proof',
            'paid_at',
            'paid_by',
            'paid_by_name',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'payment_number', 'gateway_order_id', 'gateway_payment_id',
            'paid_at', 'created_at', 'updated_at'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Payment.
    """
    class Meta:
        model = Payment
        fields = [
            'invoice',
            'amount',
            'payment_method',
            'payment_proof',
            'notes',
        ]
    
    def validate(self, data):
        """Validate payment amount and invoice."""
        invoice = data['invoice']
        
        # Check if amount matches invoice
        if data['amount'] != invoice.amount:
            raise serializers.ValidationError(
                f"Jumlah pembayaran harus sesuai dengan tagihan: {invoice.amount}"
            )
        
        # Check if invoice is already paid
        if invoice.status == 'paid':
            raise serializers.ValidationError("Invoice sudah lunas.")
        
        return data
    
    def create(self, validated_data):
        tenant = getattr(self.context['request'].user, 'tenant', None)
        validated_data['tenant'] = tenant
        validated_data['paid_by'] = self.context['request'].user
        
        # For manual payments, set status to success directly
        if validated_data.get('payment_proof'):
            validated_data['status'] = 'success'
            validated_data['paid_at'] = timezone.now()
        
        return super().create(validated_data)


class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentGatewayConfig model.
    """
    class Meta:
        model = PaymentGatewayConfig
        fields = [
            'id',
            'tenant',
            'midtrans_merchant_id',
            'midtrans_client_key',
            'midtrans_is_production',
            'midtrans_enabled',
            'xendit_api_key',
            'xendit_is_production',
            'xendit_enabled',
            'callback_secret',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'midtrans_server_key': {'write_only': True},
            'xendit_api_key': {'write_only': True},
            'callback_secret': {'write_only': True},
        }


class GenerateSPPSerializer(serializers.Serializer):
    """
    Serializer for generating SPP invoices.
    """
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=2020, max_value=2100)
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        help_text="Jumlah SPP per siswa (opsional)"
    )


class PaymentGatewayInitSerializer(serializers.Serializer):
    """
    Serializer for initiating payment via gateway.
    """
    invoice_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=['va', 'credit_card', 'e_wallet', 'qris']
    )
    
    def validate_invoice_id(self, value):
        from .models import Invoice
        try:
            invoice = Invoice.objects.get(id=value)
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("Invoice tidak ditemukan.")
        
        if invoice.status == 'paid':
            raise serializers.ValidationError("Invoice sudah lunas.")
        
        return value


# Import Django models for aggregation
from django.db import models
from django.utils import timezone