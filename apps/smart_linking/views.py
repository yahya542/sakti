"""
Smart Linking Views.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import ParentStudentLink, LinkRequest
from .serializers import (
    ParentStudentLinkSerializer,
    ParentStudentLinkCreateSerializer,
    LinkRequestSerializer,
    LinkRequestCreateSerializer,
    LinkRequestActionSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=['Smart Linking'],
        summary='Daftar tautan siswa-orang tua',
        description='Mengambil daftar semua tautan siswa-orang tua.'
    ),
    create=extend_schema(
        tags=['Smart Linking'],
        summary='Buat tautan',
        description='Membuat tautan siswa-orang tua baru.'
    ),
    retrieve=extend_schema(
        tags=['Smart Linking'],
        summary='Detail tautan',
        description='Mengambil informasi detail tautan tertentu.'
    ),
    update=extend_schema(
        tags=['Smart Linking'],
        summary='Perbarui tautan',
        description='Memperbarui informasi tautan.'
    ),
    destroy=extend_schema(
        tags=['Smart Linking'],
        summary='Hapus tautan',
        description='Menghapus tautan siswa-orang tua.'
    )
)
class ParentStudentLinkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing parent-student links.
    
    Parents can view their linked students.
    Admins can manage all links.
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ParentStudentLinkCreateSerializer
        return ParentStudentLinkSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Parents can only see their own links
        if user.role == 'parent':
            return ParentStudentLink.objects.filter(parent=user)
        
        # Admins and teachers can see all links
        return ParentStudentLink.objects.all()
    
    def perform_create(self, serializer):
        """Set the parent to current user."""
        serializer.save(parent=self.request.user)


@extend_schema_view(
    list=extend_schema(
        tags=['Smart Linking'],
        summary='Daftar permintaan tautan',
        description='Mengambil daftar semua permintaan tautan.'
    ),
    create=extend_schema(
        tags=['Smart Linking'],
        summary='Buat permintaan tautan',
        description='Membuat permintaan tautan baru.'
    ),
    retrieve=extend_schema(
        tags=['Smart Linking'],
        summary='Detail permintaan tautan',
        description='Mengambil informasi detail permintaan tautan tertentu.'
    ),
    update=extend_schema(
        tags=['Smart Linking'],
        summary='Perbarui permintaan tautan',
        description='Memperbarui informasi permintaan tautan.'
    ),
    destroy=extend_schema(
        tags=['Smart Linking'],
        summary='Hapus permintaan tautan',
        description='Menghapus permintaan tautan.'
    )
)
class LinkRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing link requests.
    
    Parents can create and view their own requests.
    Admins can approve/reject requests.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LinkRequestSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LinkRequestCreateSerializer
        return LinkRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Parents can only see their own requests
        if user.role == 'parent':
            return LinkRequest.objects.filter(parent=user)
        
        # Admins can see all pending requests
        if user.role in ['admin', 'super_admin']:
            return LinkRequest.objects.filter(status='pending')
        
        return LinkRequest.objects.none()
    
    def perform_create(self, serializer):
        """Set the parent to current user."""
        serializer.save(parent=self.request.user)
    
    @extend_schema(
        tags=['Smart Linking'],
        summary='Setuju permintaan tautan',
        description='Menyetujuui permintaan tautan. Hanya untuk admin.'
    )
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a link request (Admin only).
        """
        if request.user.role not in ['admin', 'super_admin']:
            return Response(
                {'error': 'Anda tidak memiliki izin untuk menyetujui permintaan ini.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            link_request = LinkRequest.objects.get(pk=pk)
        except LinkRequest.DoesNotExist:
            return Response(
                {'error': 'Permintaan tidak ditemukan.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if link_request.status != 'pending':
            return Response(
                {'error': 'Permintaan sudah diproses.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import and use the helper function
        from .signals import approve_link_request
        parent_student_link = approve_link_request(pk, request.user)
        
        return Response(
            ParentStudentLinkSerializer(parent_student_link).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        tags=['Smart Linking'],
        summary='Tolak permintaan tautan',
        description='Menolak permintaan tautan. Hanya untuk admin.'
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a link request (Admin only).
        """
        if request.user.role not in ['admin', 'super_admin']:
            return Response(
                {'error': 'Anda tidak memiliki izin untuk menolak permintaan ini.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            link_request = LinkRequest.objects.get(pk=pk)
        except LinkRequest.DoesNotExist:
            return Response(
                {'error': 'Permintaan tidak ditemukan.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if link_request.status != 'pending':
            return Response(
                {'error': 'Permintaan sudah diproses.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import and use the helper function
        from .signals import reject_link_request
        rejected_request = reject_link_request(pk, request.user)
        
        return Response(
            LinkRequestSerializer(rejected_request).data,
            status=status.HTTP_200_OK
        )


class StudentLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for students to view their linked parents.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ParentStudentLinkSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Only students can access this view
        if user.role != 'student':
            return ParentStudentLink.objects.none()
        
        return ParentStudentLink.objects.filter(student=user)