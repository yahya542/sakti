"""
Academic Admin Configuration.
"""

from django.contrib import admin
from .models import (
    AcademicYear, Subject, Grade, Classroom,
    Enrollment, TeacherAssignment
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active', 'is_current']
    list_filter = ['is_active', 'is_current']
    search_fields = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'subject_type', 'is_active']
    list_filter = ['subject_type', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'grade_type']
    list_filter = ['grade_type']
    ordering = ['level']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'academic_year', 'homeroom_teacher', 'room_number']
    list_filter = ['academic_year', 'grade']
    search_fields = ['name', 'room_number']
    raw_id_fields = ['homeroom_teacher']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'classroom', 'status', 'enrolled_at', 'is_active']
    list_filter = ['status', 'is_active', 'classroom']
    raw_id_fields = ['student', 'classroom']
    search_fields = ['student__email', 'classroom__name']


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'classroom', 'is_homeroom', 'academic_year', 'is_active']
    list_filter = ['academic_year', 'is_homeroom', 'is_active']
    raw_id_fields = ['teacher', 'subject', 'classroom']
    search_fields = ['teacher__email', 'subject__name']