"""
Account Signals - Auto-create profile, handle user events, and link parent-student.
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


@receiver(post_save, sender=User)
def link_parent_student_by_no_kk(sender, instance, created, **kwargs):
    """
    Link student and parent accounts based on matching no_kk.
    This runs after a user is created to establish the parent-child relationship.
    """
    if not created:
        return
    
    # Only process students and parents
    if instance.role not in [User.ROLE_STUDENT, User.ROLE_PARENT]:
        return
    
    # Skip if no_kk is not provided
    if not instance.no_kk:
        return
    
    # Find related user with same no_kk but different role
    if instance.role == User.ROLE_STUDENT:
        # Look for parent with same no_kk
        related_user = User.objects.filter(
            no_kk=instance.no_kk,
            role=User.ROLE_PARENT
        ).first()
        
        if related_user:
            instance.parent_account = related_user
            instance.save(update_fields=['parent_account'])
    elif instance.role == User.ROLE_PARENT:
        # Look for students with same no_kk and link them
        students = User.objects.filter(
            no_kk=instance.no_kk,
            role=User.ROLE_STUDENT
        )
        
        for student in students:
            if student.parent_account is None:
                student.parent_account = instance
                student.save(update_fields=['parent_account'])