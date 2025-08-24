"""
Admin interface for FBS License Manager
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import SolutionLicense, FeatureUsage, LicenseManager


@admin.register(SolutionLicense)
class SolutionLicenseAdmin(admin.ModelAdmin):
    list_display = [
        'solution_name', 'license_type', 'status', 'source', 
        'created_at', 'updated_at'
    ]
    list_filter = ['license_type', 'status', 'source', 'created_at']
    search_fields = ['solution_name']
    readonly_fields = ['created_at', 'updated_at', 'decrypted_license_key']
    ordering = ['solution_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('solution_name', 'license_type', 'status')
        }),
        ('License Key', {
            'fields': ('license_key', 'decrypted_license_key'),
            'description': 'License key is encrypted for security'
        }),
        ('Features & Limits', {
            'fields': ('features', 'limits'),
            'description': 'Features and limits in JSON format'
        }),
        ('Timing', {
            'fields': ('expiry_date', 'created_at', 'updated_at')
        }),
        ('Source', {
            'fields': ('source',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly based on conditions"""
        if obj and obj.source == 'external':
            return self.readonly_fields + ('features', 'limits')
        return self.readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of active licenses"""
        if obj and obj.status == 'active':
            return False
        return super().has_delete_permission(request, obj)
    
    def decrypted_license_key(self, obj):
        """Display decrypted license key"""
        if obj.license_key:
            try:
                decrypted = obj.get_decrypted_license_key()
                if decrypted:
                    return f"🔓 {decrypted[:8]}...{decrypted[-4:] if len(decrypted) > 12 else ''}"
                else:
                    return "🔒 [Encrypted]"
            except Exception:
                return "🔒 [Encrypted]"
        return "—"
    
    decrypted_license_key.short_description = 'Decrypted Key'


@admin.register(FeatureUsage)
class FeatureUsageAdmin(admin.ModelAdmin):
    list_display = [
        'solution_name', 'feature_name', 'usage_count', 
        'last_updated', 'usage_percentage'
    ]
    list_filter = ['solution_name', 'feature_name', 'last_updated']
    search_fields = ['solution_name', 'feature_name']
    readonly_fields = ['last_updated']
    ordering = ['solution_name', 'feature_name']
    
    def usage_percentage(self, obj):
        """Display usage as percentage of limit"""
        try:
            # Get license for this solution
            license_record = SolutionLicense.get_license_for_solution(obj.solution_name)
            if license_record:
                limits = license_record.get_limits_dict()
                limit = limits.get(obj.feature_name, -1)
                
                if limit == -1:  # Unlimited
                    return format_html('<span style="color: green;">∞ Unlimited</span>')
                elif limit == 0:
                    return format_html('<span style="color: red;">N/A</span>')
                else:
                    percentage = (obj.usage_count / limit) * 100
                    if percentage >= 90:
                        color = 'red'
                    elif percentage >= 75:
                        color = 'orange'
                    else:
                        color = 'green'
                    
                    return format_html(
                        '<span style="color: {};">{:.1f}%</span>',
                        color, percentage
                    )
        except Exception:
            pass
        
        return format_html('<span style="color: gray;">Unknown</span>')
    
    usage_percentage.short_description = 'Usage %'
    
    def has_add_permission(self, request):
        """Prevent manual creation of usage records"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow viewing but not editing"""
        return request.method == 'GET'


@admin.register(LicenseManager)
class LicenseManagerAdmin(admin.ModelAdmin):
    list_display = ['id']
    readonly_fields = ['id']
    
    def has_add_permission(self, request):
        """This is a utility model, not for direct creation"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """This is a utility model, not for deletion"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """This is a utility model, read-only"""
        return request.method == 'GET'

