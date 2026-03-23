"""
Smart Linking Signals - Auto-link parent and student based on No KK.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auto_link_parent_student(sender, instance, created, **kwargs):
    """
    Signal to automatically link parent to students based on No KK.
    
    When a parent account is created:
    1. Get the parent's No KK from their profile
    2. Find all students with matching No KK in the same tenant
    3. Create ParentStudentLink records automatically
    
    This implements the smart linking logic from sakti.md:
    "Logic: Saat akun Wali Murid/Santri dibuat, sistem melakukan cross-check 
     field no_kk pada tabel Siswa/Santri. Jika cocok, relasi dibuat otomatis 
     tanpa intervensi Admin."
    """
    if not created:
        return
    
    # Only process parent accounts
    if instance.role != 'parent':
        return
    
    # Import here to avoid circular imports
    from .models import ParentStudentLink
    
    # Get the parent profile if it exists
    parent_profile = getattr(instance, 'profile', None)
    
    if not parent_profile or not parent_profile.no_kk:
        return
    
    # Get the tenant from the user
    tenant = getattr(instance, 'tenant', None)
    if not tenant:
        return
    
    # Find students with matching No KK in the same tenant
    # We need to query through the academic app's Student model
    try:
        from apps.academic.models import Student
        
        # Get students with matching No KK in the same tenant
        # Note: We need to use tenant schema for this query
        students = Student.objects.filter(
            no_kk=parent_profile.no_kk,
            tenant=tenant,
            user__is_active=True
        )
        
        # Create links for found students
        links_created = 0
        for student in students:
            # Check if link already exists
            if not ParentStudentLink.objects.filter(
                parent=instance,
                student=student.user
            ).exists():
                ParentStudentLink.objects.create(
                    parent=instance,
                    student=student.user,
                    relation_type='father',  # Default, can be changed later
                    is_primary=True,
                    is_verified=True,
                    verified_at=timezone.now()
                )
                links_created += 1
        
        if links_created > 0:
            # You could add logging here if needed
            pass
            
    except ImportError:
        # If academic app is not available, skip
        pass


def create_link_request(parent, student, relation_type='father', notes=''):
    """
    Helper function to create a manual link request.
    
    Used when:
    - Auto-linking fails (No KK doesn't match any student)
    - Parent wants to link additional children
    """
    from .models import LinkRequest
    
    # Check if there's already a pending request
    existing_request = LinkRequest.objects.filter(
        parent=parent,
        student=student,
        status='pending'
    ).exists()
    
    if existing_request:
        return None
    
    return LinkRequest.objects.create(
        parent=parent,
        student=student,
        requested_relation=relation_type,
        notes=notes
    )


def approve_link_request(request_id, approved_by):
    """
    Helper function to approve a link request.
    """
    from .models import LinkRequest, ParentStudentLink
    
    try:
        link_request = LinkRequest.objects.get(id=request_id)
    except LinkRequest.DoesNotExist:
        return None
    
    # Create the actual link
    parent_student_link, created = ParentStudentLink.objects.get_or_create(
        parent=link_request.parent,
        student=link_request.student,
        defaults={
            'relation_type': link_request.requested_relation,
            'is_primary': True,
            'is_verified': True,
            'verified_at': timezone.now()
        }
    )
    
    # Update the request status
    link_request.status = 'approved'
    link_request.approved_by = approved_by
    link_request.approved_at = timezone.now()
    link_request.save()
    
    return parent_student_link


def reject_link_request(request_id, approved_by):
    """
    Helper function to reject a link request.
    """
    from .models import LinkRequest
    
    try:
        link_request = LinkRequest.objects.get(id=request_id)
    except LinkRequest.DoesNotExist:
        return None
    
    link_request.status = 'rejected'
    link_request.approved_by = approved_by
    link_request.approved_at = timezone.now()
    link_request.save()
    
    return link_request