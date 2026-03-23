from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    """Configuration for Accounts app - User management."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = _('Accounts')

    def ready(self):
        """Initialize app signals."""
        import apps.accounts.signals  # noqa