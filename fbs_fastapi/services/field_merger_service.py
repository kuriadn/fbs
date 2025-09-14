"""
FBS FastAPI Field Merger Service

PRESERVED from Django field_merger_service.py
Service for merging data from Odoo models with custom fields stored in FastAPI.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FieldMergerService:
    """Service for merging Odoo fields with custom FastAPI fields - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        self.solution_name = solution_name

    async def split_fields_by_source(self, model_name: str, requested_fields: List[str],
                                   available_odoo_fields: List[str], database_name: str) -> Tuple[List[str], List[str]]:
        """
        Split requested fields into Odoo fields and custom fields

        PRESERVED from Django field_merger_service.py
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
                logger.info(f"Field '{field}' not found in Odoo model '{model_name}', will be retrieved from custom fields")

        return odoo_fields, custom_fields

    async def set_custom_field(self, model_name: str, record_id: int, field_name: str,
                             field_value: Any, field_type: str = 'char',
                             database_name: Optional[str] = None) -> Dict[str, Any]:
        """Set custom field value - PRESERVED from Django"""
        try:
            from ..models.models import CustomField
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                # Check if field already exists
                existing_field = await db.query(CustomField).filter(
                    CustomField.model_name == model_name,
                    CustomField.record_id == record_id,
                    CustomField.field_name == field_name
                ).first()

                if existing_field:
                    # Update existing field
                    existing_field.field_value = field_value
                    existing_field.field_type = field_type
                    existing_field.updated_at = datetime.now()
                    await db.commit()
                    await db.refresh(existing_field)

                    return {
                        'success': True,
                        'action': 'updated',
                        'field_id': str(existing_field.id),
                        'field_name': field_name,
                        'field_value': field_value
                    }
                else:
                    # Create new field
                    custom_field = CustomField(
                        model_name=model_name,
                        record_id=record_id,
                        field_name=field_name,
                        field_value=field_value,
                        field_type=field_type
                    )

                    db.add(custom_field)
                    await db.commit()
                    await db.refresh(custom_field)

                    return {
                        'success': True,
                        'action': 'created',
                        'field_id': str(custom_field.id),
                        'field_name': field_name,
                        'field_value': field_value
                    }

        except Exception as e:
            logger.error(f"Error setting custom field: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def get_custom_field(self, model_name: str, record_id: int, field_name: str,
                             database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get custom field value - PRESERVED from Django"""
        try:
            from ..models.models import CustomField
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                custom_field = await db.query(CustomField).filter(
                    CustomField.model_name == model_name,
                    CustomField.record_id == record_id,
                    CustomField.field_name == field_name
                ).first()

                if custom_field:
                    return {
                        'success': True,
                        'found': True,
                        'field_name': custom_field.field_name,
                        'field_value': custom_field.field_value,
                        'field_type': custom_field.field_type,
                        'created_at': custom_field.created_at.isoformat(),
                        'updated_at': custom_field.updated_at.isoformat()
                    }
                else:
                    return {
                        'success': True,
                        'found': False,
                        'field_name': field_name,
                        'message': 'Custom field not found'
                    }

        except Exception as e:
            logger.error(f"Error getting custom field: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def get_custom_fields(self, model_name: str, record_id: int,
                              database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get all custom fields for a record - PRESERVED from Django"""
        try:
            from ..models.models import CustomField
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                custom_fields = await db.query(CustomField).filter(
                    CustomField.model_name == model_name,
                    CustomField.record_id == record_id
                ).all()

                fields_data = []
                for field in custom_fields:
                    fields_data.append({
                        'field_name': field.field_name,
                        'field_value': field.field_value,
                        'field_type': field.field_type,
                        'created_at': field.created_at.isoformat(),
                        'updated_at': field.updated_at.isoformat()
                    })

                return {
                    'success': True,
                    'model_name': model_name,
                    'record_id': record_id,
                    'custom_fields': fields_data,
                    'count': len(fields_data)
                }

        except Exception as e:
            logger.error(f"Error getting custom fields: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def delete_custom_field(self, model_name: str, record_id: int, field_name: str,
                                database_name: Optional[str] = None) -> Dict[str, Any]:
        """Delete custom field - PRESERVED from Django"""
        try:
            from ..models.models import CustomField
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                custom_field = await db.query(CustomField).filter(
                    CustomField.model_name == model_name,
                    CustomField.record_id == record_id,
                    CustomField.field_name == field_name
                ).first()

                if custom_field:
                    await db.delete(custom_field)
                    await db.commit()

                    return {
                        'success': True,
                        'deleted': True,
                        'field_name': field_name,
                        'message': 'Custom field deleted successfully'
                    }
                else:
                    return {
                        'success': True,
                        'deleted': False,
                        'field_name': field_name,
                        'message': 'Custom field not found'
                    }

        except Exception as e:
            logger.error(f"Error deleting custom field: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def merge_odoo_with_custom(self, model_name: str, record_id: int,
                                   odoo_fields: Optional[List[str]] = None,
                                   database_name: Optional[str] = None) -> Dict[str, Any]:
        """Merge Odoo data with custom fields - PRESERVED from Django"""
        try:
            # Get custom fields
            custom_result = await self.get_custom_fields(model_name, record_id, database_name)

            if not custom_result['success']:
                return custom_result

            # Get Odoo data if odoo_fields specified
            odoo_data = {}
            if odoo_fields:
                from .odoo_service import OdooService
                odoo_service = OdooService(self.solution_name)

                # Try to get Odoo record
                odoo_result = await odoo_service.get_records(model_name, [('id', '=', record_id)], odoo_fields)
                if odoo_result['success'] and odoo_result['data']:
                    odoo_data = odoo_result['data'][0] if odoo_result['data'] else {}

            # Merge the data
            merged_data = dict(odoo_data)  # Start with Odoo data

            # Add custom fields (these take precedence)
            for custom_field in custom_result['custom_fields']:
                merged_data[custom_field['field_name']] = custom_field['field_value']

            return {
                'success': True,
                'model_name': model_name,
                'record_id': record_id,
                'merged_data': merged_data,
                'odoo_data': odoo_data,
                'custom_fields_count': len(custom_result['custom_fields']),
                'message': 'Data merged successfully'
            }

        except Exception as e:
            logger.error(f"Error merging data: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def get_virtual_model_schema(self, model_name: str,
                                     database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get virtual model schema including custom fields - PRESERVED from Django"""
        try:
            from ..models.models import CustomField
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                # Get all custom fields for this model
                custom_fields = await db.query(CustomField).filter(
                    CustomField.model_name == model_name
                ).distinct(CustomField.field_name).all()

                # Build schema
                schema = {
                    'model_name': model_name,
                    'custom_fields': []
                }

                field_definitions = {}
                for field in custom_fields:
                    if field.field_name not in field_definitions:
                        field_definitions[field.field_name] = {
                            'field_name': field.field_name,
                            'field_type': field.field_type,
                            'usage_count': 0
                        }

                    field_definitions[field.field_name]['usage_count'] += 1

                schema['custom_fields'] = list(field_definitions.values())

                return {
                    'success': True,
                    'schema': schema,
                    'custom_fields_count': len(field_definitions),
                    'message': f'Schema retrieved for model {model_name}'
                }

        except Exception as e:
            logger.error(f"Error getting virtual model schema: {str(e)}")
            return {'success': False, 'error': str(e)}
