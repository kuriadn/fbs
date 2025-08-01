from django.contrib import admin
from fayvad_core.models import FBSDiscovery, FBSSolutionSchema, FBSSchemaMigration


@admin.register(FBSDiscovery)
class FBSDiscoveryAdmin(admin.ModelAdmin):
    """Admin interface for FBS Discovery management"""
    
    list_display = [
        'name', 'discovery_type', 'domain', 'version', 
        'is_active', 'discovered_at', 'updated_at'
    ]
    
    list_filter = [
        'discovery_type', 'domain', 'is_active', 
        'discovered_at', 'updated_at'
    ]
    
    search_fields = ['name', 'domain', 'discovery_type']
    
    readonly_fields = ['discovered_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'discovery_type', 'domain', 'version')
        }),
        ('Metadata', {
            'fields': ('metadata', 'schema_definition'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'discovered_at', 'updated_at')
        }),
    )
    
    actions = ['activate_discoveries', 'deactivate_discoveries']
    
    def activate_discoveries(self, request, queryset):
        """Activate selected discoveries"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} discoveries activated successfully.')
    activate_discoveries.short_description = "Activate selected discoveries"
    
    def deactivate_discoveries(self, request, queryset):
        """Deactivate selected discoveries"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} discoveries deactivated successfully.')
    deactivate_discoveries.short_description = "Deactivate selected discoveries"


@admin.register(FBSSolutionSchema)
class FBSSolutionSchemaAdmin(admin.ModelAdmin):
    """Admin interface for FBS Solution Schema management"""
    
    list_display = [
        'solution_name', 'database_name', 'schema_version', 
        'is_active', 'created_at', 'updated_at'
    ]
    
    list_filter = ['is_active', 'schema_version', 'created_at', 'updated_at']
    
    search_fields = ['solution_name', 'database_name']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Solution Information', {
            'fields': ('solution_name', 'schema_version')
        }),
        ('Database Configuration', {
            'fields': ('database_name', 'database_user', 'database_password')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['activate_schemas', 'deactivate_schemas']
    
    def activate_schemas(self, request, queryset):
        """Activate selected schemas"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} schemas activated successfully.')
    activate_schemas.short_description = "Activate selected schemas"
    
    def deactivate_schemas(self, request, queryset):
        """Deactivate selected schemas"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} schemas deactivated successfully.')
    deactivate_schemas.short_description = "Deactivate selected schemas"


@admin.register(FBSSchemaMigration)
class FBSSchemaMigrationAdmin(admin.ModelAdmin):
    """Admin interface for FBS Schema Migration management"""
    
    list_display = [
        'solution_name', 'table_name', 'migration_type', 
        'status', 'executed_at', 'executed_by'
    ]
    
    list_filter = [
        'migration_type', 'status', 'executed_at', 'solution_name'
    ]
    
    search_fields = ['solution_name', 'table_name', 'executed_by']
    
    readonly_fields = ['executed_at']
    
    fieldsets = (
        ('Migration Information', {
            'fields': ('solution_name', 'table_name', 'migration_type')
        }),
        ('Schema Changes', {
            'fields': ('old_schema', 'new_schema'),
            'classes': ('collapse',)
        }),
        ('Execution Details', {
            'fields': ('status', 'executed_at', 'executed_by', 'error_message')
        }),
    )
    
    actions = ['mark_as_success', 'mark_as_failed']
    
    def mark_as_success(self, request, queryset):
        """Mark selected migrations as successful"""
        updated = queryset.update(status='success')
        self.message_user(request, f'{updated} migrations marked as successful.')
    mark_as_success.short_description = "Mark as successful"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected migrations as failed"""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} migrations marked as failed.')
    mark_as_failed.short_description = "Mark as failed" 