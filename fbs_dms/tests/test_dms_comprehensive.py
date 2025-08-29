"""
Comprehensive DMS Test Suite

Tests all DMS functionality including edge cases, error handling, and integration scenarios.
"""

import os
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from datetime import timedelta

from ..models import (
    DocumentType, DocumentCategory, DocumentTag, Document, 
    FileAttachment, DocumentWorkflow, DocumentApproval
)
from ..services.document_service import DocumentService
from ..services.workflow_service import WorkflowService
from ..services.search_service import SearchService
from ..services.file_service import FileService


class DMSComprehensiveTestCase(TestCase):
    """Comprehensive test case for all DMS functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test company
        self.company_id = 'test_company'
        
        # Create document type
        self.doc_type = DMSDocumentType.objects.create(
            name='Test Document',
            code='TEST_DOC',
            description='Test document type for comprehensive testing',
            allowed_extensions='pdf,doc,docx',
            max_file_size=10,  # 10MB
            requires_approval=True,
            is_active=True
        )
        
        # Create document category
        self.category = DMSDocumentCategory.objects.create(
            name='Test Category',
            description='Test category for comprehensive testing',
            sequence=1,
            is_active=True
        )
        
        # Create document tag
        self.tag = DMSDocumentTag.objects.create(
            name='Test Tag',
            description='Test tag for comprehensive testing',
            color=1,
            is_active=True
        )
        
        # Create test file
        self.test_file = SimpleUploadedFile(
            'test.pdf',
            b'Test PDF content',
            content_type='application/pdf'
        )
        
        # Initialize services
        self.doc_service = DocumentService(self.company_id)
        self.workflow_service = WorkflowService(self.company_id)
        self.search_service = SearchService(self.company_id)
        self.file_service = FileService(self.company_id)
    
    def test_service_instantiation(self):
        """Test that all DMS services can be instantiated"""
        self.assertIsInstance(self.doc_service, DocumentService)
        self.assertIsInstance(self.workflow_service, WorkflowService)
        self.assertIsInstance(self.search_service, SearchService)
        self.assertIsInstance(self.file_service, FileService)
        
        # Verify service properties
        self.assertEqual(self.doc_service.company_id, self.company_id)
        self.assertEqual(self.workflow_service.company_id, self.company_id)
        self.assertEqual(self.search_service.company_id, self.company_id)
        self.assertEqual(self.file_service.company_id, self.company_id)
    
    def test_document_creation_comprehensive(self):
        """Test comprehensive document creation scenarios"""
        # Test basic document creation
        doc_data = {
            'name': 'Test Document',
            'title': 'Test Document Title',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test document description',
            'confidentiality_level': 'internal',
            'metadata': {'key': 'value'}
        }
        
        document = self.doc_service.create_document(doc_data, self.user)
        self.assertIsInstance(document, Document)
        self.assertEqual(document.name, 'Test Document')
        self.assertEqual(document.company_id, self.company_id)
        self.assertEqual(document.created_by, self.user)
        
        # Test document with file attachment
        doc_data_with_file = {
            'name': 'Test Document with File',
            'title': 'Test Document with File Title',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test document with file',
            'confidentiality_level': 'internal'
        }
        
        document_with_file = self.doc_service.create_document(
            doc_data_with_file, self.user, self.test_file
        )
        self.assertIsInstance(document_with_file, Document)
        self.assertIsNotNone(document_with_file.attachment)
        # Test that the attachment has a description field (even if empty)
        self.assertTrue(hasattr(document_with_file.attachment, 'description'))
        
        # Test document with tags
        doc_data_with_tags = {
            'name': 'Test Document with Tags',
            'title': 'Test Document with Tags Title',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test document with tags',
            'confidentiality_level': 'internal',
            'tag_ids': [self.tag.id]
        }
        
        document_with_tags = self.doc_service.create_document(doc_data_with_tags, self.user)
        self.assertIsInstance(document_with_tags, Document)
        self.assertIn(self.tag, document_with_tags.tags.all())
    
    def test_document_validation_edge_cases(self):
        """Test document validation edge cases"""
        # Test invalid document type
        with self.assertRaises(ValidationError):
            self.doc_service.create_document({
                'name': 'Invalid Doc',
                'title': 'Invalid Doc Title',
                'document_type_id': 99999,  # Non-existent ID
                'category_id': self.category.id
            }, self.user)
        
        # Test invalid category
        with self.assertRaises(ValidationError):
            self.doc_service.create_document({
                'name': 'Invalid Doc',
                'title': 'Invalid Doc Title',
                'document_type_id': self.doc_type.id,
                'category_id': 99999  # Non-existent ID
            }, self.user)
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            self.doc_service.create_document({
                'name': '',  # Empty name
                'title': 'Test Title',
                'document_type_id': self.doc_type.id,
                'category_id': self.category.id
            }, self.user)
    
    def test_document_workflow_comprehensive(self):
        """Test comprehensive document workflow scenarios"""
        # Create a document that requires approval
        doc_data = {
            'name': 'Workflow Test Document',
            'title': 'Workflow Test Document Title',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test document for workflow',
            'confidentiality_level': 'internal'
        }
        
        document = self.doc_service.create_document(doc_data, self.user)
        
        # Verify workflow was started
        self.assertEqual(document.state, 'pending')
        self.assertTrue(hasattr(document, 'workflow'))
        self.assertIsNotNone(document.workflow)
        
        # Test workflow status
        workflow_status = self.workflow_service.get_workflow_status(document.id)
        self.assertIsNotNone(workflow_status)
        self.assertEqual(workflow_status['status'], 'active')
        
        # Test pending approvals
        pending_approvals = self.workflow_service.get_pending_approvals(self.user)
        self.assertIsInstance(pending_approvals, QuerySet)
        
        # Test approval step
        if pending_approvals.exists():
            approval = pending_approvals.first()
            approved_step = self.workflow_service.approve_step(
                approval.id, self.user, 'Approved for testing'
            )
            self.assertIsInstance(approved_step, DocumentApproval)
            self.assertEqual(approved_step.status, 'approved')
    
    def test_document_search_comprehensive(self):
        """Test comprehensive document search functionality"""
        # Create multiple test documents
        for i in range(5):
            doc_data = {
                'name': f'Search Test Document {i}',
                'title': f'Search Test Document {i} Title',
                'document_type_id': self.doc_type.id,
                'category_id': self.category.id,
                'description': f'Test document {i} for search testing',
                'confidentiality_level': 'internal'
            }
            self.doc_service.create_document(doc_data, self.user)
        
        # Test full text search
        search_results = self.search_service.full_text_search('Search Test')
        self.assertIsInstance(search_results, list)
        self.assertGreater(len(search_results), 0)
        
        # Test metadata search
        metadata_results = self.search_service.search_by_metadata({
            'confidentiality_level': 'internal'
        })
        self.assertIsInstance(metadata_results, list)
        self.assertGreater(len(metadata_results), 0)
        
        # Test workflow status search
        workflow_results = self.search_service.search_by_workflow_status('pending')
        self.assertIsInstance(workflow_results, list)
        
        # Test advanced search
        advanced_results = self.search_service.advanced_search({
            'query': 'Search Test',
            'filters': {
                'state': 'pending',
                'confidentiality_level': 'internal'
            }
        })
        self.assertIsInstance(advanced_results, list)
        
        # Test search suggestions
        suggestions = self.search_service.get_search_suggestions('Search')
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Test search statistics
        stats = self.search_service.get_search_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_documents', stats)
    
    def test_file_management_comprehensive(self):
        """Test comprehensive file management functionality"""
        # Test file upload
        uploaded_file = self.file_service.upload_file(
            self.test_file, self.user, 'test_upload.pdf'
        )
        self.assertIsInstance(uploaded_file, FileAttachment)
        self.assertEqual(uploaded_file.original_filename, 'test_upload.pdf')
        
        # Test file validation
        is_valid = self.file_service.validate_file_for_document_type(
            self.test_file, self.doc_type
        )
        self.assertTrue(is_valid)
        
        # Test file info retrieval
        file_info = self.file_service.get_file_info(uploaded_file.id)
        self.assertIsInstance(file_info, dict)
        self.assertIn('filename', file_info)
        self.assertIn('file_size', file_info)
        self.assertIn('mime_type', file_info)
        
        # Test file download
        downloaded_file = self.file_service.download_file(uploaded_file.id, self.user)
        self.assertIsInstance(downloaded_file, FileAttachment)
        self.assertEqual(downloaded_file.id, uploaded_file.id)
        
        # Test file deletion
        delete_result = self.file_service.delete_file(uploaded_file.id, self.user)
        self.assertTrue(delete_result)
    
    def test_document_operations_comprehensive(self):
        """Test comprehensive document operations"""
        # Create a test document
        doc_data = {
            'name': 'Operations Test Document',
            'title': 'Operations Test Document Title',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test document for operations',
            'confidentiality_level': 'internal'
        }
        
        document = self.doc_service.create_document(doc_data, self.user)
        
        # Test document update
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        
        updated_doc = self.doc_service.update_document(
            document.id, update_data, self.user
        )
        self.assertEqual(updated_doc.title, 'Updated Title')
        self.assertEqual(updated_doc.description, 'Updated description')
        
        # Test document approval
        approved_doc = self.doc_service.approve_document(
            document.id, self.user, 'Approved for testing'
        )
        self.assertEqual(approved_doc.state, 'approved')
        self.assertEqual(approved_doc.approved_by, self.user)
        
        # Test document rejection
        rejected_doc = self.doc_service.reject_document(
            document.id, self.user, 'Rejected for testing'
        )
        self.assertEqual(rejected_doc.state, 'rejected')
        
        # Test document deletion
        delete_result = self.doc_service.delete_document(document.id, self.user)
        self.assertTrue(delete_result)
    
    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling"""
        # Test non-existent document operations
        with self.assertRaises(ValidationError):
            self.doc_service.get_document(99999)
        
        with self.assertRaises(ValidationError):
            self.doc_service.update_document(99999, {'title': 'Test'}, self.user)
        
        with self.assertRaises(ValidationError):
            self.doc_service.delete_document(99999, self.user)
        
        # Test invalid workflow operations
        with self.assertRaises(ValidationError):
            self.workflow_service.approve_step(99999, self.user, 'Test')
        
        with self.assertRaises(ValidationError):
            self.workflow_service.reject_step(99999, self.user, 'Test')
        
        # Test invalid file operations
        with self.assertRaises(ValidationError):
            self.file_service.get_file_info(99999)
        
        with self.assertRaises(ValidationError):
            self.file_service.download_file(99999, self.user)
    
    def test_performance_scenarios(self):
        """Test performance scenarios with multiple documents"""
        # Create multiple documents for performance testing
        start_time = timezone.now()
        
        for i in range(10):
            doc_data = {
                'name': f'Performance Test Document {i}',
                'title': f'Performance Test Document {i} Title',
                'document_type_id': self.doc_type.id,
                'category_id': self.category.id,
                'description': f'Performance test document {i}',
                'confidentiality_level': 'internal'
            }
            self.doc_service.create_document(doc_data, self.user)
        
        creation_time = timezone.now() - start_time
        self.assertLess(creation_time.total_seconds(), 5.0)  # Should complete within 5 seconds
        
        # Test bulk search performance
        start_time = timezone.now()
        search_results = self.search_service.full_text_search('Performance Test')
        search_time = timezone.now() - start_time
        
        self.assertIsInstance(search_results, list)
        self.assertEqual(len(search_results), 10)
        self.assertLess(search_time.total_seconds(), 2.0)  # Should complete within 2 seconds
    
    def test_integration_scenarios(self):
        """Test integration scenarios between different services"""
        # Create a document
        doc_data = {
            'name': 'Integration Test Document',
            'title': 'Integration Test Document Title',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test document for integration testing',
            'confidentiality_level': 'internal'
        }
        
        document = self.doc_service.create_document(doc_data, self.user)
        
        # Test workflow integration
        workflow_status = self.workflow_service.get_workflow_status(document.id)
        self.assertIsNotNone(workflow_status)
        
        # Test search integration
        search_results = self.search_service.full_text_search('Integration Test')
        self.assertIn(document.id, [doc['id'] for doc in search_results])
        
        # Test file integration
        if hasattr(document, 'attachment') and document.attachment:
            file_info = self.file_service.get_file_info(document.attachment.id)
            self.assertIsInstance(file_info, dict)
    
    def test_data_consistency(self):
        """Test data consistency across different operations"""
        # Create a document
        doc_data = {
            'name': 'Consistency Test Document',
            'title': 'Consistency Test Document Title',
            'document_type_id': self.doc_type.id,
            'category_id': self.category.id,
            'description': 'Test document for consistency testing',
            'confidentiality_level': 'internal'
        }
        
        document = self.doc_service.create_document(doc_data, self.user)
        original_id = document.id
        
        # Verify document exists in database
        retrieved_doc = self.doc_service.get_document(original_id)
        self.assertIsNotNone(retrieved_doc)
        self.assertEqual(retrieved_doc.id, original_id)
        self.assertEqual(retrieved_doc.name, doc_data['name'])
        
        # Update document
        update_data = {'title': 'Updated Consistency Title'}
        updated_doc = self.doc_service.update_document(original_id, update_data, self.user)
        
        # Verify update consistency
        self.assertEqual(updated_doc.id, original_id)
        self.assertEqual(updated_doc.title, update_data['title'])
        self.assertEqual(updated_doc.name, doc_data['name'])  # Unchanged field
        
        # Verify database consistency
        db_doc = DMSDocument.objects.get(id=original_id)
        self.assertEqual(db_doc.title, update_data['title'])
        self.assertEqual(db_doc.name, doc_data['name'])
    
    def test_cleanup_and_maintenance(self):
        """Test cleanup and maintenance operations"""
        # Create test documents
        for i in range(3):
            doc_data = {
                'name': f'Cleanup Test Document {i}',
                'title': f'Cleanup Test Document {i} Title',
                'document_type_id': self.doc_type.id,
                'category_id': self.category.id,
                'description': f'Cleanup test document {i}',
                'confidentiality_level': 'internal'
            }
            self.doc_service.create_document(doc_data, self.user)
        
        # Verify documents exist
        documents = self.doc_service.list_documents()
        self.assertGreaterEqual(len(documents), 3)
        
        # Clean up test documents
        for doc in documents:
            if doc.name.startswith('Cleanup Test Document'):
                self.doc_service.delete_document(doc.id, self.user)
        
        # Verify cleanup
        remaining_docs = self.doc_service.list_documents()
        cleanup_docs = [doc for doc in remaining_docs if doc.name.startswith('Cleanup Test Document')]
        self.assertEqual(len(cleanup_docs), 0)
    
    def tearDown(self):
        """Clean up test data"""
        # Clean up any remaining test files
        try:
            for attachment in DMSFileAttachment.objects.all():
                if os.path.exists(attachment.file.path):
                    os.remove(attachment.file.path)
        except Exception:
            pass
        
        # Clean up test data
        DMSDocument.objects.filter(company_id=self.company_id).delete()
        DMSDocumentType.objects.filter(name__startswith='Test').delete()
        DMSDocumentCategory.objects.filter(name__startswith='Test').delete()
        DMSDocumentTag.objects.filter(name__startswith='Test').delete()
        User.objects.filter(username='testuser').delete()
