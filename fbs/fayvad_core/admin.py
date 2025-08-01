from django.contrib import admin
from .models import OdooDatabase, ApiTokenMapping, RequestLog, BusinessRule, CacheEntry


@admin.register(OdooDatabase)
class OdooDatabaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'odoo_db_name', 'active', 'created_at']
    list_filter = ['active', 'created_at']
    search_fields = ['name', 'display_name', 'odoo_db_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description', 'active')
        }),
        ('Odoo Configuration', {
            'fields': ('odoo_db_name', 'base_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ApiTokenMapping)
class ApiTokenMappingAdmin(admin.ModelAdmin):
    list_display = ['user', 'database', 'active', 'expires_at', 'last_used', 'created_at']
    list_filter = ['active', 'database', 'expires_at', 'created_at']
    search_fields = ['user__username', 'database__name', 'odoo_token']
    readonly_fields = ['created_at', 'updated_at', 'last_used']
    
    fieldsets = (
        ('Mapping Information', {
            'fields': ('user', 'database', 'active')
        }),
        ('Odoo Details', {
            'fields': ('odoo_token', 'odoo_user_id', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_used'),
            'classes': ('collapse',)
        })
    )
    
    def has_change_permission(self, request, obj=None):
        # Only allow superusers to change token mappings
        return request.user.is_superuser


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ['method', 'endpoint', 'user', 'database', 'response_status', 
                   'response_time', 'created_at']
    list_filter = ['method', 'response_status', 'database', 'created_at']
    search_fields = ['endpoint', 'user__username', 'model_name', 'error_message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('method', 'endpoint', 'model_name', 'record_id', 'user', 'database')
        }),
        ('Response Information', {
            'fields': ('response_status', 'response_time', 'error_message')
        }),
        ('Client Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Data', {
            'fields': ('request_data',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
    
    def has_add_permission(self, request):
        # Don't allow manual addition of request logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Don't allow changing request logs
        return False


@admin.register(BusinessRule)
class BusinessRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'database', 'model_name', 'operation', 'active', 
                   'priority', 'created_at']
    list_filter = ['database', 'operation', 'active', 'created_at']
    search_fields = ['name', 'model_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Rule Information', {
            'fields': ('name', 'database', 'model_name', 'operation', 'active', 'priority')
        }),
        ('Rule Logic', {
            'fields': ('conditions', 'actions')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CacheEntry)
class CacheEntryAdmin(admin.ModelAdmin):
    list_display = ['key', 'database', 'expires_at', 'created_at']
    list_filter = ['database', 'expires_at', 'created_at']
    search_fields = ['key']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Cache Information', {
            'fields': ('key', 'database', 'expires_at')
        }),
        ('Value', {
            'fields': ('value',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
    
    def has_change_permission(self, request, obj=None):
        # Only allow superusers to change cache entries
        return request.user.is_superuser


# Customize admin site
admin.site.site_header = 'Fayvad Core Administration'
admin.site.site_title = 'Fayvad Core Admin'
admin.site.index_title = 'Welcome to Fayvad Core Administration'
