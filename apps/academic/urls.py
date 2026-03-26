"""
Academic URL Configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcademicYearViewSet, SubjectViewSet, GradeViewSet,
    ClassroomViewSet, EnrollmentViewSet, TeacherAssignmentViewSet,
    StudentsViewSet, TeachersViewSet
)

router = DefaultRouter()
router.register(r'academic-years', AcademicYearViewSet, basename='academic_year')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'classrooms', ClassroomViewSet, basename='classroom')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'teacher-assignments', TeacherAssignmentViewSet, basename='teacher_assignment')
router.register(r'students', StudentsViewSet, basename='student')
router.register(r'teachers', TeachersViewSet, basename='teacher')

urlpatterns = [
    path('', include(router.urls)),
]