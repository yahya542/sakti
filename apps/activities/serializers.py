"""
Activities Serializers.
"""

from rest_framework import serializers
from .models import Attendance, Score, TimelineEvent, TimelineNotification


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id',
            'tenant',
            'student',
            'student_name',
            'classroom',
            'classroom_name',
            'subject',
            'subject_name',
            'attendance_type',
            'status',
            'date',
            'session',
            'notes',
            'recorded_by',
            'recorded_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceBulkCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for bulk creating attendance records.
    """
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    
    class Meta:
        model = Attendance
        fields = [
            'student_ids',
            'classroom',
            'subject',
            'attendance_type',
            'status',
            'date',
            'session',
            'notes',
        ]
    
    def create(self, validated_data):
        student_ids = validated_data.pop('student_ids')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        students = User.objects.filter(id__in=student_ids)
        attendance_records = []
        
        for student in students:
            attendance_records.append(
                Attendance(
                    tenant=validated_data.get('tenant'),
                    student=student,
                    classroom=validated_data.get('classroom'),
                    subject=validated_data.get('subject'),
                    attendance_type=validated_data.get('attendance_type'),
                    status=validated_data.get('status'),
                    date=validated_data.get('date'),
                    session=validated_data.get('session'),
                    notes=validated_data.get('notes', ''),
                    recorded_by=validated_data.get('recorded_by')
                )
            )
        
        return Attendance.objects.bulk_create(attendance_records)


class ScoreSerializer(serializers.ModelSerializer):
    """
    Serializer for Score model.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Score
        fields = [
            'id',
            'tenant',
            'student',
            'student_name',
            'subject',
            'subject_name',
            'classroom',
            'classroom_name',
            'academic_year',
            'score_type',
            'score',
            'max_score',
            'percentage',
            'title',
            'description',
            'semester',
            'recorded_by',
            'recorded_by_name',
            'previous_score',
            'changed_at',
            'changed_by',
            'changed_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'previous_score', 'changed_at', 'changed_by',
            'created_at', 'updated_at'
        ]
    
    def get_percentage(self, obj):
        """Calculate score as percentage."""
        if obj.max_score:
            return round((obj.score / obj.max_score) * 100, 2)
        return None


class ScoreAuditSerializer(serializers.ModelSerializer):
    """
    Serializer for score audit trail - shows change history.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = Score
        fields = [
            'id',
            'student',
            'student_name',
            'subject',
            'subject_name',
            'score_type',
            'title',
            'previous_score',
            'score',
            'changed_at',
            'changed_by',
            'changed_by_name',
        ]


class TimelineEventSerializer(serializers.ModelSerializer):
    """
    Serializer for TimelineEvent model.
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = TimelineEvent
        fields = [
            'id',
            'tenant',
            'event_type',
            'title',
            'description',
            'image',
            'attendance',
            'score',
            'activity_date',
            'classroom',
            'classroom_name',
            'created_by',
            'created_by_name',
            'published',
            'published_at',
            'created_at',
            'is_read',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'published_at'
        ]
    
    def get_is_read(self, obj):
        """Check if current user has read this event."""
        if self.context.get('request'):
            user = self.context['request'].user
            if user.role == 'parent':
                notification = TimelineNotification.objects.filter(
                    timeline_event=obj,
                    parent=user
                ).first()
                return notification.is_read if notification else False
        return None


class TimelineEventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating TimelineEvent.
    """
    class Meta:
        model = TimelineEvent
        fields = [
            'event_type',
            'title',
            'description',
            'image',
            'activity_date',
            'classroom',
            'published',
        ]
    
    def validate(self, data):
        """Validate event type requirements."""
        if data.get('event_type') == 'activity' and not data.get('image'):
            raise serializers.ValidationError(
                "Foto kegiatan diperlukan untuk event foto kegiatan."
            )
        return data


class TimelineNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for TimelineNotification model.
    """
    event = TimelineEventSerializer(source='timeline_event', read_only=True)
    
    class Meta:
        model = TimelineNotification
        fields = [
            'id',
            'timeline_event',
            'event',
            'parent',
            'is_read',
            'read_at',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']