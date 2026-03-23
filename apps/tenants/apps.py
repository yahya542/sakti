from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TenantsConfig(AppConfig):
    """Configuration for Tenants app - Multi-tenancy management."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tenants'
    verbose_name = _('Tenants')

    def ready(self):
        """Initialize app signals and configurations."""
        import apps.tenants.signals  # noqa