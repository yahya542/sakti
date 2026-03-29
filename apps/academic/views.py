"""
academic Views - API endpoints for academic models.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import (
    AcademicYear, Subject, Grade, Classroom,
    Enrollment, TeacherAssignment
)
from .serializers import (
    AcademicYearSerializer, SubjectSerializer, GradeSerializer,
    ClassroomSerializer, EnrollmentSerializer, TeacherAssignmentSerializer,
    ClassroomListSerializer, StudentEnrollmentSerializer
)
from apps.accounts.permissions import IsAdmin, IsTeacherOrAdmin
from apps.accounts.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        tags=['Academic'],
        summary='Daftar tahun ajaran',
        description='Mengambil daftar semua tahun ajaran. Filter berdasarkan tenant untuk pengguna non-super-admin.'
    ),
    create=extend_schema(
        tags=['Academic'],
        summary='Buat tahun ajaran',
        description='Membuat tahun ajaran baru. Memerlukan hak istimewa admin.'
    ),
    retrieve=extend_schema(
        tags=['Academic'],
        summary='Detail tahun ajaran',
        description='Mengambil informasi detail tentang tahun ajaran tertentu.'
    ),
    update=extend_schema(
        tags=['Academic'],
        summary='Perbarui tahun ajaran',
        description='Memperbarui informasi tahun ajaran. Memerlukan hak istimewa admin.'
    ),
    destroy=extend_schema(
        tags=['Academic'],
        summary='Hapus tahun ajaran',
        description='Menghapus tahun ajaran. Memerlukan hak istimewa admin.'
    )
)
class AcademicYearViewSet(viewsets.ModelViewSet):
    """ViewSet for AcademicYear CRUD operations."""
    
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return AcademicYear.objects.all()
        return AcademicYear.objects.filter(tenant=user.tenant)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active academic year."""
        try:
            academic_year = AcademicYear.objects.get(is_current=True)
            serializer = self.get_serializer(academic_year)
            return Response(serializer.data)
        except AcademicYear.DoesNotExist:
            return Response(
                {'error': 'Tidak ada tahun ajaran yang aktif.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """Set this academic year as current."""
        academic_year = self.get_object()
        AcademicYear.objects.filter(is_current=True).update(is_current=False)
        academic_year.is_current = True
        academic_year.save()
        return Response({'message': 'Tahun ajaran sekarang berhasil diubah.'})


class SubjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Subject CRUD operations."""
    
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Academic'],
        summary='Daftar mata pelajaran',
        description='Mengambil daftar semua mata pelajaran. Mendukung filter berdasarkan jenis dan pencarian berdasarkan nama/kode.'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Subject.objects.all()
        
        # Filter by subject type
        subject_type = self.request.query_params.get('type')
        if subject_type:
            queryset = queryset.filter(subject_type=subject_type)
        
        # Search by name or code
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        
        return queryset


@extend_schema_view(
    list=extend_schema(tags=['Academic'], summary='Daftar tingkat kelas', description='Mengambil daftar semua tingkat kelas.'),
    create=extend_schema(tags=['Academic'], summary='Buat tingkat kelas', description='Membuat tingkat kelas baru.'),
    retrieve=extend_schema(tags=['Academic'], summary='Detail tingkat kelas', description='Mengambil detail informasi tingkat kelas tertentu.'),
    update=extend_schema(tags=['Academic'], summary='Perbarui tingkat kelas', description='Memperbarui informasi tingkat kelas.'),
    destroy=extend_schema(tags=['Academic'], summary='Hapus tingkat kelas', description='Menghapus tingkat kelas.')
)
class GradeViewSet(viewsets.ModelViewSet):
    """ViewSet for Grade CRUD operations."""
    
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Grade.objects.all()
        
        # Filter by grade type
        grade_type = self.request.query_params.get('grade_type')
        if grade_type:
            queryset = queryset.filter(grade_type=grade_type)
        
        return queryset


class ClassroomViewSet(viewsets.ModelViewSet):
    """ViewSet for Classroom CRUD operations."""
    
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Academic'],
        summary='Daftar ruangan kelas',
        description='Mengambil daftar semua ruangan kelas. Filter berdasarkan tahun ajaran, tingkat, atau guru.'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClassroomListSerializer
        return ClassroomSerializer
    
    def get_queryset(self):
        queryset = Classroom.objects.all()
        
        # Filter by academic year
        academic_year = self.request.query_params.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        
        # Filter by grade
        grade = self.request.query_params.get('grade')
        if grade:
            queryset = queryset.filter(grade_id=grade)
        
        # Filter by homeroom teacher
        teacher = self.request.query_params.get('teacher')
        if teacher:
            queryset = queryset.filter(homeroom_teacher_id=teacher)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get students in a classroom."""
        classroom = self.get_object()
        enrollments = classroom.enrollments.filter(
            is_active=True,
            status='active'
        ).select_related('student')
        
        from apps.accounts.serializers import UserSerializer
        students = [e.student for e in enrollments]
        serializer = UserSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def enroll_bulk(self, request):
        """Bulk enroll students to a classroom."""
        serializer = StudentEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        classroom = Classroom.objects.get(id=serializer.validated_data['classroom_id'])
        student_ids = serializer.validated_data['student_ids']
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        students = User.objects.filter(id__in=student_ids, role='student')
        
        enrollments_created = 0
        for student in students:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                classroom=classroom,
                defaults={'status': 'active', 'is_active': True}
            )
            if created:
                enrollments_created += 1
        
        return Response({
            'message': f'{enrollments_created} siswa/santri berhasil didaftarkan.'
        })


class EnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Enrollment CRUD operations."""
    
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Academic'],
        summary='Daftar enrollment',
        description='Mengambil daftar semua enrollment. Filter berdasarkan classroom atau status.'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Enrollment.objects.all()
        
        # Filter by classroom
        classroom = self.request.query_params.get('classroom')
        if classroom:
            queryset = queryset.filter(classroom_id=classroom)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @extend_schema(
        tags=['Academic'],
        summary='Daftar siswa saya',
        description='Mengambil daftar siswa untuk guru yang sedang login (wali kelas).'
    )
    @action(detail=False, methods=['get'])
    def my_students(self, request):
        """Get students for the logged-in teacher."""
        user = request.user
        if user.role != 'teacher':
            return Response(
                {'error': 'Hanya guru yang dapat mengakses endpoint ini.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        enrollments = Enrollment.objects.filter(
            classroom__homeroom_teacher=user,
            is_active=True,
            status='active'
        ).select_related('student', 'classroom')
        
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)


class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet untuk operasi CRUD penugasan guru."""
    
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Academic'],
        summary='Daftar penugasan guru',
        description='Mengambil daftar penugasan guru berdasarkan filter.'
    )
    def get_queryset(self):
        # 1. Mulai dengan queryset dasar
        queryset = TeacherAssignment.objects.all()
        
        # 2. Ambil parameter dari URL (self.request hanya bisa diakses di dalam method)
        teacher = self.request.query_params.get('teacher')
        classroom = self.request.query_params.get('classroom')

        # 3. Logika Filter
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)
        
        if classroom:
            queryset = queryset.filter(classroom_id=classroom)
            
        # 4. Kembalikan hasilnya
        return queryset
        
    @extend_schema(
        tags=['Academic'],
        summary='Penugasan saya',
        description='Mengambil daftar penugasan guru untuk guru yang sedang login.'
    )
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """Mengambil penugasan untuk guru yang sedang login."""
        user = request.user
        assignments = TeacherAssignment.objects.filter(
            teacher=user,
            is_active=True
        ).select_related('subject', 'classroom', 'academic_year')
        
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)


