"""
Smart Linking Admin Configuration.
"""

from django.contrib import admin
from .models import ParentStudentLink, LinkRequest


@admin.register(ParentStudentLink)
class ParentStudentLinkAdmin(admin.ModelAdmin):
    list_display = [
        'parent',
        'student',
        'relation_type',
        'is_primary',
        'is_verified',
        'created_at',
    ]
    list_filter = [
        'relation_type',
        'is_primary',
        'is_verified',
    ]
    search_fields = [
        'parent__first_name',
        'parent__last_name',
        'student__first_name',
        'student__last_name',
    ]
    raw_id_fields = ['parent', 'student']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(LinkRequest)
class LinkRequestAdmin(admin.ModelAdmin):
    list_display = [
        'parent',
        'student',
        'requested_relation',
        'status',
        'created_at',
        'expires_at',
    ]
    list_filter = [
        'status',
        'requested_relation',
    ]
    search_fields = [
        'parent__first_name',
        'parent__last_name',
        'student__first_name',
        'student__last_name',
    ]
    raw_id_fields = ['parent', 'student', 'approved_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Approve selected pending requests."""
        from .signals import approve_link_request
        
        count = 0
        for link_request in queryset.filter(status='pending'):
            approve_link_request(link_request.id, request.user)
            count += 1
        
        self.message_user(request, f'{count} permintaan berhasil disetujui.')
    
    approve_requests.short_description = 'Setuju permintaan yang dipilih'
    
    def reject_requests(self, request, queryset):
        """Reject selected pending requests."""
        from .signals import reject_link_request
        
        count = 0
        for link_request in queryset.filter(status='pending'):
            reject_link_request(link_request.id, request.user)
            count += 1
        
        self.message_user(request, f'{count} permintaan berhasil ditolak.')
    
    reject_requests.short_description = 'Tolak permintaan yang dipilih'