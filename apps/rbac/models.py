"""
RBAC Models - Permissions and Role configurations.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    """Fine-grained permissions for resources."""
    
    name = models.CharField(
        verbose_name=_('Nama'),
        max_length=100
    )
    
    code = models.CharField(
        verbose_name=_('Kode'),
        max_length=50,
        unique=True
    )
    
    RESOURCE_CHOICES = [
        ('tenant', _('Tenant')),
        ('user', _('User')),
        ('academic_year', _('Tahun Ajaran')),
        ('subject', _('Mata Pelajaran')),
        ('grade', _('Tingkat')),
        ('classroom', _('Kelas')),
        ('enrollment', _('Pendaftaran')),
        ('attendance', _('Absensi')),
        ('score', _('Nilai')),
        ('finance', _('Keuangan')),
        ('report', _('Laporan')),
    ]
    
    resource = models.CharField(
        verbose_name=_('Resource'),
        max_length=30,
        choices=RESOURCE_CHOICES
    )
    
    ACTION_CHOICES = [
        ('create', _('Buat')),
        ('read', _('Baca')),
        ('update', _('Ubah')),
        ('delete', _('Hapus')),
        ('approve', _('Approve')),
        ('export', _('Export')),
    ]
    
    action = models.CharField(
        verbose_name=_('Aksi'),
        max_length=20,
        choices=ACTION_CHOICES
    )
    
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')
        unique_together = ['resource', 'action']
    
    def __str__(self):
        return f"{self.resource}:{self.action}"


class RolePermission(models.Model):
    """Role-Permission mapping."""
    
    role = models.CharField(
        verbose_name=_('Peran'),
        max_length=20
    )
    
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    
    is_granted = models.BooleanField(
        verbose_name=_('Diberikan'),
        default=True
    )
    
    class Meta:
        verbose_name = _('Role Permission')
        verbose_name_plural = _('Role Permissions')
        unique_together = ['role', 'permission']
    
    def __str__(self):
        status = '✓' if self.is_granted else '✗'
        return f"{self.role} - {self.permission} {status}"


def get_default_permissions():
    """Get default permissions for each role."""
    return {
        'super_admin': [
            'tenant:create', 'tenant:read', 'tenant:update', 'tenant:delete',
            'user:create', 'user:read', 'user:update', 'user:delete',
            'academic_year:create', 'academic_year:read', 'academic_year:update', 'academic_year:delete',
            'subject:create', 'subject:read', 'subject:update', 'subject:delete',
            'grade:create', 'grade:read', 'grade:update', 'grade:delete',
            'classroom:create', 'classroom:read', 'classroom:update', 'classroom:delete',
            'enrollment:create', 'enrollment:read', 'enrollment:update', 'enrollment:delete',
            'attendance:create', 'attendance:read', 'attendance:update', 'attendance:delete',
            'score:create', 'score:read', 'score:update', 'score:delete',
            'finance:create', 'finance:read', 'finance:update', 'finance:delete',
            'report:create', 'report:read', 'report:export',
        ],
        'admin': [
            'user:create', 'user:read', 'user:update',
            'academic_year:create', 'academic_year:read', 'academic_year:update',
            'subject:create', 'subject:read', 'subject:update', 'subject:delete',
            'grade:create', 'grade:read', 'grade:update', 'grade:delete',
            'classroom:create', 'classroom:read', 'classroom:update', 'classroom:delete',
            'enrollment:create', 'enrollment:read', 'enrollment:update',
            'attendance:create', 'attendance:read', 'attendance:update',
            'score:create', 'score:read', 'score:update',
            'finance:create', 'finance:read', 'finance:update',
            'report:read', 'report:export',
        ],
        'teacher': [
            'academic_year:read',
            'subject:read',
            'grade:read',
            'classroom:read',
            'enrollment:read',
            'attendance:create', 'attendance:read', 'attendance:update',
            'score:create', 'score:read', 'score:update',
            'report:read',
        ],
        'student': [
            'academic_year:read',
            'subject:read',
            'classroom:read',
            'enrollment:read',
            'attendance:read',
            'score:read',
            'report:read',
        ],
        'parent': [
            'academic_year:read',
            'subject:read',
            'classroom:read',
            'enrollment:read',
            'attendance:read',
            'score:read',
            'finance:read',
            'report:read',
        ],
    }