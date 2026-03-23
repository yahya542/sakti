"""
Academic Models - Students, Teachers, Subjects, Classes.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AcademicYear(models.Model):
    """Academic year / school year."""
    
    name = models.CharField(
        verbose_name=_('Nama Tahun Ajaran'),
        max_length=50,
        help_text=_('Contoh: 2025/2026')
    )
    
    start_date = models.DateField(
        verbose_name=_('Tanggal Mulai')
    )
    
    end_date = models.DateField(
        verbose_name=_('Tanggal Selesai')
    )
    
    is_active = models.BooleanField(
        verbose_name=_('Aktif'),
        default=False
    )
    
    is_current = models.BooleanField(
        verbose_name=_('Tahun Ajaran Sekarang'),
        default=False
    )
    
    class Meta:
        verbose_name = _('Academic Year')
        verbose_name_plural = _('Academic Years')
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name


class Subject(models.Model):
    """
    Subject / Subject matter.
    For schools: Mapel (Matematika, Bahasa Indonesia, etc.)
    Forpesantrens: Kitab (Al-Quran, Hadits, Fiqih, etc.)
    """
    
    name = models.CharField(
        verbose_name=_('Nama Mapel/Kitab'),
        max_length=100
    )
    
    code = models.CharField(
        verbose_name=_('Kode'),
        max_length=20,
        unique=True
    )
    
    TYPE_CHOICES = [
        ('general', _(' Umum')),
        ('religious', _('Agama')),
        ('language', _('Bahasa')),
        ('science', _('Sains')),
        ('arts', _('Seni')),
        ('sports', _('Olahraga')),
    ]
    
    subject_type = models.CharField(
        verbose_name=_('Tipe'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='general'
    )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        ordering = ['subject_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Grade(models.Model):
    """
    Grade / Class level.
    For schools: Kelas 1, Kelas 2, etc.
    Forpesantrens: Kelas 1, 2, 3 (Kitab), etc.
    """
    
    name = models.CharField(
        verbose_name=_('Nama Tingkat/Kelas'),
        max_length=50,
        help_text=_('Contoh: Kelas 1, Kelas 2 SMA')
    )
    
    level = models.PositiveIntegerField(
        verbose_name=_('Tingkat'),
        unique=True
    )
    
    TYPE_CHOICES = [
        ('sd', _('SD')),
        ('smp', _('SMP')),
        ('sma', _('SMA')),
        ('smk', _('SMK')),
        ('pesantren', _('Pesantren')),
    ]
    
    grade_type = models.CharField(
        verbose_name=_('Tipe'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='sd'
    )
    
    description = models.TextField(
        verbose_name=_('Deskripsi'),
        blank=True
    )
    
    class Meta:
        verbose_name = _('Grade')
        verbose_name_plural = _('Grades')
        ordering = ['level']
    
    def __str__(self):
        return self.name


class Classroom(models.Model):
    """
    Classroom / Class group.
    Links students with a homeroom teacher.
    """
    
    name = models.CharField(
        verbose_name=_('Nama Kelas'),
        max_length=50,
        help_text=_('Contoh: Kelas 1-A')
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_('Tahun Ajaran'),
        on_delete=models.CASCADE,
        related_name='classrooms'
    )
    
    grade = models.ForeignKey(
        Grade,
        verbose_name=_('Tingkat'),
        on_delete=models.CASCADE,
        related_name='classrooms'
    )
    
    # Homeroom teacher / Walikelas / Ustadz Pendamping
    homeroom_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Wali Kelas/Ustadz'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='homeroom_classrooms'
    )
    
    capacity = models.PositiveIntegerField(
        verbose_name=_('Kapasitas'),
        default=30
    )
    
    room_number = models.CharField(
        verbose_name=_('Nomor Ruang'),
        max_length=20,
        blank=True
    )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('Classroom')
        verbose_name_plural = _('Classrooms')
        unique_together = ['name', 'academic_year']
        ordering = ['grade__level', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"
    
    @property
    def student_count(self):
        return self.enrollments.filter(is_active=True).count()


class Enrollment(models.Model):
    """Student enrollment in a classroom."""
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Siswa/Santri'),
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    classroom = models.ForeignKey(
        Classroom,
        verbose_name=_('Kelas'),
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    STATUS_CHOICES = [
        ('active', _('Aktif')),
        ('graduated', _('Lulus')),
        ('transferred', _('Pindah')),
        ('suspended', _('Skorsing')),
        ('dropout', _('Dropout')),
    ]
    
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    enrolled_at = models.DateTimeField(
        verbose_name=_('Tanggal Daftar'),
        auto_now_add=True
    )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = ['student', 'classroom']
    
    def __str__(self):
        return f"{self.student} - {self.classroom}"


class TeacherAssignment(models.Model):
    """Teacher assignment to subjects and grades."""
    
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Guru/Ustadz'),
        on_delete=models.CASCADE,
        related_name='subject_assignments'
    )
    
    subject = models.ForeignKey(
        Subject,
        verbose_name=_('Mapel/Kitab'),
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    
    classroom = models.ForeignKey(
        Classroom,
        verbose_name=_('Kelas'),
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    
    is_homeroom = models.BooleanField(
        verbose_name=_('Wali Kelas'),
        default=False
    )
    
    is_active = models.BooleanField(default=True)
    
    academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name=_('Tahun Ajaran'),
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    
    class Meta:
        verbose_name = _('Teacher Assignment')
        verbose_name_plural = _('Teacher Assignments')
        unique_together = ['teacher', 'subject', 'classroom', 'academic_year']
    
    def __str__(self):
        return f"{self.teacher} - {self.subject} ({self.classroom})"