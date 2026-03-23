"""
Activities Admin Configuration.
"""

from django.contrib import admin
from .models import Attendance, Score, TimelineEvent, TimelineNotification


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'classroom',
        'subject',
        'attendance_type',
        'status',
        'date',
        'session',
        'recorded_by',
    ]
    list_filter = [
        'attendance_type',
        'status',
        'date',
        'classroom',
    ]
    search_fields = [
        'student__first_name',
        'student__last_name',
        'notes',
    ]
    raw_id_fields = ['student', 'classroom', 'subject', 'recorded_by']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'subject',
        'score_type',
        'score',
        'max_score',
        'semester',
        'academic_year',
        'recorded_by',
    ]
    list_filter = [
        'score_type',
        'semester',
        'academic_year',
        'subject',
    ]
    search_fields = [
        'student__first_name',
        'student__last_name',
        'title',
    ]
    raw_id_fields = ['student', 'subject', 'classroom', 'academic_year', 'recorded_by', 'changed_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('tenant', 'student', 'subject', 'classroom', 'academic_year')
        }),
        ('Nilai', {
            'fields': ('score_type', 'score', 'max_score', 'title', 'description', 'semester')
        }),
        ('Audit Trail', {
            'fields': ('recorded_by', 'previous_score', 'changed_at', 'changed_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_type',
        'title',
        'classroom',
        'published',
        'created_by',
        'created_at',
    ]
    list_filter = [
        'event_type',
        'published',
        'created_at',
    ]
    search_fields = ['title', 'description']
    raw_id_fields = ['attendance', 'score', 'classroom', 'created_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    actions = ['publish_events', 'unpublish_events']
    
    def publish_events(self, request, queryset):
        queryset.update(published=True, published_at=timezone.now())
        self.message_user(request, f'{queryset.count()} event dipublikasikan.')
    
    publish_events.short_description = 'Publikasikan event yang dipilih'
    
    def unpublish_events(self, request, queryset):
        queryset.update(published=False)
        self.message_user(request, f'{queryset.count()} event tidak dipublikasikan.')
    
    unpublish_events.short_description = 'Batalkan publikasi event yang dipilih'


@admin.register(TimelineNotification)
class TimelineNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'timeline_event',
        'parent',
        'is_read',
        'read_at',
        'created_at',
    ]
    list_filter = ['is_read', 'created_at']
    raw_id_fields = ['timeline_event', 'parent']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


# Import timezone
from django.utils import timezone