class StudentListSerializer(serializers.Serializer):
    """Serializer for student list in frontend."""
    id = serializers.IntegerField()
    nis = serializers.CharField(source='profile.student_id', read_only=True)
    nisn = serializers.CharField(source='profile.student_id', read_only=True)
    name = serializers.CharField(source='full_name', read_only=True)
    email = serializers.EmailField()
    class_name = serializers.SerializerMethodField()
    no_kk = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    
    def get_class_name(self, obj):
        """Get active classroom name."""
        enrollment = Enrollment.objects.filter(
            student=obj, 
            is_active=True, 
            status='active'
        ).select_related('classroom').first()
        return enrollment.classroom.name if enrollment else None
    
    def get_no_kk(self, obj):
        """Get parent account phone for Smart Linking."""
        if obj.parent_account:
            return obj.parent_account.phone
        return None


@extend_schema_view(
    list=extend_schema(tags=['Academic'], summary='Daftar siswa', description='Mengambil daftar semua siswa. Filter berdasarkan classroom atau cari berdasarkan nama/email.'),
    create=extend_schema(tags=['Academic'], summary='Buat siswa', description='Membuat siswa baru dengan enrollment opsional.'),
    retrieve=extend_schema(tags=['Academic'], summary='Detail siswa', description='Mengambil detail informasi siswa tertentu.'),
    update=extend_schema(tags=['Academic'], summary='Perbarui siswa', description='Memperbarui data siswa dan enrollment opsional.'),
    partial_update=extend_schema(tags=['Academic'], summary='Perbarui sebagian siswa', description='Memperbarui sebagian data siswa.'),
    destroy=extend_schema(tags=['Academic'], summary='Hapus siswa', description='Menghapus siswa dari sistem.')
)
class StudentsViewSet(viewsets.ModelViewSet):
    """ViewSet untuk operasi siswa."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.filter(role='student')
        
        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Filter by classroom
        class_id = self.request.query_params.get('class_id')
        if class_id:
            student_ids = Enrollment.objects.filter(
                classroom_id=class_id,
                is_active=True,
                status='active'
            ).values_list('student_id', flat=True)
            queryset = queryset.filter(id__in=student_ids)
        
        return queryset.select_related('profile', 'parent_account').prefetch_related(
            'enrollments__classroom'
        )
    
    def create(self, request, *args, **kwargs):
        """Create new student with enrollment."""
        data = request.data.copy()
        
        # Extract enrollment data
        class_id = data.pop('class_id', None)
        
        # Create user
        serializer = UserCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        
        # Enroll in classroom if provided
        if class_id:
            try:
                classroom = Classroom.objects.get(id=class_id)
                Enrollment.objects.create(
                    student=student,
                    classroom=classroom,
                    status='active',
                    is_active=True
                )
            except Classroom.DoesNotExist:
                pass
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update student and optionally change enrollment."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        
        # Extract enrollment data
        class_id = data.pop('class_id', None)
        
        serializer = UserUpdateSerializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Update enrollment if provided
        if class_id:
            # Deactivate old enrollments
            Enrollment.objects.filter(
                student=instance,
                is_active=True
            ).update(is_active=False)
            
            # Create new enrollment
            try:
                classroom = Classroom.objects.get(id=class_id)
                Enrollment.objects.create(
                    student=instance,
                    classroom=classroom,
                    status='active',
                    is_active=True
                )
            except Classroom.DoesNotExist:
                pass
        
        return Response(serializer.data)


class TeacherListSerializer(serializers.Serializer):
    """Serializer for teacher list in frontend."""
    id = serializers.IntegerField()
    nip = serializers.CharField(source='profile.employee_id', read_only=True)
    name = serializers.CharField(source='full_name', read_only=True)
    email = serializers.EmailField()
    phone = serializers.CharField()
    subjects = serializers.SerializerMethodField()
    class_as_wali = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    
    def get_subjects(self, obj):
        """Get subjects taught by this teacher."""
        from .serializers import SubjectSerializer
        assignments = TeacherAssignment.objects.filter(
            teacher=obj, 
            is_active=True
        ).select_related('subject')
        return SubjectSerializer([a.subject for a in assignments], many=True).data
    
    def get_class_as_wali(self, obj):
        """Get classroom where teacher is homeroom teacher."""
        classroom = Classroom.objects.filter(
            homeroom_teacher=obj,
            is_active=True
        ).first()
        return classroom.name if classroom else None


@extend_schema_view(
    list=extend_schema(tags=['Academic'], summary='Daftar guru', description='Mengambil daftar semua guru. Cari berdasarkan nama/email.'),
    create=extend_schema(tags=['Academic'], summary='Buat guru', description='Membuat guru baru.'),
    retrieve=extend_schema(tags=['Academic'], summary='Detail guru', description='Mengambil detail informasi guru tertentu.'),
    update=extend_schema(tags=['Academic'], summary='Perbarui guru', description='Memperbarui data guru.'),
    partial_update=extend_schema(tags=['Academic'], summary='Perbarui sebagian guru', description='Memperbarui sebagian data guru.'),
    destroy=extend_schema(tags=['Academic'], summary='Hapus guru', description='Menghapus guru dari sistem.')
)
class TeachersViewSet(viewsets.ModelViewSet):
    """ViewSet untuk operasi guru."""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TeacherListSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.filter(role='teacher')
        
        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.select_related('profile').prefetch_related(
            'subject_assignments__subject',
            'homeroom_classrooms'
        )
    
    def create(self, request, *args, **kwargs):
        """Create new teacher."""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update teacher."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)