"""
Activities Views.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
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


@extend_schema_view(
    list=extend_schema(
        tags=['Activities'],
        summary='Daftar absensi',
        description='Mengambil daftar semua absensi. Filter berdasarkan tanggal, status, tipe, classroom, atau mata pelajaran.'
    ),
    create=extend_schema(
        tags=['Activities'],
        summary='Buat absensi',
        description='Merekam entri absensi baru.'
    ),
    retrieve=extend_schema(
        tags=['Activities'],
        summary='Detail absensi',
        description='Mengambil informasi detail absensi tertentu.'
    ),
    update=extend_schema(
        tags=['Activities'],
        summary='Perbarui absensi',
        description='Memperbarui informasi absensi.'
    ),
    destroy=extend_schema(
        tags=['Activities'],
        summary='Hapus absensi',
        description='Menghapus catatan absensi.'
    )
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
            # Parents can see their children's attendance via parent_account relationship
            # Get children (students) linked via parent_account
            child_ids = user.children.values_list('id', flat=True)
            queryset = queryset.filter(student_id__in=child_ids)
        
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
    
    @extend_schema(
        tags=['Activities'],
        summary='Buat absensi massal',
        description='Membuat beberapa catatan absensi sekaligus.'
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


@extend_schema_view(
    list=extend_schema(
        tags=['Activities'],
        summary='Daftar nilai',
        description='Mengambil daftar semua nilai. Filter berdasarkan siswa, mata pelajaran, classroom, atau tipe.'
    ),
    create=extend_schema(
        tags=['Activities'],
        summary='Buat nilai',
        description='Merekam entri nilai baru.'
    ),
    retrieve=extend_schema(
        tags=['Activities'],
        summary='Detail nilai',
        description='Mengambil informasi detail nilai tertentu.'
    ),
    update=extend_schema(
        tags=['Activities'],
        summary='Perbarui nilai',
        description='Memperbarui informasi nilai.'
    ),
    destroy=extend_schema(
        tags=['Activities'],
        summary='Hapus nilai',
        description='Menghapus catatan nilai.'
    )
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
            # Parents can see their children's scores via parent_account relationship
            # Get children (students) linked via parent_account
            child_ids = user.children.values_list('id', flat=True)
            queryset = queryset.filter(student_id__in=child_ids)
        
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
    
    @extend_schema(
        tags=['Activities'],
        summary='Riwayat perubahan nilai',
        description='Mengambil riwayat perubahan nilai. Hanya untuk admin.'
    )
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


@extend_schema_view(
    list=extend_schema(
        tags=['Activities'],
        summary='Daftar acara timeline',
        description='Mengambil daftar semua acara timeline. Filter berdasarkan tipe atau tanggal.'
    ),
    create=extend_schema(
        tags=['Activities'],
        summary='Buat acara timeline',
        description='Membuat acara timeline baru.'
    ),
    retrieve=extend_schema(
        tags=['Activities'],
        summary='Detail acara timeline',
        description='Mengambil informasi detail acara timeline tertentu.'
    ),
    update=extend_schema(
        tags=['Activities'],
        summary='Perbarui acara timeline',
        description='Memperbarui informasi acara timeline.'
    ),
    destroy=extend_schema(
        tags=['Activities'],
        summary='Hapus acara timeline',
        description='Menghapus acara timeline.'
    )
)
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


@extend_schema_view(
    list=extend_schema(
        tags=['Activities'],
        summary='Daftar notifikasi timeline',
        description='Mengambil daftar semua notifikasi timeline untuk orang tua saat ini.'
    ),
    retrieve=extend_schema(
        tags=['Activities'],
        summary='Detail notifikasi timeline',
        description='Mengambil informasi detail notifikasi timeline tertentu.'
    )
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
    
    @extend_schema(
        tags=['Activities'],
        summary='Tandai notifikasi sudah dibaca',
        description='Menandai notifikasi tertentu sudah dibaca.'
    )
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
    
    @extend_schema(
        tags=['Activities'],
        summary='Tandai semua notifikasi sudah dibaca',
        description='Menandai semua notifikasi sudah dibaca untuk orang tua saat ini.'
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