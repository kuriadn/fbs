"""
FBS App Field Merger Service

Service for merging data from Odoo models with custom fields stored in Django.
It allows clients to request any field names, and the system intelligently combines
data from both sources.
"""

import logging
from typing import Dict, List, Any, Tuple
from django.conf import settings

logger = logging.getLogger('fbs_app')


class FieldMergerService:
    """Service for merging Odoo fields with custom Django fields"""
    
    @staticmethod
    def split_fields_by_source(model_name: str, requested_fields: List[str], 
                              available_odoo_fields: List[str], database_name: str) -> Tuple[List[str], List[str]]:
        """
        Split requested fields into Odoo fields and custom fields
        
        Args:
            model_name: Name of the Odoo model
            requested_fields: List of fields requested by client
            available_odoo_fields: List of fields available in Odoo
            database_name: Name of the solution database
            
        Returns:
            Tuple of (odoo_fields, custom_fields)
        """
        if not requested_fields:
            return [], []
        
        odoo_fields = []
        custom_fields = []
        
        for field in requested_fields:
            if field in available_odoo_fields:
                odoo_fields.append(field)
            else:
                custom_fields.append(field)
                logger.info(f"Field '{field}' not found in Odoo model '{model_name}', will be retrieved from Django custom fields")
        
        return odoo_fields, custom_fields
    
    @staticmethod
    def merge_odoo_and_custom_data(odoo_data: List[Dict], custom_fields: List[str], 
                                  model_name: str, database_name: str) -> List[Dict]:
        """
        Merge Odoo data with custom field data
        
        Args:
            odoo_data: List of records from Odoo
            custom_fields: List of custom field names to retrieve
            model_name: Name of the Odoo model
            database_name: Name of the solution database
            
        Returns:
            List of merged records
        """
        if not custom_fields or not odoo_data:
            return odoo_data
        
        # Extract record IDs from Odoo data
        record_ids = [record.get('id') for record in odoo_data if record.get('id')]
        
        if not record_ids:
            return odoo_data
        
        # Get custom field values
        custom_field_data = FieldMergerService._get_custom_fields(
            model_name=model_name,
            record_ids=record_ids,
            field_names=custom_fields,
            database_name=database_name
        )
        
        # Merge custom fields into Odoo data
        merged_data = []
        for record in odoo_data:
            record_id = record.get('id')
            if record_id and record_id in custom_field_data:
                # Add custom fields to the record
                record.update(custom_field_data[record_id])
            merged_data.append(record)
        
        logger.info(f"Merged {len(custom_fields)} custom fields for {len(record_ids)} records in {model_name}")
        return merged_data
    
    @staticmethod
    def handle_missing_fields_in_domain(domain: List, model_name: str, 
                                      available_odoo_fields: List[str], database_name: str) -> Tuple[List, List]:
        """
        Handle missing fields in domain by splitting into valid and invalid conditions
        
        Args:
            domain: Domain conditions from client
            model_name: Name of the Odoo model
            available_odoo_fields: List of fields available in Odoo
            database_name: Name of the solution database
            
        Returns:
            Tuple of (valid_conditions, invalid_conditions)
        """
        if not domain:
            return [], []
        
        valid_conditions = []
        invalid_conditions = []
        
        for condition in domain:
            if len(condition) >= 3:
                field_name = condition[0]
                operator = condition[1]
                value = condition[2]
                
                if field_name in available_odoo_fields:
                    valid_conditions.append(condition)
                else:
                    # Check if it's a custom field
                    if FieldMergerService._is_custom_field(field_name, model_name, database_name):
                        # Convert to custom field query
                        custom_condition = FieldMergerService._convert_to_custom_field_condition(
                            field_name, operator, value, model_name, database_name
                        )
                        if custom_condition:
                            valid_conditions.append(custom_condition)
                    else:
                        invalid_conditions.append(condition)
                        logger.warning(f"Field '{field_name}' not found in model '{model_name}' and is not a custom field")
            else:
                invalid_conditions.append(condition)
                logger.warning(f"Invalid domain condition format: {condition}")
        
        return valid_conditions, invalid_conditions
    
    @staticmethod
    def _get_custom_fields(model_name: str, record_ids: List[int], 
                          field_names: List[str], database_name: str) -> Dict[int, Dict[str, Any]]:
        """
        Get custom field values for specific records
        
        Args:
            model_name: Name of the Odoo model
            record_ids: List of record IDs
            field_names: List of custom field names
            database_name: Name of the solution database
            
        Returns:
            Dict mapping record_id to custom field values
        """
        try:
            from ..models import CustomField
            
            # Get custom field values from Django
            custom_fields = CustomField.objects.filter(
                model_name=model_name,
                record_id__in=record_ids,
                field_name__in=field_names,
                database_name=database_name
            )
            
            # Group by record_id
            custom_field_data = {}
            for custom_field in custom_fields:
                record_id = custom_field.record_id
                if record_id not in custom_field_data:
                    custom_field_data[record_id] = {}
                
                custom_field_data[record_id][custom_field.field_name] = custom_field.field_value
            
            return custom_field_data
            
        except Exception as e:
            logger.error(f"Error getting custom fields: {str(e)}")
            return {}
    
    @staticmethod
    def _is_custom_field(field_name: str, model_name: str, database_name: str) -> bool:
        """
        Check if a field is a custom field
        
        Args:
            field_name: Name of the field
            model_name: Name of the Odoo model
            database_name: Name of the solution database
            
        Returns:
            bool: True if field is a custom field
        """
        try:
            from ..models import CustomField
            
            return CustomField.objects.filter(
                model_name=model_name,
                field_name=field_name,
                database_name=database_name
            ).exists()
            
        except Exception as e:
            logger.error(f"Error checking if field is custom: {str(e)}")
            return False
    
    @staticmethod
    def _convert_to_custom_field_condition(field_name: str, operator: str, value: Any, 
                                         model_name: str, database_name: str) -> List:
        """
        Convert Odoo domain condition to custom field condition
        
        Args:
            field_name: Name of the custom field
            operator: Odoo operator
            value: Value to compare against
            model_name: Name of the Odoo model
            database_name: Name of the solution database
            
        Returns:
            List: Custom field condition
        """
        # Map Odoo operators to Django operators
        operator_mapping = {
            '=': 'exact',
            '!=': 'exact',
            '>': 'gt',
            '>=': 'gte',
            '<': 'lt',
            '<=': 'lte',
            'in': 'in',
            'not in': 'in',
            'like': 'icontains',
            'ilike': 'icontains',
            'not like': 'icontains',
            'not ilike': 'icontains'
        }
        
        django_operator = operator_mapping.get(operator, 'exact')
        
        # Create custom field condition
        if operator in ['!=', 'not in', 'not like', 'not ilike']:
            # Handle negation
            return ['custom_field', field_name, django_operator, value, 'negated']
        else:
            return ['custom_field', field_name, django_operator, value]
    
    @staticmethod
    def create_custom_field(model_name: str, record_id: int, field_name: str, 
                           field_value: Any, database_name: str) -> Dict[str, Any]:
        """
        Create a custom field value
        
        Args:
            model_name: Name of the Odoo model
            record_id: ID of the record
            field_name: Name of the custom field
            field_value: Value of the custom field
            database_name: Name of the solution database
            
        Returns:
            Dict: Result of custom field creation
        """
        try:
            from ..models import CustomField
            
            # Check if custom field already exists
            existing_field, created = CustomField.objects.get_or_create(
                model_name=model_name,
                record_id=record_id,
                field_name=field_name,
                database_name=database_name,
                defaults={'field_value': field_value}
            )
            
            if not created:
                # Update existing field
                existing_field.field_value = field_value
                existing_field.save()
            
            return {
                'success': True,
                'custom_field_id': existing_field.id,
                'created': created,
                'message': f'Custom field {field_name} {"created" if created else "updated"} successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating custom field: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def update_custom_field(custom_field_id: int, field_value: Any) -> Dict[str, Any]:
        """
        Update a custom field value
        
        Args:
            custom_field_id: ID of the custom field
            field_value: New value for the custom field
            
        Returns:
            Dict: Result of custom field update
        """
        try:
            from ..models import CustomField
            
            try:
                custom_field = CustomField.objects.get(id=custom_field_id)
            except CustomField.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Custom field not found'
                }
            
            # Update field value
            custom_field.field_value = field_value
            custom_field.save()
            
            return {
                'success': True,
                'custom_field_id': custom_field.id,
                'message': f'Custom field {custom_field.field_name} updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating custom field: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def delete_custom_field(custom_field_id: int) -> Dict[str, Any]:
        """
        Delete a custom field
        
        Args:
            custom_field_id: ID of the custom field
            
        Returns:
            Dict: Result of custom field deletion
        """
        try:
            from ..models import CustomField
            
            try:
                custom_field = CustomField.objects.get(id=custom_field_id)
            except CustomField.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Custom field not found'
                }
            
            field_name = custom_field.field_name
            custom_field.delete()
            
            return {
                'success': True,
                'message': f'Custom field {field_name} deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting custom field: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_custom_field_schema(model_name: str, database_name: str) -> Dict[str, Any]:
        """
        Get custom field schema for a model
        
        Args:
            model_name: Name of the Odoo model
            database_name: Name of the solution database
            
        Returns:
            Dict: Custom field schema
        """
        try:
            from ..models import CustomField
            
            # Get all custom fields for the model
            custom_fields = CustomField.objects.filter(
                model_name=model_name,
                database_name=database_name
            ).values('field_name', 'field_type').distinct()
            
            # Build schema
            schema = {
                'model_name': model_name,
                'database_name': database_name,
                'custom_fields': []
            }
            
            for field in custom_fields:
                schema['custom_fields'].append({
                    'name': field['field_name'],
                    'type': field['field_type'] or 'text'
                })
            
            return {
                'success': True,
                'schema': schema
            }
            
        except Exception as e:
            logger.error(f"Error getting custom field schema: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def bulk_update_custom_fields(updates: List[Dict]) -> Dict[str, Any]:
        """
        Bulk update custom fields
        
        Args:
            updates: List of update dictionaries with keys: model_name, record_id, field_name, field_value, database_name
            
        Returns:
            Dict: Result of bulk update
        """
        try:
            results = []
            
            for update in updates:
                model_name = update.get('model_name')
                record_id = update.get('record_id')
                field_name = update.get('field_name')
                field_value = update.get('field_value')
                database_name = update.get('database_name')
                
                if not all([model_name, record_id, field_name, database_name]):
                    results.append({
                        'update': update,
                        'success': False,
                        'error': 'Missing required parameters'
                    })
                    continue
                
                # Create or update custom field
                result = FieldMergerService.create_custom_field(
                    model_name, record_id, field_name, field_value, database_name
                )
                
                results.append({
                    'update': update,
                    'success': result['success'],
                    'message': result.get('message', ''),
                    'error': result.get('error', '')
                })
            
            return {
                'success': True,
                'bulk_update_complete': True,
                'results': results,
                'total_updates': len(updates),
                'successful_updates': len([r for r in results if r['success']])
            }
            
        except Exception as e:
            logger.error(f"Error in bulk custom field update: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
