"""
Test Odoo-Driven DMS Integration

Tests the integration between DMS and FBS virtual fields system.
"""

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import Mock, patch

from ..services.odoo_dms_service import OdooDMSService


class OdooDMSIntegrationTestCase(TestCase):
    """Test case for Odoo-driven DMS integration"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.company_id = 'test_company'
        
        # Mock FBS interface
        self.mock_fbs_interface = Mock()
        self.mock_odoo = Mock()
        self.mock_virtual_fields = Mock()
        
        # Set up mock responses
        self.mock_odoo.create_record.return_value = {
            'success': True,
            'data': {'id': 123}
        }
        self.mock_odoo.update_record.return_value = {
            'success': True,
            'data': {'id': 123}
        }
        self.mock_odoo.delete_record.return_value = {
            'success': True,
            'message': 'Deleted'
        }
        self.mock_odoo.get_record.return_value = {
            'success': True,
            'data': {
                'id': 123,
                'name': 'Test Document',
                'description': 'Test Description'
            }
        }
        
        self.mock_virtual_fields.set_custom_field.return_value = {
            'success': True,
            'message': 'Field set'
        }
        
        # Mock virtual fields get_custom_fields method
        self.mock_virtual_fields.get_custom_fields.return_value = {
            'success': True,
            'data': {
                'document_type': 'invoice',
                'category': 'financial',
                'confidentiality_level': 'internal',
                'workflow_status': 'pending',
                'document_state': 'draft'
            }
        }
        
        # Wire up the mocks
        self.mock_fbs_interface.odoo = self.mock_odoo
        self.mock_fbs_interface.fields = self.mock_virtual_fields
        
        # Create service with mocked interface
        self.odoo_dms_service = OdooDMSService(
            self.company_id, 
            self.mock_fbs_interface
        )
    
    def test_service_initialization(self):
        """Test that service initializes correctly"""
        self.assertEqual(self.odoo_dms_service.company_id, self.company_id)
        self.assertIsNotNone(self.odoo_dms_service.odoo_dms)
        self.assertIsNotNone(self.odoo_dms_service.virtual_fields)
    
    def test_create_document_success(self):
        """Test successful document creation with virtual fields"""
        document_data = {
            'name': 'Test Document',
            'description': 'Test Description',
            'mime_type': 'text/plain',
            'document_type': 'invoice',
            'category': 'financial',
            'confidentiality_level': 'internal',
            'state': 'draft'
        }
        
        result = self.odoo_dms_service.create_document(document_data, self.user)
        
        # Verify success
        self.assertTrue(result['success'])
        self.assertEqual(result['odoo_id'], 123)
        
        # Verify Odoo creation was called
        self.mock_odoo.create_record.assert_called_once()
        call_args = self.mock_odoo.create_record.call_args
        self.assertEqual(call_args[0][0], 'ir.attachment')  # model_name
        
        # Verify virtual fields were set
        self.assertEqual(self.mock_virtual_fields.set_custom_field.call_count, 5)
    
    def test_create_document_no_odoo_integration(self):
        """Test document creation without Odoo integration"""
        service = OdooDMSService(self.company_id, None)
        
        document_data = {'name': 'Test Document'}
        result = service.create_document(document_data, self.user)
        
        self.assertFalse(result['success'])
        self.assertIn('Odoo integration required', result['error'])
    
    def test_get_document_success(self):
        """Test successful document retrieval with virtual fields"""
        result = self.odoo_dms_service.get_document(123)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['id'], 123)
        self.assertEqual(result['data']['name'], 'Test Document')
    
    def test_update_document_success(self):
        """Test successful document update"""
        update_data = {
            'name': 'Updated Document',
            'document_type': 'receipt',
            'state': 'approved'
        }
        
        result = self.odoo_dms_service.update_document(123, update_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['odoo_id'], 123)
        
        # Verify Odoo update was called
        self.mock_odoo.update_record.assert_called_once()
        
        # Verify virtual fields were updated
        self.assertEqual(self.mock_virtual_fields.set_custom_field.call_count, 2)
    
    def test_delete_document_success(self):
        """Test successful document deletion"""
        result = self.odoo_dms_service.delete_document(123)
        
        self.assertTrue(result['success'])
        self.mock_odoo.delete_record.assert_called_once_with('ir.attachment', 123)
    
    def test_search_documents_success(self):
        """Test successful document search"""
        # Mock search results
        self.mock_odoo.get_records.return_value = {
            'success': True,
            'data': [
                {'id': 123, 'name': 'Doc 1'},
                {'id': 124, 'name': 'Doc 2'}
            ]
        }
        
        filters = {'name': 'Doc'}
        result = self.odoo_dms_service.search_documents(filters)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        self.assertEqual(len(result['data']), 2)
    
    def test_build_search_domain(self):
        """Test search domain building"""
        filters = {
            'name': 'Test',
            'description': 'Description',
            'mime_type': 'text/plain'
        }
        
        domain = self.odoo_dms_service._build_search_domain(filters)
        
        # Should have 4 conditions (3 filters + company_id)
        self.assertEqual(len(domain), 4)
        
        # Check company filter is always added
        company_filter = domain[-1]
        self.assertEqual(company_filter[0], 'company_id')
        self.assertEqual(company_filter[1], '=')
        self.assertEqual(company_filter[2], self.company_id)
    
    def test_virtual_fields_error_handling(self):
        """Test that virtual field errors don't fail main operations"""
        # Make virtual fields fail
        self.mock_virtual_fields.set_custom_field.return_value = {
            'success': False,
            'error': 'Virtual field error'
        }
        
        document_data = {
            'name': 'Test Document',
            'document_type': 'invoice'
        }
        
        # Should still succeed even if virtual fields fail
        result = self.odoo_dms_service.create_document(document_data, self.user)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['odoo_id'], 123)
