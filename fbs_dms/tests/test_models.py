"""
FBS DMS Model Tests

Tests for DMS model functionality.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta

from fbs_dms.models import (
    DocumentType, DocumentCategory, DocumentTag, 
    Document, FileAttachment, DocumentWorkflow, DocumentApproval
)


class DocumentTypeTestCase(TestCase):
    """Test DocumentType model"""
    
    def setUp(self):
        self.doc_type = DocumentType.objects.create(
            name='Invoice',
            code='INV',
            requires_approval=True,
            allowed_extensions='pdf,doc,docx',
            max_file_size=10
        )
    
    def test_document_type_creation(self):
        """Test document type creation"""
        self.assertEqual(self.doc_type.name, 'Invoice')
        self.assertEqual(self.doc_type.code, 'INV')
        self.assertTrue(self.doc_type.requires_approval)
        self.assertEqual(self.doc_type.max_file_size, 10)
    
    def test_get_allowed_extensions_list(self):
        """Test getting allowed extensions as list"""
        extensions = self.doc_type.get_allowed_extensions_list()
        self.assertEqual(extensions, ['pdf', 'doc', 'docx'])
    
    def test_is_extension_allowed(self):
        """Test extension validation"""
        self.assertTrue(self.doc_type.is_extension_allowed('document.pdf'))
        self.assertTrue(self.doc_type.is_extension_allowed('invoice.docx'))
        self.assertFalse(self.doc_type.is_extension_allowed('image.jpg'))
        self.assertFalse(self.doc_type.is_extension_allowed('file.txt'))


class DocumentCategoryTestCase(TestCase):
    """Test DocumentCategory model"""
    
    def setUp(self):
        self.parent_category = DocumentCategory.objects.create(
            name='Financial',
            sequence=1
        )
        self.child_category = DocumentCategory.objects.create(
            name='Invoices',
            parent=self.parent_category,
            sequence=1
        )
    
    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.parent_category.name, 'Financial')
        self.assertEqual(self.child_category.name, 'Invoices')
        self.assertEqual(self.child_category.parent, self.parent_category)
    
    def test_category_str_representation(self):
        """Test category string representation"""
        self.assertEqual(str(self.parent_category), 'Financial')
        self.assertEqual(str(self.child_category), 'Financial > Invoices')


class DocumentTagTestCase(TestCase):
    """Test DocumentTag model"""
    
    def setUp(self):
        self.tag = DocumentTag.objects.create(
            name='Important',
            color=1
        )
    
    def test_tag_creation(self):
        """Test tag creation"""
        self.assertEqual(self.tag.name, 'Important')
        self.assertEqual(self.tag.color, 1)
        self.assertTrue(self.tag.is_active)


class FileAttachmentTestCase(TestCase):
    """Test FileAttachment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_file_attachment_creation(self):
        """Test file attachment creation"""
        # Note: In real tests, you'd use a mock file object
        # This is a simplified test for model structure
        attachment = FileAttachment.objects.create(
            original_filename='test.pdf',
            file_size=1024,
            mime_type='application/pdf',
            checksum='abc123',
            uploaded_by=self.user,
            company_id='company_123'
        )
        
        self.assertEqual(attachment.original_filename, 'test.pdf')
        self.assertEqual(attachment.file_size, 1024)
        self.assertEqual(attachment.mime_type, 'application/pdf')
        self.assertEqual(attachment.uploaded_by, self.user)
    
    def test_file_size_conversion(self):
        """Test file size conversion methods"""
        attachment = FileAttachment.objects.create(
            original_filename='test.pdf',
            file_size=1048576,  # 1MB in bytes
            mime_type='application/pdf',
            checksum='abc123',
            uploaded_by=self.user,
            company_id='company_123'
        )
        
        self.assertEqual(attachment.get_file_size_mb(), 1.0)
        self.assertEqual(attachment.get_file_size_kb(), 1024.0)
    
    def test_file_type_detection(self):
        """Test file type detection"""
        attachment = FileAttachment.objects.create(
            original_filename='test.pdf',
            file_size=1024,
            mime_type='application/pdf',
            checksum='abc123',
            uploaded_by=self.user,
            company_id='company_123'
        )
        
        self.assertTrue(attachment.is_pdf())
        self.assertFalse(attachment.is_image())
        self.assertFalse(attachment.is_office_document())


