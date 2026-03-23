"""
Activities Views.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from .models import Attendance, Score, TimelineEvent, TimelineNotification
from .serializers import (
    AttendanceSerializer,
    AttendanceBulkCreateSerializer,
    ScoreSerializer,
    ScoreAuditSerializer,
    TimelineEventSerializer,
    TimelineEventCreateSerializer,
    TimelineNotificationSerializer,
)


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student attendance.
    
    Teachers can record and view attendance.
    Parents can view their children's attendance.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['date', 'status', 'attendance_type', 'classroom', 'subject']
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['date', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        # Get tenant
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return Attendance.objects.none()
        
        queryset = Attendance.objects.filter(tenant=tenant)
        
        # Filter based on role
        if user.role == 'teacher':
            # Teachers can see attendance for their classes
            from apps.academic.models import TeacherAssignment
            teacher_assignments = TeacherAssignment.objects.filter(
                teacher=user
            ).values_list('classroom_id', flat=True)
            queryset = queryset.filter(classroom_id__in=teacher_assignments)
        
        elif user.role == 'parent':
            # Parents can see their children's attendance
            from apps.smart_linking.models import ParentStudentLink
            student_ids = ParentStudentLink.objects.filter(
                parent=user
            ).values_list('student_id', flat=True)
            queryset = queryset.filter(student_id__in=student_ids)
        
        elif user.role == 'student':
            # Students can only see their own attendance
            queryset = queryset.filter(student=user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the tenant and recorded_by."""
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(
            tenant=tenant,
            recorded_by=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create attendance records.
        """
        serializer = AttendanceBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response(
                {'error': 'Tenant not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        validated_data['tenant'] = tenant
        validated_data['recorded_by'] = request.user
        
        records = serializer.create(validated_data)
        
        return Response(
            {'message': f'{len(records)} attendance records created'},
            status=status.HTTP_201_CREATED
        )


class ScoreViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student scores.
    
    Teachers can input and view scores.
    Parents can view their children's scores.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ScoreSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['score_type', 'subject', 'classroom', 'semester', 'academic_year']
    search_fields = ['student__first_name', 'student__last_name', 'title']
    ordering_fields = ['created_at', 'date']
    
    def get_queryset(self):
        user = self.request.user
        
        # Get tenant
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return Score.objects.none()
        
        queryset = Score.objects.filter(tenant=tenant)
        
        # Filter based on role
        if user.role == 'teacher':
            # Teachers can see scores for their subjects
            from apps.academic.models import TeacherAssignment
            teacher_assignments = TeacherAssignment.objects.filter(
                teacher=user
            ).values_list('subject_id', flat=True)
            queryset = queryset.filter(subject_id__in=teacher_assignments)
        
        elif user.role == 'parent':
            # Parents can see their children's scores
            from apps.smart_linking.models import ParentStudentLink
            student_ids = ParentStudentLink.objects.filter(
                parent=user
            ).values_list('student_id', flat=True)
            queryset = queryset.filter(student_id__in=student_ids)
        
        elif user.role == 'student':
            # Students can only see their own scores
            queryset = queryset.filter(student=user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the tenant and recorded_by."""
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(
            tenant=tenant,
            recorded_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Track score changes for audit."""
        instance = serializer.save()
        
        # Update audit fields if score changed
        if instance.previous_score and instance.previous_score != instance.score:
            instance.changed_at = timezone.now()
            instance.changed_by = self.request.user
            instance.save(update_fields=['changed_at', 'changed_by'])
    
    @action(detail=False, methods=['get'])
    def audit_trail(self, request):
        """
        Get audit trail for score changes.
        Only accessible by admins.
        """
        if request.user.role not in ['admin', 'super_admin']:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().exclude(changed_at__isnull=True)
        queryset = queryset.order_by('-changed_at')[:100]
        
        serializer = ScoreAuditSerializer(queryset, many=True)
        return Response(serializer.data)


class TimelineEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing timeline events.
    
    Parents view their feed here.
    Teachers and admins create events.
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TimelineEventCreateSerializer
        return TimelineEventSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Get tenant
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return TimelineEvent.objects.none()
        
        queryset = TimelineEvent.objects.filter(
            tenant=tenant,
            published=True
        )
        
        # Filter based on role
        if user.role == 'parent':
            # Get linked students
            from apps.smart_linking.models import ParentStudentLink
            student_ids = ParentStudentLink.objects.filter(
                parent=user
            ).values_list('student_id', flat=True)
            
            # Show events related to their children
            # Filter by classrooms of linked students
            from apps.academic.models import Enrollment
            classroom_ids = Enrollment.objects.filter(
                student_id__in=student_ids
            ).values_list('classroom_id', flat=True)
            
            queryset = queryset.filter(
                Q(classroom_id__in=classroom_ids) | Q(classroom__isnull=True)
            )
        
        elif user.role == 'student':
            # Students see their own timeline
            from apps.academic.models import Enrollment
            enrollment = Enrollment.objects.filter(student=user).first()
            if enrollment:
                queryset = queryset.filter(
                    Q(classroom=enrollment.classroom) | Q(classroom__isnull=True)
                )
            else:
                queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the tenant and created_by."""
        tenant = getattr(self.request.user, 'tenant', None)
        serializer.save(
            tenant=tenant,
            created_by=self.request.user,
            published_at=timezone.now()
        )


class TimelineNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing timeline notifications.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TimelineNotificationSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role != 'parent':
            return TimelineNotification.objects.none()
        
        return TimelineNotification.objects.filter(
            parent=user
        ).select_related('timeline_event')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark notification as read.
        """
        try:
            notification = self.get_queryset().get(pk=pk)
        except TimelineNotification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at'])
        
        return Response(
            TimelineNotificationSerializer(notification).data
        )
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications as read.
        """
        notifications = self.get_queryset().filter(is_read=False)
        notifications.update(is_read=True, read_at=timezone.now())
        
        return Response(
            {'message': f'{notifications.count()} notifications marked as read'}
        )