"""
Smart Linking App Configuration.
"""

from django.apps import AppConfig


class SmartLinkingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.smart_linking'
    verbose_name = 'Smart Linking'
    
    def ready(self):
        import apps.smart_linking.signals  # noqa