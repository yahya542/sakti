"""
Academic Views - API endpoints for Academic models.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

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
    """ViewSet for TeacherAssignment CRUD operations."""
    
    queryset = TeacherAssignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TeacherAssignment.objects.all()
        
        # Filter by teacher
        teacher = self.request.query_params.get('teacher')
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)
        
        # Filter by classroom
        classroom = self.request.query_params.get('classroom')
        if classroom:
            queryset = queryset.filter(classroom_id=classroom)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """Get assignments for the logged-in teacher."""
        user = request.user
        assignments = TeacherAssignment.objects.filter(
            teacher=user,
            is_active=True
        ).select_related('subject', 'classroom', 'academic_year')
        
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)