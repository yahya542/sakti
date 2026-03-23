"""
Smart Linking Models - Auto-link parent and student based on No KK.
"""

from django.db import models
from django.conf import settings


class ParentStudentLink(models.Model):
    """
    Model to store the relationship between parent/guardian and student.
    This is created automatically when a parent account is created and matches No KK.
    """
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_links',
        limit_choices_to={'role': 'parent'},
        verbose_name='Wali Murid/Santri'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_links',
        limit_choices_to={'role': 'student'},
        verbose_name='Siswa/Santri'
    )
    relation_type = models.CharField(
        max_length=50,
        choices=[
            ('father', 'Ayah'),
            ('mother', 'Ibu'),
            ('guardian', 'Wali'),
            ('grandparent', 'Kakek/Nenek'),
            ('sibling', 'Kakak/Adik'),
            ('other', 'Lainnya'),
        ],
        default='father',
        verbose_name='Jenis Hubungan'
    )
    is_primary = models.BooleanField(
        default=True,
        verbose_name='Hubungan Utama'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Terverifikasi'
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Tanggal Verifikasi'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'smart_linking_parent_student'
        verbose_name = 'Link Wali Murid'
        verbose_name_plural = 'Link Wali Murid'
        unique_together = [['parent', 'student']]
        indexes = [
            models.Index(fields=['parent']),
            models.Index(fields=['student']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.parent.get_full_name()} -> {self.student.get_full_name()}"


class LinkRequest(models.Model):
    """
    Model to store manual linking requests from parents.
    Used when auto-linking fails or parent wants to link additional children.
    """
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('expired', 'Kedaluwarsa'),
    ]
    
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='link_requests',
        limit_choices_to={'role': 'parent'},
        verbose_name='Wali Murid/Santri'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incoming_link_requests',
        limit_choices_to={'role': 'student'},
        verbose_name='Siswa/Santri'
    )
    RELATION_TYPE_CHOICES = [
        ('father', 'Ayah'),
        ('mother', 'Ibu'),
        ('guardian', 'Wali'),
        ('grandparent', 'Kakek/Nenek'),
        ('sibling', 'Kakak/Adik'),
        ('other', 'Lainnya'),
    ]
    
    requested_relation = models.CharField(
        max_length=50,
        choices=RELATION_TYPE_CHOICES,
        default='father',
        verbose_name='Jenis Hubungan Diminta'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Catatan'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_link_requests',
        verbose_name='Disetujui Oleh'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Tanggal Persetujuan'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        verbose_name='Kedaluwarsa'
    )
    
    class Meta:
        db_table = 'smart_linking_requests'
        verbose_name = 'Permintaan Link'
        verbose_name_plural = 'Permintaan Link'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Request: {self.parent.get_full_name()} -> {self.student.get_full_name()}"
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        
        super().save(*args, **kwargs)