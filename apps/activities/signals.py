"""
Activities Signals - Create timeline events for score and attendance.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(pre_save, sender='activities.Score')
def score_pre_save(sender, instance, **kwargs):
    """
    Before saving a score, check if it's being updated.
    If so, store the previous score for audit logging.
    """
    if instance.pk:
        try:
            old_instance = Score.objects.get(pk=instance.pk)
            instance.previous_score = old_instance.score
        except Score.DoesNotExist:
            pass


@receiver(post_save, sender='activities.Score')
def create_timeline_event_for_score(sender, instance, created, **kwargs):
    """
    Create a timeline event when a new score is entered.
    
    This implements the requirement from sakti.md:
    "Timeline: Mengirimkan sinyal (Signal) ke feed wali jika ada input nilai atau absen baru."
    """
    if created:
        # Create timeline event
        TimelineEvent.objects.create(
            tenant=instance.tenant,
            event_type='score',
            title=f"Nilai Baru: {instance.title}",
            description=f"Nilai {instance.subject.name}: {instance.score}/{instance.max_score}",
            score=instance,
            classroom=instance.classroom,
            created_by=instance.recorded_by,
            published=True,
            published_at=timezone.now()
        )
        
        # Create notifications for linked parents
        _create_parent_notifications(instance.tenant, instance.student, 'score')


@receiver(post_save, sender='activities.Attendance')
def create_timeline_event_for_attendance(sender, instance, created, **kwargs):
    """
    Create a timeline event when attendance is recorded.
    
    Only create timeline for non-present statuses or late arrivals
    to avoid spamming parents with "present" notifications.
    """
    if created and instance.status != 'present':
        # Create timeline event
        TimelineEvent.objects.create(
            tenant=instance.tenant,
            event_type='attendance',
            title=f"Status Absensi: {instance.get_status_display()}",
            description=f"{instance.student.get_full_name()} - {instance.date}",
            attendance=instance,
            classroom=instance.classroom,
            created_by=instance.recorded_by,
            published=True,
            published_at=timezone.now()
        )
        
        # Create notifications for linked parents
        _create_parent_notifications(instance.tenant, instance.student, 'attendance')


def _create_parent_notifications(tenant, student, event_type):
    """
    Helper function to create notifications for linked parents.
    """
    try:
        from apps.smart_linking.models import ParentStudentLink
        
        # Get linked parents
        links = ParentStudentLink.objects.filter(
            student=student,
            is_verified=True
        ).select_related('parent')
        
        for link in links:
            # Get or create timeline event
            timeline_event = TimelineEvent.objects.filter(
                tenant=tenant,
                event_type=event_type
            ).order_by('-created_at').first()
            
            if timeline_event:
                TimelineNotification.objects.get_or_create(
                    timeline_event=timeline_event,
                    parent=link.parent
                )
    except ImportError:
        # If smart_linking is not available, skip
        pass


# Import models for use in signals
from .models import TimelineEvent, TimelineNotification, Score, Attendance