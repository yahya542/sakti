"""
Activities Models - Attendance, Scores, Timeline.
"""

from django.db import models
from django.conf import settings
import uuid


class Attendance(models.Model):
    """
    Model for student attendance tracking.
    Supports daily, per-session, and activity-based attendance.
    """
    ATTENDANCE_TYPES = [
        ('daily', 'Harian'),
        ('session', 'Per Jam Pelajaran'),
        ('activity', 'Ekstrakurikuler/Diniyah'),
    ]
    
    STATUS_CHOICES = [
        ('present', 'Hadir'),
        ('absent', 'Tidak Hadir'),
        ('late', 'Terlambat'),
        ('excused', 'Izin'),
        ('sick', 'Sakit'),
    ]
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances',
        limit_choices_to={'role': 'student'}
    )
    classroom = models.ForeignKey(
        'academic.Classroom',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances'
    )
    subject = models.ForeignKey(
        'academic.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances'
    )
    
    attendance_type = models.CharField(
        max_length=20,
        choices=ATTENDANCE_TYPES,
        default='daily'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present'
    )
    date = models.DateField()
    session = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Nomor sesi untuk attendance_type=session'
    )
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_attendances'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activities_attendance'
        verbose_name = 'Absensi'
        verbose_name_plural = 'Absensi'
        unique_together = [['student', 'date', 'attendance_type', 'session', 'subject']]
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['student', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['recorded_by']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.status}"


class Score(models.Model):
    """
    Model for student scores/grades.
    Supports daily assignments, mid-term (UTS), final exams (UAS), and tasks.
    """
    SCORE_TYPES = [
        ('daily', 'Tugas Harian'),
        ('midterm', 'UTS'),
        ('final', 'UAS'),
        ('task', 'Tugas'),
        ('project', 'Proyek'),
        ('practice', 'Praktik'),
    ]
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='scores'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scores',
        limit_choices_to={'role': 'student'}
    )
    subject = models.ForeignKey(
        'academic.Subject',
        on_delete=models.CASCADE,
        related_name='scores'
    )
    classroom = models.ForeignKey(
        'academic.Classroom',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scores'
    )
    academic_year = models.ForeignKey(
        'academic.AcademicYear',
        on_delete=models.CASCADE,
        related_name='scores'
    )
    
    score_type = models.CharField(
        max_length=20,
        choices=SCORE_TYPES
    )
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100
    )
    title = models.CharField(
        max_length=255,
        help_text='Judul tugas/ujian'
    )
    description = models.TextField(blank=True)
    semester = models.PositiveSmallIntegerField(
        help_text='Semester (1 atau 2)'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_scores'
    )
    
    # Audit fields for change tracking
    previous_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    changed_at = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='score_changes'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activities_scores'
        verbose_name = 'Nilai'
        verbose_name_plural = 'Nilai'
        ordering = [ '-created_at']
        indexes = [
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['score_type']),
            models.Index(fields=['semester']),
            models.Index(fields=['recorded_by']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.name} - {self.score}"


class TimelineEvent(models.Model):
    """
    Model for timeline events that appear in parent/guardian feed.
    Events are created when:
    - New attendance is recorded
    - New score is entered
    - Activity photo is uploaded
    - Announcement is made
    """
    EVENT_TYPES = [
        ('attendance', 'Absensi'),
        ('score', 'Nilai Baru'),
        ('activity', 'Foto Kegiatan'),
        ('announcement', 'Pengumuman'),
        ('assignment', 'Tugas Baru'),
    ]
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='timeline_events'
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='timeline/',
        null=True,
        blank=True
    )
    
    # Reference to related objects
    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='timeline_events'
    )
    score = models.ForeignKey(
        Score,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='timeline_events'
    )
    
    # For activity type events
    activity_date = models.DateTimeField(null=True, blank=True)
    classroom = models.ForeignKey(
        'academic.Classroom',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timeline_events'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_timeline_events'
    )
    published = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activities_timeline'
        verbose_name = 'Timeline'
        verbose_name_plural = 'Timeline'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['published']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.title}"


class TimelineNotification(models.Model):
    """
    Model to track which parents have seen which timeline events.
    """
    timeline_event = models.ForeignKey(
        TimelineEvent,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'parent'},
        related_name='timeline_notifications'
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activities_timeline_notifications'
        verbose_name = 'Notifikasi Timeline'
        verbose_name_plural = 'Notifikasi Timeline'
        unique_together = [['timeline_event', 'parent']]
        indexes = [
            models.Index(fields=['parent', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.parent.get_full_name()} - {self.timeline_event.title}"