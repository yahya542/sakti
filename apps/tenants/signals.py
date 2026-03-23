"""
Tenant Signals - Auto-create signals for tenant lifecycle.
"""

from django.db import connection
from django_tenants.utils import get_tenant_model
from django.core.management import call_command
from django.dispatch import receiver
from django_tenants.signals import post_schema_sync, schema_migrated


@receiver(post_schema_sync)
def on_tenant_created(sender, tenant, **kwargs):
    """
    Execute after new tenant is created and schema is synced.
    Automatically run migrations and create initial data.
    """
    # Run migrations for tenant schema
    # Note: django-tenants handles this automatically
    pass


def create_tenant_initial_data(tenant):
    """
    Create initial data for new tenant.
    Called after tenant schema is ready.
    """
    pass  # Initial data will be created via migrations