"""
Academic Signals - Handle model events.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save)
def handle_enrollment_created(sender, instance, created, **kwargs):
    """Handle new enrollment creation."""
    if created and kwargs.get('raw'):
        return
    
    if sender.__name__ == 'Enrollment' and created:
        # Emit notification or log event
        pass