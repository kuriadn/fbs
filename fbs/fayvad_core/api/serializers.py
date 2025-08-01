from rest_framework import serializers
from ..models import OdooDatabase, ApiTokenMapping, RequestLog, BusinessRule
from ..workflows.workflow_models import WorkflowDefinition, WorkflowInstance, WorkflowTransition, WorkflowExecutionLog


class OdooDatabaseSerializer(serializers.ModelSerializer):
    """Serializer for OdooDatabase model"""
    
    class Meta:
        model = OdooDatabase
        fields = ['id', 'name', 'display_name', 'description', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ApiTokenMappingSerializer(serializers.ModelSerializer):
    """Serializer for ApiTokenMapping model"""
    
    class Meta:
        model = ApiTokenMapping
        fields = ['id', 'database', 'active', 'expires_at', 'last_used', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'odoo_token', 'odoo_user_id', 'created_at', 'updated_at']


class RequestLogSerializer(serializers.ModelSerializer):
    """Serializer for RequestLog model"""
    
    class Meta:
        model = RequestLog
        fields = ['id', 'method', 'endpoint', 'model_name', 'record_id', 'response_status', 
                 'response_time', 'error_message', 'created_at']
        read_only_fields = ['id', 'user', 'database', 'created_at']


class BusinessRuleSerializer(serializers.ModelSerializer):
    """Serializer for BusinessRule model"""
    
    class Meta:
        model = BusinessRule
        fields = ['id', 'name', 'model_name', 'operation', 'conditions', 'actions', 
                 'active', 'priority', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# Workflow Serializers
class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowDefinition model"""
    
    class Meta:
        model = WorkflowDefinition
        fields = [
            'id', 'name', 'description', 'model_name', 'database', 'trigger_type',
            'trigger_conditions', 'workflow_steps', 'states', 'initial_state',
            'requires_approval', 'approval_roles', 'is_scheduled', 'schedule_cron',
            'schedule_interval', 'active', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowInstance model"""
    
    workflow_definition_name = serializers.CharField(source='workflow_definition.name', read_only=True)
    initiated_by_username = serializers.CharField(source='initiated_by.username', read_only=True)
    current_assignee_username = serializers.CharField(source='current_assignee.username', read_only=True)
    
    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'workflow_definition', 'workflow_definition_name', 'odoo_record_id',
            'odoo_model_name', 'database', 'current_state', 'workflow_data', 'context_data',
            'current_step', 'completed_steps', 'failed_steps', 'approval_status',
            'approval_history', 'status', 'started_at', 'completed_at', 'last_executed_at',
            'initiated_by', 'initiated_by_username', 'current_assignee', 'current_assignee_username'
        ]
        read_only_fields = ['id', 'started_at', 'last_executed_at']


class WorkflowTransitionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowTransition model"""
    
    class Meta:
        model = WorkflowTransition
        fields = [
            'id', 'workflow_definition', 'from_state', 'to_state', 'conditions',
            'actions', 'name', 'description', 'required_roles', 'requires_approval',
            'button_text', 'button_style', 'order'
        ]
        read_only_fields = ['id']


class WorkflowExecutionLogSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowExecutionLog model"""
    
    executed_by_username = serializers.CharField(source='executed_by.username', read_only=True)
    
    class Meta:
        model = WorkflowExecutionLog
        fields = [
            'id', 'workflow_instance', 'step_name', 'step_type', 'status',
            'input_data', 'output_data', 'error_message', 'execution_time_ms',
            'executed_by', 'executed_by_username', 'executed_at'
        ]
        read_only_fields = ['id', 'executed_at']


# BI Serializers
class AnalyticsRequestSerializer(serializers.Serializer):
    """Serializer for analytics requests"""
    model = serializers.CharField(max_length=255)
    report_type = serializers.CharField(max_length=50, default='summary')
    filters = serializers.DictField(required=False, default=dict)
    group_by = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    measures = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    date_range = serializers.DictField(required=False, default=dict)


class SalesReportSerializer(serializers.Serializer):
    """Serializer for sales report requests"""
    period = serializers.CharField(max_length=20, default='month')
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)


