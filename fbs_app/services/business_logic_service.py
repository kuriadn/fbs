"""
FBS App Business Logic Service

Service for handling business logic and complex workflows.
"""

import logging
from typing import Dict, Any, List, Optional
from django.contrib.auth.models import User
from django.conf import settings

logger = logging.getLogger('fbs_app')


class BusinessLogicService:
    """Service for handling business logic and complex workflows"""
    
    @staticmethod
    def validate_business_rules(user: User, database_name: str, model_name: str, 
                               operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate business rules for an operation"""
        try:
            from ..models import BusinessRule, OdooDatabase
            
            database = OdooDatabase.objects.get(name=database_name, active=True)
            
            # Get applicable business rules
            rules = BusinessRule.objects.filter(
                database=database,
                model_name=model_name,
                operation=operation,
                active=True
            ).order_by('priority')
            
            validation_results = {
                'valid': True,
                'messages': [],
                'modified_data': data.copy()
            }
            
            for rule in rules:
                # Check conditions
                if BusinessLogicService._check_conditions(rule.conditions, data, user):
                    # Apply actions
                    action_result = BusinessLogicService._apply_actions(rule.actions, validation_results['modified_data'], user)
                    
                    if not action_result['valid']:
                        validation_results['valid'] = False
                        validation_results['messages'].extend(action_result['messages'])
                    else:
                        validation_results['modified_data'] = action_result['data']
                        validation_results['messages'].extend(action_result['messages'])
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating business rules: {str(e)}")
            return {
                'valid': False,
                'messages': [f"Business rule validation error: {str(e)}"],
                'modified_data': data
            }
    
    @staticmethod
    def _check_conditions(conditions: Dict[str, Any], data: Dict[str, Any], user: User) -> bool:
        """Check if conditions are met"""
        try:
            # Simple condition checking - can be extended for complex logic
            for field, condition in conditions.items():
                if field == 'user_group':
                    # Check user group membership
                    if not user.groups.filter(name=condition).exists():
                        return False
                elif field == 'field_value':
                    # Check field value conditions
                    field_name = condition['field']
                    operator = condition['operator']
                    value = condition['value']
                    
                    if field_name in data:
                        field_value = data[field_name]
                        
                        if operator == 'equals' and field_value != value:
                            return False
                        elif operator == 'not_equals' and field_value == value:
                            return False
                        elif operator == 'in' and field_value not in value:
                            return False
                        elif operator == 'not_in' and field_value in value:
                            return False
                        elif operator == 'greater_than' and field_value <= value:
                            return False
                        elif operator == 'less_than' and field_value >= value:
                            return False
                elif field == 'record_count':
                    # Check record count conditions
                    model_name = condition.get('model')
                    operator = condition.get('operator', 'equals')
                    expected_count = condition.get('value', 0)
                    
                    if model_name:
                        # This would query the database for record count
                        # For now, we'll return True as a placeholder
                        return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking conditions: {str(e)}")
            return False
    
    @staticmethod
    def _apply_actions(actions: Dict[str, Any], data: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Apply business rule actions"""
        try:
            result = {
                'valid': True,
                'messages': [],
                'data': data.copy()
            }
            
            for action_type, action_data in actions.items():
                if action_type == 'set_field_value':
                    # Set field value
                    field_name = action_data.get('field')
                    value = action_data.get('value')
                    
                    if field_name and value is not None:
                        result['data'][field_name] = value
                        result['messages'].append(f"Set {field_name} to {value}")
                
                elif action_type == 'validate_field':
                    # Validate field value
                    field_name = action_data.get('field')
                    validation_type = action_data.get('validation_type')
                    validation_params = action_data.get('validation_params', {})
                    
                    if field_name in result['data']:
                        field_value = result['data'][field_name]
                        
                        if validation_type == 'required' and not field_value:
                            result['valid'] = False
                            result['messages'].append(f"Field {field_name} is required")
                        
                        elif validation_type == 'min_length' and len(str(field_value)) < validation_params.get('min_length', 0):
                            result['valid'] = False
                            result['messages'].append(f"Field {field_name} must be at least {validation_params['min_length']} characters")
                        
                        elif validation_type == 'max_length' and len(str(field_value)) > validation_params.get('max_length', 0):
                            result['valid'] = False
                            result['messages'].append(f"Field {field_name} must be no more than {validation_params['max_length']} characters")
                
                elif action_type == 'transform_field':
                    # Transform field value
                    field_name = action_data.get('field')
                    transform_type = action_data.get('transform_type')
                    
                    if field_name in result['data']:
                        field_value = result['data'][field_name]
                        
                        if transform_type == 'uppercase' and isinstance(field_value, str):
                            result['data'][field_name] = field_value.upper()
                            result['messages'].append(f"Transformed {field_name} to uppercase")
                        
                        elif transform_type == 'lowercase' and isinstance(field_value, str):
                            result['data'][field_name] = field_value.lower()
                            result['messages'].append(f"Transformed {field_name} to lowercase")
                        
                        elif transform_type == 'trim' and isinstance(field_value, str):
                            result['data'][field_name] = field_value.strip()
                            result['messages'].append(f"Trimmed {field_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying actions: {str(e)}")
            return {
                'valid': False,
                'messages': [f"Action application error: {str(e)}"],
                'data': data
            }
    
    @staticmethod
    def execute_business_workflow(workflow_name: str, context: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Execute a business workflow"""
        try:
            from ..models import BusinessRule
            
            # Get workflow rules
            workflow_rules = BusinessRule.objects.filter(
                workflow_name=workflow_name,
                active=True
            ).order_by('priority')
            
            if not workflow_rules.exists():
                return {
                    'success': False,
                    'error': f'Workflow {workflow_name} not found'
                }
            
            # Execute workflow steps
            workflow_context = context.copy()
            execution_log = []
            
            for rule in workflow_rules:
                # Validate rule conditions
                if BusinessLogicService._check_conditions(rule.conditions, workflow_context, user):
                    # Apply rule actions
                    action_result = BusinessLogicService._apply_actions(rule.actions, workflow_context, user)
                    
                    if not action_result['valid']:
                        execution_log.append({
                            'rule_id': rule.id,
                            'status': 'failed',
                            'messages': action_result['messages']
                        })
                        
                        return {
                            'success': False,
                            'error': 'Workflow execution failed',
                            'execution_log': execution_log
                        }
                    else:
                        workflow_context = action_result['data']
                        execution_log.append({
                            'rule_id': rule.id,
                            'status': 'success',
                            'messages': action_result['messages']
                        })
            
            return {
                'success': True,
                'workflow_name': workflow_name,
                'final_context': workflow_context,
                'execution_log': execution_log
            }
            
        except Exception as e:
            logger.error(f"Error executing business workflow: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_business_rules_summary(database_name: str = None, model_name: str = None) -> Dict[str, Any]:
        """Get summary of business rules"""
        try:
            from ..models import BusinessRule
            
            # Build query
            query = {'active': True}
            if database_name:
                query['database__name'] = database_name
            if model_name:
                query['model_name'] = model_name
            
            # Get rules
            rules = BusinessRule.objects.filter(**query)
            
            # Group by model and operation
            summary = {}
            for rule in rules:
                model = rule.model_name
                operation = rule.operation
                
                if model not in summary:
                    summary[model] = {}
                
                if operation not in summary[model]:
                    summary[model][operation] = []
                
                summary[model][operation].append({
                    'id': rule.id,
                    'name': rule.name,
                    'priority': rule.priority,
                    'description': rule.description
                })
            
            return {
                'success': True,
                'summary': summary,
                'total_rules': rules.count()
            }
            
        except Exception as e:
            logger.error(f"Error getting business rules summary: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
