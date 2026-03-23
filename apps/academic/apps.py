"""
Academic App Configuration.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AcademicConfig(AppConfig):
    """Configuration for Academic app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.academic'
    verbose_name = _('Academic')
    
    def ready(self):
        """Initialize app signals."""
        import apps.academic.signals  # noqa