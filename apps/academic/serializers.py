"""
Academic Serializers - DRF Serializers for Academic models.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import (
    AcademicYear, Subject, Grade, Classroom,
    Enrollment, TeacherAssignment
)
from apps.accounts.serializers import UserSerializer


class AcademicYearSerializer(serializers.ModelSerializer):
    """Serializer for AcademicYear."""
    
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_active', 'is_current']
        read_only_fields = ['id']


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject."""
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'subject_type', 'is_active']
        read_only_fields = ['id']


class GradeSerializer(serializers.ModelSerializer):
    """Serializer for Grade."""
    
    class Meta:
        model = Grade
        fields = ['id', 'name', 'level', 'grade_type', 'description']
        read_only_fields = ['id']


class ClassroomSerializer(serializers.ModelSerializer):
    """Serializer for Classroom."""
    
    student_count = serializers.IntegerField(read_only=True)
    homeroom_teacher_detail = UserSerializer(source='homeroom_teacher', read_only=True)
    
    class Meta:
        model = Classroom
        fields = [
            'id', 'name', 'academic_year', 'grade', 'homeroom_teacher',
            'homeroom_teacher_detail', 'capacity', 'room_number',
            'is_active', 'student_count'
        ]
        read_only_fields = ['id', 'student_count']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment."""
    
    student_detail = UserSerializer(source='student', read_only=True)
    classroom_detail = ClassroomSerializer(source='classroom', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_detail', 'classroom', 'classroom_detail',
            'status', 'enrolled_at', 'is_active'
        ]
        read_only_fields = ['id', 'enrolled_at']


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for TeacherAssignment."""
    
    teacher_detail = UserSerializer(source='teacher', read_only=True)
    subject_detail = SubjectSerializer(source='subject', read_only=True)
    classroom_detail = ClassroomSerializer(source='classroom', read_only=True)
    academic_year_detail = AcademicYearSerializer(source='academic_year', read_only=True)
    
    class Meta:
        model = TeacherAssignment
        fields = [
            'id', 'teacher', 'teacher_detail', 'subject', 'subject_detail',
            'classroom', 'classroom_detail', 'is_homeroom', 'is_active',
            'academic_year', 'academic_year_detail'
        ]
        read_only_fields = ['id']


class ClassroomListSerializer(serializers.ModelSerializer):
    """Extended classroom serializer with student list."""
    
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    homeroom_teacher_name = serializers.CharField(
        source='homeroom_teacher.full_name',
        read_only=True
    )
    students = serializers.SerializerMethodField()
    
    class Meta:
        model = Classroom
        fields = [
            'id', 'name', 'grade', 'grade_name', 'academic_year', 'academic_year_name',
            'homeroom_teacher', 'homeroom_teacher_name', 'capacity', 'room_number',
            'is_active', 'student_count', 'students'
        ]
    
    def get_students(self, obj):
        enrollments = obj.enrollments.filter(is_active=True, status='active')
        return UserSerializer(enrollments.values_list('student', flat=True), many=True).data


class StudentEnrollmentSerializer(serializers.Serializer):
    """Serializer for bulk student enrollment."""
    
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    classroom_id = serializers.IntegerField()
    
    def validate_classroom_id(self, value):
        try:
            classroom = Classroom.objects.get(id=value)
        except Classroom.DoesNotExist:
            raise serializers.ValidationError('Kelas tidak ditemukan.')
        return value