class DocumentTestCase(TestCase):
    """Test Document model"""
    
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
        
        self.document = Document.objects.create(
            name='INV-001',
            title='Test Invoice',
            document_type=self.doc_type,
            category=self.category,
            created_by=self.user,
            company_id='company_123',
            confidentiality_level='internal'
        )
    
    def test_document_creation(self):
        """Test document creation"""
        self.assertEqual(self.document.name, 'INV-001')
        self.assertEqual(self.document.title, 'Test Invoice')
        self.assertEqual(self.document.document_type, self.doc_type)
        self.assertEqual(self.document.category, self.category)
        self.assertEqual(self.document.created_by, self.user)
        self.assertEqual(self.document.state, 'draft')
        self.assertEqual(self.document.confidentiality_level, 'internal')
    
    def test_document_str_representation(self):
        """Test document string representation"""
        self.assertEqual(str(self.document), 'INV-001 - Test Invoice')
    
    def test_document_expiry_check(self):
        """Test document expiry checking"""
        # Document with no expiry date
        self.assertFalse(self.document.is_expired())
        
        # Document with future expiry date
        self.document.expiry_date = date.today() + timedelta(days=30)
        self.document.save()
        self.assertFalse(self.document.is_expired())
        
        # Document with past expiry date
        self.document.expiry_date = date.today() - timedelta(days=1)
        self.document.save()
        self.assertTrue(self.document.is_expired())
    
    def test_document_approval_capabilities(self):
        """Test document approval capabilities"""
        # Document type doesn't require approval
        self.assertFalse(self.document.can_be_approved())
        self.assertFalse(self.document.can_be_rejected())
        
        # Change document type to require approval
        self.doc_type.requires_approval = True
        self.doc_type.save()
        
        # Document is in draft state, not pending
        self.assertFalse(self.document.can_be_approved())
        self.assertFalse(self.document.can_be_rejected())
        
        # Change document to pending state
        self.document.state = 'pending'
        self.document.save()
        
        self.assertTrue(self.document.can_be_approved())
        self.assertTrue(self.document.can_be_rejected())


class DocumentWorkflowTestCase(TestCase):
    """Test DocumentWorkflow model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.doc_type = DocumentType.objects.create(
            name='Invoice',
            code='INV',
            requires_approval=True,
            max_file_size=10
        )
        
        self.category = DocumentCategory.objects.create(
            name='Financial',
            sequence=1
        )
        
        self.document = Document.objects.create(
            name='INV-001',
            title='Test Invoice',
            document_type=self.doc_type,
            category=self.category,
            created_by=self.user,
            company_id='company_123'
        )
        
        self.workflow = DocumentWorkflow.objects.create(
            document=self.document,
            status='active'
        )
    
    def test_workflow_creation(self):
        """Test workflow creation"""
        self.assertEqual(self.workflow.document, self.document)
        self.assertEqual(self.workflow.status, 'active')
        self.assertIsNone(self.workflow.completed_at)
    
    def test_workflow_status_checking(self):
        """Test workflow status checking"""
        self.assertTrue(self.workflow.is_active())
        self.assertFalse(self.workflow.is_completed())
        
        # Complete workflow
        self.workflow.complete_workflow()
        self.assertTrue(self.workflow.is_completed())
        self.assertFalse(self.workflow.is_active())
    
    def test_workflow_str_representation(self):
        """Test workflow string representation"""
        self.assertEqual(str(self.workflow), 'Workflow for INV-001')


class DocumentApprovalTestCase(TestCase):
    """Test DocumentApproval model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='approver123'
        )
        
        self.doc_type = DocumentType.objects.create(
            name='Invoice',
            code='INV',
            requires_approval=True,
            max_file_size=10
        )
        
        self.category = DocumentCategory.objects.create(
            name='Financial',
            sequence=1
        )
        
        self.document = Document.objects.create(
            name='INV-001',
            title='Test Invoice',
            document_type=self.doc_type,
            category=self.category,
            created_by=self.user,
            company_id='company_123'
        )
        
        self.workflow = DocumentWorkflow.objects.create(
            document=self.document,
            status='active'
        )
        
        self.approval = DocumentApproval.objects.create(
            workflow=self.workflow,
            approver=self.approver,
            sequence=1,
            status='pending',
            required=True
        )
    
    def test_approval_creation(self):
        """Test approval creation"""
        self.assertEqual(self.approval.workflow, self.workflow)
        self.assertEqual(self.approval.approver, self.approver)
        self.assertEqual(self.approval.sequence, 1)
        self.assertEqual(self.approval.status, 'pending')
        self.assertTrue(self.approval.required)
    
    def test_approval_status_checking(self):
        """Test approval status checking"""
        self.assertTrue(self.approval.is_pending())
        self.assertFalse(self.approval.is_approved())
        self.assertFalse(self.approval.is_rejected())
    
    def test_approval_capabilities(self):
        """Test approval capabilities"""
        self.assertEqual(self.approval.can_approve(), True)
        self.assertEqual(self.approval.can_reject(), True)
        self.assertEqual(self.approval.can_skip(), False)
        
        # Make approval non-required
        self.approval.required = False
        self.approval.save()
        
        # When required=False, can_approve() and can_reject() return False
        # because they require both is_pending() AND required=True
        self.assertEqual(self.approval.can_approve(), False)
        self.assertEqual(self.approval.can_reject(), False)
        self.assertEqual(self.approval.can_skip(), True)
    
    def test_approval_str_representation(self):
        """Test approval string representation"""
        self.assertEqual(str(self.approval), 'Approval 1 for INV-001')
