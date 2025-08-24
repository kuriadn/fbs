"""
FBS DMS FBS Integration Tests

Tests for DMS integration with FBS app for Odoo communication.
"""

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError

from fbs_dms.models import DocumentType, DocumentCategory, Document
from fbs_dms.services.document_service import DocumentService


class FBSIntegrationTestCase(TestCase):
    """Test FBS integration for Odoo communication"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.doc_type = DocumentType.objects.create(
            name='Invoice',
            code='INV',
            requires_approval=False,
            max_file_size=10
        )
        
        self.category = DocumentCategory.objects.create(
            name='Financial',
            sequence=1
        )
        
        self.dms_service = DocumentService('company_123')
    
    @patch('fbs_dms.services.document_service.DocumentService._is_fbs_available')
    @patch('fbs_dms.services.document_service.DocumentService._get_fbs_interface')
    def test_document_creation_with_fbs_available(self, mock_get_fbs, mock_fbs_available):
        """Test document creation when FBS app is available"""
        # Mock FBS availability
        mock_fbs_available.return_value = True
        
        # Mock FBS interface
        mock_fbs_interface = MagicMock()
        mock_fbs_interface.odoo.create_record.return_value = {'id': 123}
        mock_get_fbs.return_value = mock_fbs_interface
        
        # Create document
        document_data = {
            'name': 'INV-001',
            'title': 'Test Invoice',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test invoice',
            'confidentiality_level': 'internal'
        }
        
        document = self.dms_service.create_document(document_data, self.user)
        
        # Verify document was created
        self.assertEqual(document.name, 'INV-001')
        self.assertEqual(document.title, 'Test Invoice')
        
        # Verify FBS integration was called
        mock_fbs_interface.odoo.create_record.assert_called_once()
        call_args = mock_fbs_interface.odoo.create_record.call_args
        self.assertEqual(call_args[0][0], 'fayvad.document')
        
        # Verify data mapping
        odoo_data = call_args[0][1]
        self.assertEqual(odoo_data['name'], 'INV-001')
        self.assertEqual(odoo_data['title'], 'Test Invoice')
        self.assertEqual(odoo_data['company_id'], 'company_123')
    
    @patch('fbs_dms.services.document_service.DocumentService._is_fbs_available')
    def test_document_creation_without_fbs(self, mock_fbs_available):
        """Test document creation when FBS app is not available"""
        # Mock FBS unavailability
        mock_fbs_available.return_value = False
        
        # Create document
        document_data = {
            'name': 'INV-002',
            'title': 'Test Invoice 2',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test invoice without FBS',
            'confidentiality_level': 'internal'
        }
        
        # Should still work without FBS
        document = self.dms_service.create_document(document_data, self.user)
        
        # Verify document was created
        self.assertEqual(document.name, 'INV-002')
        self.assertEqual(document.title, 'Test Invoice 2')
    
    @patch('fbs_dms.services.document_service.DocumentService._is_fbs_available')
    @patch('fbs_dms.services.document_service.DocumentService._get_fbs_interface')
    def test_document_update_with_fbs(self, mock_get_fbs, mock_fbs_available):
        """Test document update with FBS integration"""
        # Mock FBS availability
        mock_fbs_available.return_value = True
        
        # Mock FBS interface
        mock_fbs_interface = MagicMock()
        mock_get_fbs.return_value = mock_fbs_interface
        
        # Create document first
        document_data = {
            'name': 'INV-003',
            'title': 'Test Invoice 3',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test invoice for update',
            'confidentiality_level': 'internal'
        }
        
        document = self.dms_service.create_document(document_data, self.user)
        
        # Update document
        update_data = {
            'title': 'Updated Invoice Title',
            'description': 'Updated description'
        }
        
        updated_document = self.dms_service.update_document(
            document.id, update_data, self.user
        )
        
        # Verify update
        self.assertEqual(updated_document.title, 'Updated Invoice Title')
        self.assertEqual(updated_document.description, 'Updated description')
        
        # Verify FBS update was called
        mock_fbs_interface.odoo.update_record.assert_called_once()
        call_args = mock_fbs_interface.odoo.update_record.call_args
        self.assertEqual(call_args[0][0], 'fayvad.document')
        self.assertEqual(call_args[0][1], document.id)
    
    @patch('fbs_dms.services.document_service.DocumentService._is_fbs_available')
    @patch('fbs_dms.services.document_service.DocumentService._get_fbs_interface')
    def test_document_deletion_with_fbs(self, mock_get_fbs, mock_fbs_available):
        """Test document deletion with FBS integration"""
        # Mock FBS availability
        mock_fbs_available.return_value = True
        
        # Mock FBS interface
        mock_fbs_interface = MagicMock()
        mock_get_fbs.return_value = mock_fbs_interface
        
        # Create document first
        document_data = {
            'name': 'INV-004',
            'title': 'Test Invoice 4',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test invoice for deletion',
            'confidentiality_level': 'internal'
        }
        
        document = self.dms_service.create_document(document_data, self.user)
        
        # Delete document
        result = self.dms_service.delete_document(document.id, self.user)
        
        # Verify deletion
        self.assertTrue(result)
        
        # Verify FBS deletion was called
        mock_fbs_interface.odoo.delete_record.assert_called_once()
        call_args = mock_fbs_interface.odoo.delete_record.call_args
        self.assertEqual(call_args[0][0], 'fayvad.document')
        self.assertEqual(call_args[0][1], document.id)
    
    def test_odoo_data_mapping(self):
        """Test Django model to Odoo data mapping"""
        # Create document
        document_data = {
            'name': 'INV-005',
            'title': 'Test Invoice 5',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test invoice for mapping',
            'confidentiality_level': 'confidential'
        }
        
        document = self.dms_service.create_document(document_data, self.user)
        
        # Test data mapping
        odoo_data = self.dms_service._map_to_odoo_format(document)
        
        # Verify mapping
        self.assertEqual(odoo_data['name'], 'INV-005')
        self.assertEqual(odoo_data['title'], 'Test Invoice 5')
        self.assertEqual(odoo_data['document_type_id'], self.doc_type.id)
        self.assertEqual(odoo_data['document_category_id'], self.category.id)
        self.assertEqual(odoo_data['state'], 'draft')
        self.assertEqual(odoo_data['created_by'], self.user.id)
        self.assertEqual(odoo_data['company_id'], 'company_123')
        self.assertEqual(odoo_data['confidentiality_level'], 'confidential')
        self.assertEqual(odoo_data['description'], 'Test invoice for mapping')
        
        # Verify tag_ids format (Odoo many2many format)
        # The method returns a list containing the tuple, so we check the first element
        self.assertEqual(odoo_data['tag_ids'], [(6, 0, [])])
        
        # Verify attachment_id (no attachment in this test)
        self.assertEqual(odoo_data['attachment_id'], False)
        
        # Verify expiry_date (no expiry in this test)
        self.assertEqual(odoo_data['expiry_date'], False)
    
    @patch('fbs_dms.services.document_service.DocumentService._is_fbs_available')
    def test_fbs_availability_detection(self, mock_fbs_available):
        """Test FBS availability detection"""
        # Test when FBS is available
        mock_fbs_available.return_value = True
        self.assertTrue(self.dms_service._is_fbs_available())
        
        # Test when FBS is not available
        mock_fbs_available.return_value = False
        self.assertFalse(self.dms_service._is_fbs_available())
    
    @patch('fbs_dms.services.document_service.DocumentService._is_fbs_available')
    @patch('fbs_dms.services.document_service.DocumentService._get_fbs_interface')
    def test_fbs_interface_error_handling(self, mock_get_fbs, mock_fbs_available):
        """Test error handling when FBS interface fails"""
        # Mock FBS availability
        mock_fbs_available.return_value = True
        
        # Mock FBS interface failure
        mock_get_fbs.return_value = None
        
        # Create document - should still work despite FBS failure
        document_data = {
            'name': 'INV-006',
            'title': 'Test Invoice 6',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test invoice with FBS failure',
            'confidentiality_level': 'internal'
        }
        
        document = self.dms_service.create_document(document_data, self.user)
        
        # Verify document was created
        self.assertEqual(document.name, 'INV-006')
        self.assertEqual(document.title, 'Test Invoice 6')
