"""
Account Signals - Auto-create profile and handle user events.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when a new User is created.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(pre_save, sender=User)
def sanitize_user_data(sender, instance, **kwargs):
    """
    Sanitize user data before saving.
    """
    if instance.email:
        instance.email = instance.email.lower().strip()
    
    if instance.first_name:
        instance.first_name = instance.first_name.strip().title()
    
    if instance.last_name:
        instance.last_name = instance.last_name.strip().title()