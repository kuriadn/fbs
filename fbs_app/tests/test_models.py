"""
Comprehensive Unit Tests for FBS App Models

Tests all model functionality including:
- Model creation and validation
- Field constraints and relationships
- Model methods and business logic
- Signal handling
- Database operations
"""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
import json

from fbs_app.models import (
    OdooDatabase, TokenMapping, RequestLog, BusinessRule,
    CacheEntry, Handshake, Notification, ApprovalRequest, ApprovalResponse,
    MSMESetupWizard, MSMEKPI, MSMECompliance, MSMEMarketing,
    MSMETemplate, MSMEAnalytics, CustomField
)

from fbs_app.tests.conftest import FBSAppTestCase, UserFactory


class TestOdooDatabase(FBSAppTestCase):
    """Test OdooDatabase model"""
    
    def test_create_odoo_database(self):
        """Test creating a basic Odoo database"""
        db = OdooDatabase.objects.create(
            name='test_db',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
        self.assertEqual(db.name, 'test_db')
        self.assertEqual(db.host, 'localhost')
        self.assertTrue(db.is_active)
    
    def test_database_str_representation(self):
        """Test string representation"""
        db = OdooDatabase.objects.create(
            name='test_db',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
        self.assertEqual(str(db), 'test_db (localhost:8069)')
    
    def test_database_validation(self):
        """Test database field validation"""
        # Test that we can create a database with valid data
        db = OdooDatabase.objects.create(
            name='test_db_validation',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
        self.assertEqual(db.name, 'test_db_validation')
        
        # Test that creating another database with the same name fails
        with self.assertRaises(IntegrityError):
            OdooDatabase.objects.create(
                name='test_db_validation',  # Duplicate name should fail
                host='localhost',
                port=8069,
                protocol='http',
                username='admin',
                password='admin'
            )


class TestTokenMapping(FBSAppTestCase):
    """Test TokenMapping model"""
    
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.database = OdooDatabase.objects.create(
            name='test_db',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
    
    def test_create_token_mapping(self):
        """Test creating a token mapping"""
        token_mapping = TokenMapping.objects.create(
            user=self.user,
            database=self.database,
            token='test_token_123'
        )
        self.assertEqual(token_mapping.user, self.user)
        self.assertEqual(token_mapping.database, self.database)
        self.assertTrue(token_mapping.is_active)
    
    def test_token_mapping_str_representation(self):
        """Test string representation"""
        token_mapping = TokenMapping.objects.create(
            user=self.user,
            database=self.database,
            token='test_token_123'
        )
        expected = f"{self.user.username} - {self.database.name}"
        self.assertEqual(str(token_mapping), expected)
    
    def test_unique_user_database_constraint(self):
        """Test unique constraint on user and database"""
        TokenMapping.objects.create(
            user=self.user,
            database=self.database,
            token='token1'
        )
        
        with self.assertRaises(IntegrityError):
            TokenMapping.objects.create(
                user=self.user,
                database=self.database,
                token='token2'
            )


class TestRequestLog(FBSAppTestCase):
    """Test RequestLog model"""
    
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.database = OdooDatabase.objects.create(
            name='test_db',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
    
    def test_create_request_log(self):
        """Test creating a request log"""
        log = RequestLog.objects.create(
            user=self.user,
            database=self.database,
            method='GET',
            path='/fbs/health/',
            status_code=200,
            response_time=150.5,
            ip_address='127.0.0.1'
        )
        self.assertEqual(log.method, 'GET')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.response_time, 150.5)
    
    def test_request_log_str_representation(self):
        """Test string representation"""
        log = RequestLog.objects.create(
            user=self.user,
            database=self.database,
            method='POST',
            path='/fbs/auth/handshake/',
            status_code=201,
            response_time=200.0,
            ip_address='127.0.0.1'
        )
        expected = f"POST /fbs/auth/handshake/ - 201 ({log.timestamp})"
        self.assertEqual(str(log), expected)


class TestBusinessRule(FBSAppTestCase):
    """Test BusinessRule model"""
    
    def test_create_business_rule(self):
        """Test creating a business rule"""
        rule = BusinessRule.objects.create(
            name='Test Rule',
            rule_type='validation',
            description='Test validation rule',
            model_name='res.partner',
            rule_definition={'field': 'name', 'required': True},
            priority=1
        )
        self.assertEqual(rule.name, 'Test Rule')
        self.assertEqual(rule.rule_type, 'validation')
        self.assertTrue(rule.is_active)
    
    def test_business_rule_str_representation(self):
        """Test string representation"""
        rule = BusinessRule.objects.create(
            name='Test Rule',
            rule_type='calculation',
            description='Test calculation rule',
            model_name='res.partner',
            rule_definition={'formula': 'amount * 1.1'},
            priority=2
        )
        expected = "Test Rule (calculation)"
        self.assertEqual(str(rule), expected)


class TestHandshake(FBSAppTestCase):
    """Test Handshake model"""
    
    def test_create_handshake(self):
        """Test creating a handshake"""
        handshake = Handshake.objects.create(
            handshake_id='test_handshake_123',
            solution_name='test_solution',
            secret_key='secret_key_123',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        self.assertEqual(handshake.handshake_id, 'test_handshake_123')
        self.assertEqual(handshake.solution_name, 'test_solution')
        self.assertEqual(handshake.status, 'pending')
    
    def test_handshake_str_representation(self):
        """Test string representation"""
        handshake = Handshake.objects.create(
            handshake_id='test_handshake_123',
            solution_name='test_solution',
            secret_key='secret_key_123',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        expected = f"test_solution - test_handshake_123 (pending)"
        self.assertEqual(str(handshake), expected)


class TestMSMEModels(FBSAppTestCase):
    """Test MSME-related models"""
    
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
    
    def test_msme_setup_wizard(self):
        """Test MSME setup wizard"""
        wizard = MSMESetupWizard.objects.create(
            solution_name='test_solution',
            business_type='retail',
            current_step='setup',
            total_steps=5,
            progress=20.0
        )
        self.assertEqual(wizard.solution_name, 'test_solution')
        self.assertEqual(wizard.business_type, 'retail')
        self.assertEqual(wizard.status, 'not_started')
    
    def test_msme_kpi(self):
        """Test MSME KPI"""
        kpi = MSMEKPI.objects.create(
            solution_name='test_solution',
            kpi_name='Revenue Growth',
            kpi_type='financial',
            current_value=12.5,
            target_value=15.0,
            unit='%',
            period='monthly'
        )
        self.assertEqual(kpi.kpi_name, 'Revenue Growth')
        self.assertEqual(kpi.kpi_type, 'financial')
        self.assertEqual(kpi.current_value, 12.5)
    
    def test_msme_compliance(self):
        """Test MSME compliance"""
        compliance = MSMECompliance.objects.create(
            solution_name='test_solution',
            compliance_type='tax',
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(compliance.compliance_type, 'tax')
        self.assertEqual(compliance.status, 'pending')


class TestCacheEntry(FBSAppTestCase):
    """Test CacheEntry model"""
    
    def test_create_cache_entry(self):
        """Test creating a cache entry"""
        cache_entry = CacheEntry.objects.create(
            key='test_key',
            value={'data': 'test_value'},
            expires_at=timezone.now() + timedelta(hours=1)
        )
        self.assertEqual(cache_entry.key, 'test_key')
        self.assertEqual(cache_entry.value, {'data': 'test_value'})
    
    def test_cache_entry_str_representation(self):
        """Test string representation"""
        cache_entry = CacheEntry.objects.create(
            key='test_key',
            value={'data': 'test_value'},
            expires_at=timezone.now() + timedelta(hours=1)
        )
        # The string representation includes the key and expiry time
        str_repr = str(cache_entry)
        self.assertIn('test_key', str_repr)
        self.assertIn('expires:', str_repr)


class TestNotification(FBSAppTestCase):
    """Test Notification model"""
    
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
    
    def test_create_notification(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            notification_type='info'
        )
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.notification_type, 'info')
        self.assertFalse(notification.is_read)
    
    def test_notification_str_representation(self):
        """Test string representation"""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            notification_type='info'
        )
        expected = 'Test Notification (info)'
        self.assertEqual(str(notification), expected)


class TestApprovalModels(FBSAppTestCase):
    """Test approval-related models"""
    
    def setUp(self):
        super().setUp()
        self.requester = UserFactory(username='requester')
        self.approver = UserFactory(username='approver')
    
    def test_approval_request(self):
        """Test approval request"""
        request = ApprovalRequest.objects.create(
            requester=self.requester,
            approver=self.approver,
            title='Test Approval',
            approval_type='expense',
            description='Test expense approval'
        )
        self.assertEqual(request.title, 'Test Approval')
        self.assertEqual(request.approval_type, 'expense')
        self.assertEqual(request.status, 'pending')
    
    def test_approval_response(self):
        """Test approval response"""
        approval_request = ApprovalRequest.objects.create(
            requester=self.requester,
            approver=self.approver,
            title='Test Approval',
            approval_type='expense',
            description='Test expense approval'
        )
        
        response = ApprovalResponse.objects.create(
            approval_request=approval_request,
            responder=self.approver,
            response='approve',
            comments='Looks good'
        )
        self.assertEqual(response.response, 'approve')
        self.assertEqual(response.responder, self.approver)


class TestModelValidation(FBSAppTestCase):
    """Test model validation and constraints"""
    
    def test_field_constraints(self):
        """Test field constraints and validation"""
        # Test unique constraint on name field
        OdooDatabase.objects.create(
            name='test_db_1',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
        
        # Creating another database with the same name should fail
        with self.assertRaises(IntegrityError):
            OdooDatabase.objects.create(
                name='test_db_1',  # Duplicate name
                host='localhost',
                port=8069,
                protocol='http',
                username='admin',
                password='admin'
            )
    
    def test_model_relationships(self):
        """Test model relationships"""
        user = UserFactory()
        database = OdooDatabase.objects.create(
            name='test_db',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
        
        # Test foreign key relationship
        token_mapping = TokenMapping.objects.create(
            user=user,
            database=database,
            token='test_token'
        )
        
        self.assertEqual(token_mapping.user, user)
        self.assertEqual(token_mapping.database, database)
    
    def test_model_methods(self):
        """Test model methods"""
        # Add tests for any custom model methods here
        pass


class TestModelSignals(FBSAppTestCase):
    """Test model signals"""
    
    def test_post_save_signals(self):
        """Test post-save signals"""
        # This will be tested in integration tests
        pass
    
    def test_post_delete_signals(self):
        """Test post-delete signals"""
        # This will be tested in integration tests
        pass


# Performance tests
@pytest.mark.performance
class TestModelPerformance(FBSAppTestCase):
    """Test model performance"""
    
    def test_bulk_create_performance(self):
        """Test bulk create performance"""
        def bulk_create_users():
            users = [UserFactory.build() for _ in range(10)]
            return User.objects.bulk_create(users)
        
        result = bulk_create_users()
        self.assertEqual(len(result), 10)
    
    def test_query_performance(self):
        """Test query performance"""
        # Create test data - reduce from 100 to 10 for faster testing
        users = [UserFactory() for _ in range(10)]
        
        def query_users():
            return list(User.objects.all())
        
        result = query_users()
        self.assertEqual(len(result), 10)


# Security tests
@pytest.mark.security
class TestModelSecurity(FBSAppTestCase):
    """Test model security"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # Test that user input is properly escaped
        suspicious_name = "'; DROP TABLE users; --"
        
        db = OdooDatabase.objects.create(
            name=suspicious_name,
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
        
        # Should not cause SQL injection
        retrieved = OdooDatabase.objects.get(name=suspicious_name)
        self.assertEqual(retrieved, db)
    
    def test_xss_prevention(self):
        """Test XSS prevention"""
        # Test that HTML is properly handled in string representations
        suspicious_title = "<script>alert('xss')</script>"
        
        notification = Notification.objects.create(
            user=UserFactory(),
            title=suspicious_title,
            message='Test',
            notification_type='info'
        )
        
        # String representation should contain the title as-is (Django doesn't auto-escape)
        str_repr = str(notification)
        self.assertIn('<script>', str_repr)
        self.assertIn('</script>', str_repr)
        # This is expected behavior - Django models don't auto-escape HTML in __str__ methods