class DashboardRequestSerializer(serializers.Serializer):
    """Serializer for dashboard requests"""
    dashboard_type = serializers.ChoiceField(choices=[
        ('sales', 'Sales'),
        ('inventory', 'Inventory'),
        ('financial', 'Financial'),
        ('operations', 'Operations')
    ])


class ReportExecutionSerializer(serializers.Serializer):
    """Serializer for report execution requests"""
    report_id = serializers.IntegerField()
    parameters = serializers.DictField(required=False, default=dict)
    format = serializers.ChoiceField(choices=['json', 'pdf', 'xlsx'], default='json')


# Generic Serializers
class BusinessOperationSerializer(serializers.Serializer):
    """Serializer for business operation requests"""
    operation_type = serializers.CharField(max_length=100)
    data = serializers.DictField()
    
    def validate_operation_type(self, value):
        """Validate operation type"""
        allowed_operations = [
            'create_partner_with_address',
            'book_rental_room',
            'process_payment'
        ]
        
        if value not in allowed_operations:
            raise serializers.ValidationError(f"Invalid operation type. Allowed: {allowed_operations}")
        
        return value


class GenericModelSerializer(serializers.Serializer):
    """Generic serializer for model operations"""
    data = serializers.DictField()
    
    def validate_data(self, value):
        """Validate data dictionary"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data must be a dictionary")
        
        return value


class DomainSerializer(serializers.Serializer):
    """Serializer for domain queries"""
    domain = serializers.ListField(required=False, default=list)
    fields = serializers.ListField(child=serializers.CharField(), required=False)
    order = serializers.CharField(required=False, default='id')
    limit = serializers.IntegerField(required=False, default=100, min_value=1, max_value=1000)
    offset = serializers.IntegerField(required=False, default=0, min_value=0)
    
    def validate_domain(self, value):
        """Validate domain format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Domain must be a list")
        
        # Basic domain validation
        for item in value:
            if isinstance(item, str) and item not in ['&', '|', '!']:
                raise serializers.ValidationError(f"Invalid domain operator: {item}")
            elif isinstance(item, (list, tuple)) and len(item) != 3:
                raise serializers.ValidationError("Domain clauses must have exactly 3 elements")
        
        return value


class ProfileRequestSerializer(serializers.Serializer):
    """Serializer for profile requests"""
    models = serializers.ListField(child=serializers.CharField(), required=False)
    model = serializers.CharField(required=False)
    
    def validate(self, data):
        """Validate that either models or model is provided"""
        if 'models' in data and 'model' in data:
            raise serializers.ValidationError("Provide either 'models' or 'model', not both")
        
        return data


class CacheStatsSerializer(serializers.Serializer):
    """Serializer for cache statistics"""
    total_entries = serializers.IntegerField()
    expired_entries = serializers.IntegerField()
    active_entries = serializers.IntegerField()
    database_entries = serializers.IntegerField(required=False)
    database_active_entries = serializers.IntegerField(required=False)


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check responses"""
    status = serializers.CharField()
    message = serializers.CharField(required=False)
    components = serializers.DictField(required=False)
    error = serializers.CharField(required=False)


# Base Serializer for Common Patterns
class BaseModelSerializer(serializers.ModelSerializer):
    """Base serializer with common patterns"""
    
    def get_fields(self):
        """Add created_at and updated_at to read_only_fields if they exist"""
        fields = super().get_fields()
        if 'created_at' in fields:
            fields['created_at'].read_only = True
        if 'updated_at' in fields:
            fields['updated_at'].read_only = True
        return fields


class BaseResponseSerializer(serializers.Serializer):
    """Base serializer for API responses"""
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    data = serializers.DictField(required=False)
    error = serializers.CharField(required=False)
