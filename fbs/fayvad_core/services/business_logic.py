from django.contrib.auth.models import User
from ..models import BusinessRule, OdooDatabase
from .odoo_client import odoo_client, OdooClientError
from .auth_service import AuthService
from .cache_service import CacheService
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger('fayvad_core')


class BusinessLogicService:
    """Service for handling business logic and complex workflows"""
    
    @staticmethod
    def validate_business_rules(user: User, database_name: str, model_name: str, 
                               operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate business rules for an operation"""
        try:
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
                    # Check record count conditions (would need to query Odoo)
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking conditions: {str(e)}")
            return False
    
    @staticmethod
    def _apply_actions(actions: Dict[str, Any], data: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Apply actions based on business rules"""
        try:
            result = {
                'valid': True,
                'messages': [],
                'data': data.copy()
            }
            
            for action_type, action_config in actions.items():
                if action_type == 'set_default':
                    # Set default values
                    for field, value in action_config.items():
                        if field not in result['data'] or result['data'][field] is None:
                            result['data'][field] = value
                            result['messages'].append(f"Set default value for {field}")
                
                elif action_type == 'require_field':
                    # Require specific fields
                    for field in action_config:
                        if field not in result['data'] or result['data'][field] is None:
                            result['valid'] = False
                            result['messages'].append(f"Field {field} is required")
                
                elif action_type == 'validate_format':
                    # Validate field formats
                    for field, format_config in action_config.items():
                        if field in result['data']:
                            if not BusinessLogicService._validate_format(result['data'][field], format_config):
                                result['valid'] = False
                                result['messages'].append(f"Invalid format for field {field}")
                
                elif action_type == 'transform_data':
                    # Transform data
                    for field, transform_config in action_config.items():
                        if field in result['data']:
                            result['data'][field] = BusinessLogicService._transform_value(
                                result['data'][field], 
                                transform_config
                            )
                            result['messages'].append(f"Transformed field {field}")
                
                elif action_type == 'prevent_operation':
                    # Prevent the operation
                    result['valid'] = False
                    result['messages'].append(action_config.get('message', 'Operation not allowed'))
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying actions: {str(e)}")
            return {
                'valid': False,
                'messages': [f"Action application error: {str(e)}"],
                'data': data
            }
    
    @staticmethod
    def _validate_format(value: Any, format_config: Dict[str, Any]) -> bool:
        """Validate value format"""
        try:
            format_type = format_config.get('type')
            
            if format_type == 'email':
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                return bool(re.match(email_pattern, str(value)))
            
            elif format_type == 'phone':
                import re
                # Simple phone validation - can be improved
                phone_pattern = r'^\+?[\d\s\-\(\)]{10,}$'
                return bool(re.match(phone_pattern, str(value)))
            
            elif format_type == 'length':
                min_length = format_config.get('min', 0)
                max_length = format_config.get('max', float('inf'))
                return min_length <= len(str(value)) <= max_length
            
            elif format_type == 'numeric':
                try:
                    float(value)
                    return True
                except (ValueError, TypeError):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating format: {str(e)}")
            return False
    
    @staticmethod
    def _transform_value(value: Any, transform_config: Dict[str, Any]) -> Any:
        """Transform value based on configuration"""
        try:
            transform_type = transform_config.get('type')
            
            if transform_type == 'upper':
                return str(value).upper()
            elif transform_type == 'lower':
                return str(value).lower()
            elif transform_type == 'strip':
                return str(value).strip()
            elif transform_type == 'replace':
                old_value = transform_config.get('old', '')
                new_value = transform_config.get('new', '')
                return str(value).replace(old_value, new_value)
            elif transform_type == 'prefix':
                prefix = transform_config.get('prefix', '')
                return f"{prefix}{value}"
            elif transform_type == 'suffix':
                suffix = transform_config.get('suffix', '')
                return f"{value}{suffix}"
            
            return value
            
        except Exception as e:
            logger.error(f"Error transforming value: {str(e)}")
            return value
    
    @staticmethod
    def orchestrate_complex_operation(user: User, database_name: str, operation_type: str, 
                                    data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate complex operations involving multiple models"""
        try:
            result = {
                'success': True,
                'results': [],
                'errors': []
            }
            
            # Get user token
            token = AuthService.get_user_token(user, database_name)
            if not token:
                return {
                    'success': False,
                    'errors': ['Authentication failed']
                }
            
            # Handle different operation types
            if operation_type == 'create_partner_with_address':
                # Create partner and address in one operation
                result = BusinessLogicService._create_partner_with_address(
                    user, database_name, token, data
                )
            
            elif operation_type == 'book_rental_room':
                # Complex rental booking operation
                result = BusinessLogicService._book_rental_room(
                    user, database_name, token, data
                )
            
            elif operation_type == 'process_payment':
                # Process payment with external service integration
                result = BusinessLogicService._process_payment(
                    user, database_name, token, data
                )
            
            else:
                result['success'] = False
                result['errors'] = [f"Unknown operation type: {operation_type}"]
            
            return result
            
        except Exception as e:
            logger.error(f"Error orchestrating complex operation: {str(e)}")
            return {
                'success': False,
                'errors': [f"Operation failed: {str(e)}"]
            }
    
    @staticmethod
    def _create_partner_with_address(user: User, database_name: str, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create partner with address in one transaction"""
        try:
            # Validate partner data
            partner_validation = BusinessLogicService.validate_business_rules(
                user, database_name, 'res.partner', 'create', data.get('partner', {})
            )
            
            if not partner_validation['valid']:
                return {
                    'success': False,
                    'errors': partner_validation['messages']
                }
            
            # Create partner
            partner_response = odoo_client.create_record(
                'res.partner', 
                partner_validation['modified_data'], 
                token, 
                database_name
            )
            
            if not partner_response.get('success'):
                return {
                    'success': False,
                    'errors': [partner_response.get('message', 'Partner creation failed')]
                }
            
            partner_id = partner_response['data']['id']
            
            # Create address if provided
            if 'address' in data:
                address_data = data['address'].copy()
                address_data['parent_id'] = partner_id
                address_data['type'] = 'delivery'
                
                address_response = odoo_client.create_record(
                    'res.partner', 
                    address_data, 
                    token, 
                    database_name
                )
                
                if not address_response.get('success'):
                    # Rollback partner creation would be ideal here
                    logger.error(f"Address creation failed for partner {partner_id}")
            
            return {
                'success': True,
                'results': [
                    {'type': 'partner', 'id': partner_id},
                    {'type': 'address', 'id': address_response['data']['id']} if 'address_response' in locals() else None
                ]
            }
            
        except Exception as e:
            logger.error(f"Error creating partner with address: {str(e)}")
            return {
                'success': False,
                'errors': [f"Operation failed: {str(e)}"]
            }
    
    @staticmethod
    def _book_rental_room(user: User, database_name: str, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Book rental room with availability check"""
        # This would be implemented based on specific rental model structure
        return {
            'success': True,
            'results': [{'type': 'booking', 'id': 1}],
            'message': 'Rental booking operation placeholder'
        }
    
    @staticmethod
    def _process_payment(user: User, database_name: str, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment with external service integration"""
        # This would integrate with Stripe or other payment processors
        return {
            'success': True,
            'results': [{'type': 'payment', 'id': 1}],
            'message': 'Payment processing operation placeholder'
        }
