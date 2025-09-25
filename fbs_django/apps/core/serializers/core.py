"""
FBS Core API Serializers

DRF serializers for core FBS models.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from ..models import (
    FBSSolution, FBSUser, FBSAuditLog, FBSAPIToken, FBSSystemSettings
)


class FBSSolutionSerializer(serializers.ModelSerializer):
    """Serializer for FBS solutions"""

    user_count = serializers.SerializerMethodField()
    database_status = serializers.SerializerMethodField()

    class Meta:
        model = FBSSolution
        fields = [
            'id', 'name', 'display_name', 'database_name',
            'odoo_database_name', 'is_active', 'created_at',
            'updated_at', 'user_count', 'database_status'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_count', 'database_status']

    def get_user_count(self, obj):
        """Get user count for this solution"""
        return obj.users.count()

    def get_database_status(self, obj):
        """Get database connection status"""
        # In a real implementation, this would check actual DB connectivity
        return "connected"


class FBSUserSerializer(serializers.ModelSerializer):
    """Serializer for FBS users"""

    solution_name = serializers.CharField(source='solution.name', read_only=True)
    solution_display_name = serializers.CharField(source='solution.display_name', read_only=True)

    class Meta:
        model = FBSUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_solution_admin', 'date_joined',
            'last_login', 'solution', 'solution_name',
            'solution_display_name', 'odoo_user_id', 'phone', 'department'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login',
            'solution_name', 'solution_display_name'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        """Update user with password handling"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class FBSAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs"""

    user_username = serializers.CharField(source='user.username', read_only=True)
    solution_name = serializers.CharField(source='solution.name', read_only=True)

    class Meta:
        model = FBSAuditLog
        fields = [
            'id', 'user', 'user_username', 'solution', 'solution_name',
            'action', 'resource_type', 'resource_id', 'details',
            'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = [
            'id', 'timestamp', 'user_username', 'solution_name'
        ]


class FBSAPITokenSerializer(serializers.ModelSerializer):
    """Serializer for API tokens"""

    user_username = serializers.CharField(source='user.username', read_only=True)
    solution_name = serializers.CharField(source='user.solution.name', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = FBSAPIToken
        fields = [
            'id', 'user', 'user_username', 'solution_name', 'name',
            'token', 'scopes', 'is_active', 'expires_at',
            'last_used_at', 'created_at', 'is_expired'
        ]
        read_only_fields = [
            'id', 'token', 'created_at', 'last_used_at',
            'user_username', 'solution_name', 'is_expired'
        ]

    def get_is_expired(self, obj):
        """Check if token is expired"""
        return obj.is_expired()


class FBSSystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for system settings"""

    class Meta:
        model = FBSSystemSettings
        fields = [
            'id', 'key', 'value', 'setting_type',
            'description', 'is_system_setting', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    """Serializer for login request"""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh request"""

    token = serializers.CharField(required=True)
