"""
Finance URL Configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InvoiceViewSet,
    PaymentViewSet,
    PaymentGatewayConfigViewSet,
)

router = DefaultRouter()

router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'payment-config', PaymentGatewayConfigViewSet, basename='payment-config')

urlpatterns = [
    path('', include(router.urls)),
]