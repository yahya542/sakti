"""
Custom OpenAPI Schema for Multi-tenant SAKTI Application
Handles tenant-aware schema generation
"""

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import get_doc, force_instance


class TenantAwareSchema(AutoSchema):
    """
    Custom schema that adds tenant information to API documentation.
    For multi-tenant applications, this helps document which endpoints
    require tenant context.
    """
    
    def get_tags(self):
        tags = super().get_tags()
        
        # Add tenant-aware tag to all tenant-specific endpoints
        if hasattr(self.view, 'tenant_aware') and self.view.tenant_aware:
            if 'Tenant-Aware' not in tags:
                tags.append('Tenant-Aware')
        
        return tags
    
    def get_operation_id(self, *args, **kwargs):
        # Generate more descriptive operation IDs
        return super().get_operation_id(*args, **kwargs)
    
    def get_description(self, *args, **kwargs):
        description = super().get_description(*args, **kwargs)
        
        # Add tenant context note for tenant-aware endpoints
        if hasattr(self.view, 'tenant_aware') and self.view.tenant_aware:
            tenant_note = "\n\n**Note:** This endpoint is tenant-aware and requires valid tenant context."
            description = (description or "") + tenant_note
        
        return description


def get_schema_view(title, description, version='1.0.0'):
    """
    Factory function to create a tenant-aware schema view.
    """
    from drf_spectacular.views import SpectacularAPIView
    from drf_spectacular.generators import SchemaGenerator
    from drf_spectacular.extensions import OpenApiSchemaExtension
    
    class TenantSchemaGenerator(SchemaGenerator):
        def get_schema(self, request=None, public=False):
            schema = super().get_schema(request, public)
            
            # Add tenant information to components
            if 'components' not in schema:
                schema['components'] = {}
            
            if 'securitySchemes' not in schema['components']:
                schema['components']['securitySchemes'] = {
                    'Bearer': {
                        'type': 'http',
                        'scheme': 'bearer',
                        'description': 'JWT token authentication. Use the `/api/v1/auth/login/` endpoint to obtain a token.'
                    },
                    'Tenant-Header': {
                        'type': 'apiKey',
                        'in': 'header',
                        'name': 'X-Tenant-ID',
                        'description': 'Tenant ID header (required for multi-tenant endpoints)'
                    }
                }
            
            return schema
    
    return TenantSchemaGenerator
