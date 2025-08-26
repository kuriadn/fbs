"""
FBS DMS Odoo-Driven Service

This service implements the Odoo + FBS Virtual Fields + Django UI architecture.
Documents are stored in Odoo (ir.attachment) with DMS-specific fields as FBS virtual fields.
"""

import logging
from typing import Dict, Any, Optional, List
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

logger = logging.getLogger('fbs_dms')


class OdooDMSService:
    """Odoo-driven DMS service using FBS virtual fields for extensions"""
    
    def __init__(self, company_id: str, fbs_interface=None):
        self.company_id = company_id
        self.fbs = fbs_interface
        self.odoo_dms = fbs_interface.odoo if fbs_interface else None
        self.virtual_fields = fbs_interface.fields if fbs_interface else None
        
        if not self.odoo_dms:
            logger.warning("Odoo integration not available - DMS will work in limited mode")
    
    def create_document(self, document_data: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Create document with Odoo storage + FBS virtual fields"""
        if not self.odoo_dms:
            return {
                'success': False,
                'error': 'Odoo integration required for document creation'
            }
        
        try:
            # 1. Prepare base document data for Odoo (ir.attachment)
            odoo_data = {
                'name': document_data['name'],
                'description': document_data.get('description', ''),
                'mimetype': document_data.get('mime_type', 'text/plain'),
                'res_model': 'fbs_dms.document',
                'res_id': 0,  # Will be set after creation
                'company_id': self.company_id,
                'create_uid': user.id,
                'write_uid': user.id,
                'create_date': timezone.now().isoformat(),
                'write_date': timezone.now().isoformat()
            }
            
            # Add file data if present
            if document_data.get('file_data'):
                odoo_data['datas'] = document_data['file_data']
            
            # 2. Create base document in Odoo
            odoo_result = self.odoo_dms.create_record('ir.attachment', odoo_data)
            
            if not odoo_result.get('success'):
                raise Exception(f"Odoo creation failed: {odoo_result.get('error')}")
            
            odoo_id = odoo_result['data']['id']
            
            # 3. Add FBS virtual fields for DMS-specific data
            if self.virtual_fields:
                self._add_dms_virtual_fields(odoo_id, document_data)
            
            # 4. Update res_id to point to itself (for self-reference)
            self.odoo_dms.update_record('ir.attachment', odoo_id, {'res_id': odoo_id})
            
            return {
                'success': True,
                'odoo_id': odoo_id,
                'message': 'Document created successfully in Odoo with virtual fields'
            }
            
        except Exception as e:
            logger.error(f"Document creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_dms_virtual_fields(self, odoo_id: int, document_data: Dict[str, Any]):
        """Add DMS-specific virtual fields to the Odoo document"""
        try:
            # Document type (not in standard Odoo)
            if document_data.get('document_type'):
                self.virtual_fields.set_custom_field(
                    'ir.attachment', odoo_id, 'document_type', 
                    document_data['document_type'], 'char', self.company_id
                )
            
            # Document category (not in standard Odoo)
            if document_data.get('category'):
                self.virtual_fields.set_custom_field(
                    'ir.attachment', odoo_id, 'document_category', 
                    document_data['category'], 'char', self.company_id
                )
            
            # Confidentiality level (not in standard Odoo)
            self.virtual_fields.set_custom_field(
                'ir.attachment', odoo_id, 'confidentiality_level', 
                document_data.get('confidentiality_level', 'internal'), 'char', self.company_id
            )
            
            # Approval workflow status (not in standard Odoo)
            self.virtual_fields.set_custom_field(
                'ir.attachment', odoo_id, 'workflow_status', 
                'pending', 'char', self.company_id
            )
            
            # Expiry date (not in standard Odoo)
            if document_data.get('expiry_date'):
                self.virtual_fields.set_custom_field(
                    'ir.attachment', odoo_id, 'expiry_date', 
                    document_data['expiry_date'].isoformat(), 'date', self.company_id
                )
            
            # Document state (not in standard Odoo)
            self.virtual_fields.set_custom_field(
                'ir.attachment', odoo_id, 'document_state', 
                document_data.get('state', 'draft'), 'char', self.company_id
            )
            
            logger.info(f"Added DMS virtual fields to Odoo document {odoo_id}")
            
        except Exception as e:
            logger.error(f"Failed to add DMS virtual fields: {str(e)}")
            # Don't fail the main operation if virtual fields fail
    
    def get_document(self, odoo_id: int) -> Dict[str, Any]:
        """Get complete document data from Odoo + FBS virtual fields"""
        if not self.odoo_dms:
            return {
                'success': False,
                'error': 'Odoo integration required'
            }
        
        try:
            # 1. Get base Odoo data
            odoo_result = self.odoo_dms.get_record('ir.attachment', odoo_id)
            
            if not odoo_result.get('success'):
                return {
                    'success': False,
                    'error': f"Document not found: {odoo_result.get('error')}"
                }
            
            # 2. Get FBS virtual fields
            virtual_fields_data = {}
            if self.virtual_fields:
                virtual_result = self.virtual_fields.get_custom_fields(
                    'ir.attachment', odoo_id, self.company_id
                )
                
                if virtual_result.get('success'):
                    virtual_fields_data = virtual_result.get('data', {})
            
            # 3. Merge Odoo data with virtual fields
            complete_data = odoo_result['data']
            complete_data.update(virtual_fields_data)
            
            return {
                'success': True,
                'data': complete_data,
                'message': 'Document retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_document(self, odoo_id: int, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update document in Odoo + FBS virtual fields"""
        if not self.odoo_dms:
            return {
                'success': False,
                'error': 'Odoo integration required'
            }
        
        try:
            # 1. Update base Odoo data
            odoo_update_data = {}
            odoo_fields = ['name', 'description', 'mimetype']
            
            for field in odoo_fields:
                if field in document_data:
                    odoo_update_data[field] = document_data[field]
            
            if odoo_update_data:
                odoo_result = self.odoo_dms.update_record('ir.attachment', odoo_id, odoo_update_data)
                if not odoo_result.get('success'):
                    raise Exception(f"Odoo update failed: {odoo_result.get('error')}")
            
            # 2. Update FBS virtual fields
            if self.virtual_fields:
                self._update_dms_virtual_fields(odoo_id, document_data)
            
            return {
                'success': True,
                'odoo_id': odoo_id,
                'message': 'Document updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Document update failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_dms_virtual_fields(self, odoo_id: int, document_data: Dict[str, Any]):
        """Update DMS-specific virtual fields"""
        try:
            # Update document type
            if 'document_type' in document_data:
                self.virtual_fields.set_custom_field(
                    'ir.attachment', odoo_id, 'document_type', 
                    document_data['document_type'], 'char', self.company_id
                )
            
            # Update document category
            if 'category' in document_data:
                self.virtual_fields.set_custom_field(
                    'ir.attachment', odoo_id, 'document_category', 
                    document_data['category'], 'char', self.company_id
                )
            
            # Update confidentiality level
            if 'confidentiality_level' in document_data:
                self.virtual_fields.set_custom_field(
                    'ir.attachment', odoo_id, 'confidentiality_level', 
                    document_data['confidentiality_level'], 'char', self.company_id
                )
            
            # Update workflow status
            if 'workflow_status' in document_data:
                self.virtual_fields.set_custom_field(
                    'ir.attachment', odoo_id, 'workflow_status', 
                    document_data['workflow_status'], 'char', self.company_id
                )
            
            # Update document state
            if 'state' in document_data:
                self.virtual_fields.set_custom_field(
                    'ir.attachment', odoo_id, 'document_state', 
                    document_data['state'], 'char', self.company_id
                )
            
            logger.info(f"Updated DMS virtual fields for Odoo document {odoo_id}")
            
        except Exception as e:
            logger.error(f"Failed to update DMS virtual fields: {str(e)}")
    
    def delete_document(self, odoo_id: int) -> Dict[str, Any]:
        """Delete document from Odoo (virtual fields are automatically cleaned up)"""
        if not self.odoo_dms:
            return {
                'success': False,
                'error': 'Odoo integration required'
            }
        
        try:
            # Delete from Odoo (this will cascade to virtual fields)
            result = self.odoo_dms.delete_record('ir.attachment', odoo_id)
            
            if not result.get('success'):
                return {
                    'success': False,
                    'error': f"Deletion failed: {result.get('error')}"
                }
            
            return {
                'success': True,
                'message': 'Document deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Document deletion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_documents(self, filters: Dict[str, Any] = None, limit: int = 100) -> Dict[str, Any]:
        """Search documents using Odoo + FBS virtual fields"""
        if not self.odoo_dms:
            return {
                'success': False,
                'error': 'Odoo integration required'
            }
        
        try:
            # Build domain for Odoo search
            domain = self._build_search_domain(filters)
            
            # Search in Odoo
            search_result = self.odoo_dms.get_records('ir.attachment', domain, ['id', 'name', 'description'], limit)
            
            if not search_result.get('success'):
                return search_result
            
            # Get virtual fields for each document
            documents = []
            for doc in search_result['data']:
                doc_data = self.get_document(doc['id'])
                if doc_data.get('success'):
                    documents.append(doc_data['data'])
            
            return {
                'success': True,
                'data': documents,
                'count': len(documents),
                'message': f'Found {len(documents)} documents'
            }
            
        except Exception as e:
            logger.error(f"Document search failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_search_domain(self, filters: Dict[str, Any] = None) -> List:
        """Build Odoo domain from filters"""
        if not filters:
            return []
        
        domain = []
        
        # Map DMS filters to Odoo fields
        if 'name' in filters:
            domain.append(('name', 'ilike', filters['name']))
        
        if 'description' in filters:
            domain.append(('description', 'ilike', filters['description']))
        
        if 'mime_type' in filters:
            domain.append(('mimetype', '=', filters['mime_type']))
        
        # Add company filter
        domain.append(('company_id', '=', self.company_id))
        
        return domain
