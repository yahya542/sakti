"""
Smart Linking Serializers.
"""

from rest_framework import serializers
from .models import ParentStudentLink, LinkRequest


class ParentStudentLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for ParentStudentLink model.
    """
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_nis = serializers.SerializerMethodField()
    
    class Meta:
        model = ParentStudentLink
        fields = [
            'id',
            'parent',
            'parent_name',
            'student',
            'student_name',
            'student_nis',
            'relation_type',
            'is_primary',
            'is_verified',
            'verified_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'verified_at', 'created_at', 'updated_at']
    
    def get_student_nis(self, obj):
        """Get student's NIS from their profile."""
        profile = getattr(obj.student, 'profile', None)
        if profile:
            return profile.nis
        return None


class ParentStudentLinkCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating ParentStudentLink manually.
    """
    class Meta:
        model = ParentStudentLink
        fields = [
            'student',
            'relation_type',
            'is_primary',
        ]
    
    def validate(self, data):
        """Validate that parent and student are not the same."""
        if self.context.get('request'):
            parent = self.context['request'].user
            if parent.id == data.get('student').id:
                raise serializers.ValidationError(
                    "Wali murid tidak bisa menjadi siswa itu sendiri."
                )
        return data


class LinkRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for LinkRequest model.
    """
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = LinkRequest
        fields = [
            'id',
            'parent',
            'parent_name',
            'student',
            'student_name',
            'requested_relation',
            'status',
            'notes',
            'approved_by',
            'approved_by_name',
            'approved_at',
            'created_at',
            'expires_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'approved_by',
            'approved_by_name',
            'approved_at',
            'created_at',
            'expires_at',
        ]


class LinkRequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating LinkRequest.
    """
    class Meta:
        model = LinkRequest
        fields = [
            'student',
            'requested_relation',
            'notes',
        ]
    
    def validate(self, data):
        """Validate that parent and student are different users."""
        if self.context.get('request'):
            parent = self.context['request'].user
            student = data.get('student')
            
            if parent.id == student.id:
                raise serializers.ValidationError(
                    "Wali murid tidak bisa menjadi siswa itu sendiri."
                )
            
            # Check if there's already a link
            existing_link = ParentStudentLink.objects.filter(
                parent=parent,
                student=student
            ).exists()
            
            if existing_link:
                raise serializers.ValidationError(
                    "Siswa ini sudah terhubung dengan akun Anda."
                )
            
            # Check if there's already a pending request
            pending_request = LinkRequest.objects.filter(
                parent=parent,
                student=student,
                status='pending'
            ).exists()
            
            if pending_request:
                raise serializers.ValidationError(
                    "Anda sudah memiliki permintaan link yang menunggu."
                )
        
        return data


class LinkRequestActionSerializer(serializers.Serializer):
    """
    Serializer for approving/rejecting link requests.
    """
    request_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_request_id(self, value):
        """Validate that the request exists."""
        if not LinkRequest.objects.filter(id=value).exists():
            raise serializers.ValidationError("Permintaan link tidak ditemukan.")
        return value
    
    def validate(self, data):
        """Validate action."""
        request = LinkRequest.objects.get(id=data.get('request_id'))
        
        if request.status != 'pending':
            raise serializers.ValidationError(
                f"Permintaan sudah diproses dengan status: {request.status}"
            )
        
        return data