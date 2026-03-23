"""
Account Models - User and Profile management.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for SAKTI."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ROLE_SUPER_ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for SAKTI.
    Extends Django's AbstractUser with additional fields.
    """
    
    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN := 'super_admin', _('Super Admin')),
        (ROLE_ADMIN := 'admin', _('Admin Sekolah')),
        (ROLE_TEACHER := 'teacher', _('Guru/Ustadz')),
        (ROLE_STUDENT := 'student', _('Siswa/Santri')),
        (ROLE_PARENT := 'parent', _('Wali Murid/Santri')),
    ]
    
    # Replace username with email as primary identifier
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Role-based access
    role = models.CharField(
        verbose_name=_('Peran'),
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT
    )
    
    # Profile photo
    photo = models.ImageField(
        verbose_name=_('Foto'),
        upload_to='accounts/photos/',
        blank=True,
        null=True
    )
    
    # Phone number
    phone = models.CharField(
        verbose_name=_('Telepon'),
        max_length=20,
        blank=True
    )
    
    # Additional info
    is_active = models.BooleanField(
        verbose_name=_('Aktif'),
        default=True,
        help_text=_('Non-aktifkan untuk menonaktifkan akses user')
    )
    
    email_verified = models.BooleanField(
        verbose_name=_('Email Terverifikasi'),
        default=False
    )
    
    last_login_ip = models.GenericIPAddressField(
        verbose_name=_('IP Login Terakhir'),
        null=True,
        blank=True
    )
    
    last_login_at = models.DateTimeField(
        verbose_name=_('Login Terakhir'),
        null=True,
        blank=True
    )
    
    # Parent relationship (for students/parents)
    parent_account = models.ForeignKey(
        'self',
        verbose_name=_('Akun Orang Tua'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def role_display(self):
        """Return human-readable role name."""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
    
    def is_teacher(self):
        return self.role == self.ROLE_TEACHER
    
    def is_student(self):
        return self.role == self.ROLE_STUDENT
    
    def is_parent(self):
        return self.role == self.ROLE_PARENT
    
    def is_admin(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPER_ADMIN]


class UserProfile(models.Model):
    """
    Extended profile information for users.
    Additional fields that vary by role.
    """
    
    user = models.OneToOneField(
        User,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # For teachers
    employee_id = models.CharField(
        verbose_name=_('NIP'),
        max_length=50,
        blank=True
    )
    
    # For students
    student_id = models.CharField(
        verbose_name=_('NIS/NISN'),
        max_length=50,
        blank=True
    )
    
    # Address
    address = models.TextField(
        verbose_name=_('Alamat'),
        blank=True
    )
    
    # Place of birth
    place_of_birth = models.CharField(
        verbose_name=_('Tempat Lahir'),
        max_length=100,
        blank=True
    )
    
    # Date of birth
    date_of_birth = models.DateField(
        verbose_name=_('Tanggal Lahir'),
        null=True,
        blank=True
    )
    
    # Gender
    GENDER_CHOICES = [
        ('male', _('Laki-laki')),
        ('female', _('Perempuan')),
    ]
    gender = models.CharField(
        verbose_name=_('Jenis Kelamin'),
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    # Additional metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"Profile: {self.user.email}"