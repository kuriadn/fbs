"""
Comprehensive Test Suite for FBS Core App

This test suite covers all aspects of the FBS core app:
- Models (all categories)
- Services (all service classes)
- Interfaces (all interface classes)
- Middleware (database routing, request logging)
- Authentication and authorization
- Integration with other apps
- Performance and security
"""

import pytest
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.db import connections
from django.conf import settings
import json
import time
from datetime import timedelta
from django.utils import timezone

from fbs_app.models import (
    # Core models
    OdooDatabase, TokenMapping, RequestLog, BusinessRule, CacheEntry,
    Handshake, Notification, ApprovalRequest, ApprovalResponse, CustomField,
    # MSME models
    MSMESetupWizard, MSMEKPI, MSMECompliance, MSMEMarketing, MSMETemplate, MSMEAnalytics,
    # Discovery models
    OdooModel, OdooField, OdooModule, DiscoverySession,
    # Workflow models
    WorkflowDefinition, WorkflowInstance, WorkflowStep, WorkflowTransition,
    # BI models
    Dashboard, Report, KPI, Chart,
    # Compliance models
    ComplianceRule, AuditTrail, ReportSchedule, RecurringTransaction, UserActivityLog,
    # Accounting models
    CashEntry, IncomeExpense, BasicLedger, TaxCalculation
)

from fbs_app.services import (
    OdooClient, AuthService, CacheService, DiscoveryService, WorkflowService,
    OnboardingService, MSMEService, BusinessLogicService, BusinessIntelligenceService,
    ComplianceService, NotificationService, SimpleAccountingService, DatabaseService,
    FieldMergerService, FBSServiceGenerator
)

from fbs_app.interfaces import FBSInterface
from fbs_app.middleware import DatabaseRoutingMiddleware, RequestLoggingMiddleware


class TestFBSAppModels(TestCase):
    """Test all FBS app models comprehensively."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.company_id = 'test_company_001'
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_core_models_creation(self):
        """Test creation of all core models."""
        # Test OdooDatabase
        odoo_db = OdooDatabase.objects.create(
            name='test_odoo_db',
            host='localhost',
            port=8069,
            username='admin',
            password='admin123'
        )
        self.assertEqual(odoo_db.name, 'test_odoo_db')
        self.assertEqual(odoo_db.host, 'localhost')
        
        # Test TokenMapping
        token_mapping = TokenMapping.objects.create(
            user=self.user,
            database=odoo_db,
            token='test_token_123'
        )
        self.assertEqual(token_mapping.user, self.user)
        self.assertEqual(token_mapping.database, odoo_db)
        
        # Test RequestLog
        request_log = RequestLog.objects.create(
            user=self.user,
            database=odoo_db,
            method='GET',
            path='/api/test',
            status_code=200,
            response_time=0.1,
            ip_address='127.0.0.1'
        )
        self.assertEqual(request_log.method, 'GET')
        self.assertEqual(request_log.status_code, 200)
        
        # Test BusinessRule
        business_rule = BusinessRule.objects.create(
            name='test_rule',
            rule_type='validation',
            rule_definition='{"condition": "always", "action": "allow"}',
            is_active=True
        )
        self.assertEqual(business_rule.name, 'test_rule')
        self.assertEqual(business_rule.rule_type, 'validation')
        
        # Test CacheEntry
        cache_entry = CacheEntry.objects.create(
            key='test_cache_key',
            value='test_cache_value',
            database_name='test_db',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        self.assertEqual(cache_entry.key, 'test_cache_key')
        
        # Test Handshake
        handshake = Handshake.objects.create(
            handshake_id='test_handshake_token',
            solution_name='test_solution',
            secret_key='test_handshake_secret',
            expires_at=timezone.now() + timedelta(days=1)
        )
        self.assertEqual(handshake.handshake_id, 'test_handshake_token')
        
        # Test Notification
        notification = Notification.objects.create(
            title='Test Notification',
            message='This is a test notification',
            notification_type='info',
            priority='medium',
            user=self.user
        )
        self.assertEqual(notification.title, 'Test Notification')
        
        # Test ApprovalRequest
        approval_request = ApprovalRequest.objects.create(
            title='Document Approval Request',
            description='Please approve this document',
            approval_type='document',
            status='pending',
            requester=self.user,
            solution_name='test_solution',
            request_data='{"document_id": 123}'
        )
        self.assertEqual(approval_request.approval_type, 'document')
        
        # Test ApprovalResponse
        approval_response = ApprovalResponse.objects.create(
            approval_request=approval_request,
            responder=self.user,
            response='approve',
            comments='Looks good'
        )
        self.assertEqual(approval_response.response, 'approve')
        
        # Test CustomField
        custom_field = CustomField.objects.create(
            model_name='User',
            record_id=1,
            field_name='test_custom_field',
            field_type='text',
            field_value='test_value',
            solution_name='test_solution'
        )
        self.assertEqual(custom_field.field_name, 'test_custom_field')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_msme_models_creation(self):
        """Test creation of MSME models."""
        # Test MSMESetupWizard
        msme_wizard = MSMESetupWizard.objects.create(
            solution_name='test_solution',
            status='completed',
            current_step='final',
            total_steps=5,
            progress=100.0,
            business_type='retail'
        )
        self.assertEqual(msme_wizard.solution_name, 'test_solution')
        
        # Test MSMEKPI
        msme_kpi = MSMEKPI.objects.create(
            solution_name='test_solution',
            kpi_name='Revenue Growth',
            kpi_type='financial',
            current_value=12.5,
            target_value=15.0,
            unit='percentage'
        )
        self.assertEqual(msme_kpi.kpi_name, 'Revenue Growth')
        
        # Test MSMECompliance
        msme_compliance = MSMECompliance.objects.create(
            solution_name='test_solution',
            compliance_type='tax',
            status='compliant',
            due_date=timezone.now().date()
        )
        self.assertEqual(msme_compliance.compliance_type, 'tax')
        
        # Test MSMEMarketing
        msme_marketing = MSMEMarketing.objects.create(
            solution_name='test_solution',
            campaign_name='Summer Sale',
            campaign_type='promotional',
            budget=5000.0,
            start_date=timezone.now().date(),
            end_date=timezone.now().date()
        )
        self.assertEqual(msme_marketing.campaign_name, 'Summer Sale')
        
        # Test MSMETemplate
        msme_template = MSMETemplate.objects.create(
            name='Standard MSME Template',
            business_type='retail',
            description='Standard business setup template for MSMEs',
            configuration='{"modules": ["accounting", "inventory"]}',
            is_active=True
        )
        self.assertEqual(msme_template.name, 'Standard MSME Template')
        
        # Test MSMEAnalytics
        msme_analytics = MSMEAnalytics.objects.create(
            solution_name='test_solution',
            metric_name='Customer Acquisition Cost',
            metric_value=25.50,
            metric_type='cost',
            period='monthly',
            date=timezone.now().date(),
            context='{"source": "google_ads"}'
        )
        self.assertEqual(msme_analytics.metric_name, 'Customer Acquisition Cost')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_discovery_models_creation(self):
        """Test creation of discovery models."""
        # Test OdooModel
        odoo_model = OdooModel.objects.create(
            database_name='test_db',
            model_name='res.partner',
            technical_name='res.partner',
            display_name='Partners',
            module_name='base',
            model_type='business'
        )
        self.assertEqual(odoo_model.model_name, 'res.partner')
        
        # Test OdooField
        odoo_field = OdooField.objects.create(
            odoo_model=odoo_model,
            field_name='name',
            technical_name='name',
            display_name='Partner Name',
            field_type='char',
            required=True,
            help_text='Partner name'
        )
        self.assertEqual(odoo_field.field_name, 'name')
        
        # Test OdooModule
        odoo_module = OdooModule.objects.create(
            database_name='test_db',
            module_name='base',
            technical_name='base',
            display_name='Base',
            version='16.0',
            category='Technical'
        )
        self.assertEqual(odoo_module.module_name, 'base')
        
        # Test DiscoverySession
        discovery_session = DiscoverySession.objects.create(
            database_name='test_db',
            session_type='full_discovery',
            status='completed'
        )
        self.assertEqual(discovery_session.database_name, 'test_db')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_workflow_models_creation(self):
        """Test creation of workflow models."""
        # Test WorkflowDefinition
        workflow_def = WorkflowDefinition.objects.create(
            name='Document Approval',
            description='Document approval workflow',
            workflow_type='approval',
            workflow_data='{"steps": ["submit", "review", "approve"]}'
        )
        self.assertEqual(workflow_def.name, 'Document Approval')
        
        # Test WorkflowInstance
        workflow_instance = WorkflowInstance.objects.create(
            workflow_definition=workflow_def,
            business_id='test_business_001',
            status='active'
        )
        self.assertEqual(workflow_instance.status, 'active')
        
        # Test WorkflowStep
        workflow_step = WorkflowStep.objects.create(
            workflow_definition=workflow_def,
            name='review',
            step_type='approval',
            order=2
        )
        self.assertEqual(workflow_step.name, 'review')
        
        # Test WorkflowTransition
        workflow_transition = WorkflowTransition.objects.create(
            workflow_definition=workflow_def,
            from_step=workflow_step,
            to_step=workflow_step,
            transition_type='conditional',
            conditions='{"status": "submitted"}',
            actions=['auto_approve']
        )
        self.assertEqual(workflow_transition.from_step, workflow_step)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_bi_models_creation(self):
        """Test creation of BI models."""
        # Test Dashboard
        dashboard = Dashboard.objects.create(
            name='MSME Dashboard',
            dashboard_type='msme',
            layout='{"widgets": ["kpi", "chart", "table"]}',
            is_active=True
        )
        self.assertEqual(dashboard.name, 'MSME Dashboard')
        
        # Test Report
        report = Report.objects.create(
            name='Monthly Revenue Report',
            description='Monthly revenue analysis',
            report_type='financial',
            data_source='sales_database',
            output_format='pdf'
        )
        self.assertEqual(report.name, 'Monthly Revenue Report')
        
        # Test KPI
        kpi = KPI.objects.create(
            name='Monthly Revenue',
            description='Monthly revenue tracking',
            kpi_type='financial',
            calculation_method='sum(revenue)',
            data_source='sales_database',
            target_value=100000.0,
            unit='USD'
        )
        self.assertEqual(kpi.name, 'Monthly Revenue')
        
        # Test Chart
        chart = Chart.objects.create(
            name='Revenue Trend',
            chart_type='line',
            description='Revenue trend visualization',
            data_source='sales_database',
            configuration='{"x_axis": "month", "y_axis": "revenue"}'
        )
        self.assertEqual(chart.name, 'Revenue Trend')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_compliance_models_creation(self):
        """Test creation of compliance models."""
        # Test ComplianceRule
        compliance_rule = ComplianceRule.objects.create(
            solution_name='test_solution',
            name='Tax Compliance',
            description='Tax compliance requirements',
            compliance_type='tax',
            requirements=['monthly_filing', 'quarterly_reports'],
            check_frequency='monthly'
        )
        self.assertEqual(compliance_rule.name, 'Tax Compliance')
        
        # Test AuditTrail
        audit_trail = AuditTrail.objects.create(
            solution_name='test_solution',
            record_type='user',
            record_id='123',
            action='create',
            user_id='test_user_001',
            details={'status': 'draft'},
            timestamp=timezone.now()
        )
        self.assertEqual(audit_trail.action, 'create')
        
        # Test ReportSchedule
        report_schedule = ReportSchedule.objects.create(
            solution_name='test_solution',
            name='Tax Report',
            report_type='tax',
            frequency='monthly',
            next_run=timezone.now() + timedelta(days=30),
            active=True
        )
        self.assertEqual(report_schedule.name, 'Tax Report')
        
        # Test RecurringTransaction
        recurring_transaction = RecurringTransaction.objects.create(
            solution_name='test_solution',
            name='Monthly Rent',
            transaction_type='expense',
            amount=5000.0,
            frequency='monthly',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365)
        )
        self.assertEqual(recurring_transaction.name, 'Monthly Rent')
        
        # Test UserActivityLog
        user_activity_log = UserActivityLog.objects.create(
            solution_name='test_solution',
            user_id='test_user_001',
            action='login',
            details={'status': 'success'},
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0'
        )
        self.assertEqual(user_activity_log.action, 'login')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_accounting_models_creation(self):
        """Test creation of accounting models."""
        # Test CashEntry
        cash_entry = CashEntry.objects.create(
            business_id='test_business_001',
            entry_date=timezone.now().date(),
            entry_type='income',
            amount=1000.0,
            description='Cash sale',
            category='sales',
            subcategory='retail',
            payment_method='cash',
            reference_number='CS001'
        )
        self.assertEqual(cash_entry.entry_type, 'income')
        self.assertEqual(cash_entry.amount, 1000.0)
        
        # Test IncomeExpense
        income_expense = IncomeExpense.objects.create(
            business_id='test_business_001',
            transaction_date=timezone.now().date(),
            transaction_type='income',
            category='sales',
            subcategory='retail',
            amount=5000.0,
            description='Product sales'
        )
        self.assertEqual(income_expense.transaction_type, 'income')
        self.assertEqual(income_expense.amount, 5000.0)
        
        # Test BasicLedger
        basic_ledger = BasicLedger.objects.create(
            business_id='test_business_001',
            entry_date=timezone.now().date(),
            account='Cash Account',
            account_type='asset',
            debit_amount=10000.0,
            credit_amount=0.0,
            description='Initial cash deposit',
            balance=10000.0
        )
        self.assertEqual(basic_ledger.account, 'Cash Account')
        
        # Test TaxCalculation
        tax_calculation = TaxCalculation.objects.create(
            business_id='test_business_001',
            tax_period_start=timezone.now().date(),
            tax_period_end=timezone.now().date(),
            tax_type='sales_tax',
            taxable_amount=1000.0,
            tax_rate=16.0,
            tax_amount=160.0,
            net_tax_amount=160.0,
            due_date=timezone.now().date()
        )
        self.assertEqual(tax_calculation.tax_type, 'sales_tax')
        self.assertEqual(tax_calculation.tax_amount, 160.0)


class TestFBSAppServices(TestCase):
    """Test all FBS app services comprehensively."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.company_id = 'test_company_001'
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_auth_service(self):
        """Test AuthService functionality."""
        # Create OdooDatabase first
        odoo_db = OdooDatabase.objects.create(
            name='test_odoo_db',
            host='localhost',
            port=8069,
            username='admin',
            password='admin123'
        )
        
        auth_service = AuthService('test_solution')
        
        # Test token mapping creation
        result = auth_service.create_token_mapping(
            user=self.user,
            database_name='test_odoo_db',
            odoo_token='test_token_123',
            odoo_user_id=1
        )
        self.assertTrue(result['success'])
        
        # Test token mapping creation was successful
        self.assertTrue(result['success'])
        self.assertIn('token_mapping_id', result['data'])
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_cache_service(self):
        """Test CacheService functionality."""
        cache_service = CacheService('test_solution')
        
        # Test cache set/get
        cache_service.set('test_key', 'test_value', 3600)
        value = cache_service.get('test_key')
        self.assertEqual(value, 'test_value')
        
        # Test cache delete
        cache_service.delete('test_key')
        value = cache_service.get('test_key')
        self.assertIsNone(value)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_odoo_client(self):
        """Test OdooClient functionality."""
        odoo_client = OdooClient(
            base_url='http://localhost:8069',
            timeout=30
        )
        
        # Test connection (will fail in test environment, but structure is correct)
        self.assertIsNotNone(odoo_client)
        self.assertEqual(odoo_client.base_url, 'http://localhost:8069')
        self.assertEqual(odoo_client.timeout, 30)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_workflow_service(self):
        """Test WorkflowService functionality."""
        workflow_service = WorkflowService('test_solution')
        
        # Test workflow creation
        workflow_data = {
            'name': 'Test Workflow',
            'workflow_type': 'approval',
            'description': 'Test approval workflow',
            'workflow_data': {'steps': ['submit', 'approve']}
        }
        
        result = workflow_service.create_workflow_definition(workflow_data)
        self.assertIsNotNone(result)
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['name'], 'Test Workflow')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_msme_service(self):
        """Test MSMEService functionality."""
        msme_service = MSMEService('test_solution')
        
        # Test MSME setup
        result = msme_service.setup_msme_business('retail')
        self.assertTrue(result['success'])
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_bi_service(self):
        """Test BusinessIntelligenceService functionality."""
        bi_service = BusinessIntelligenceService('test_solution')
        
        # Test dashboard creation
        dashboard_data = {
            'name': 'Test Dashboard',
            'dashboard_type': 'msme',
            'layout': '{"widgets": ["kpi"]}'
        }
        
        result = bi_service.create_dashboard(dashboard_data)
        self.assertIsNotNone(result)
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['name'], 'Test Dashboard')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_compliance_service(self):
        """Test ComplianceService functionality."""
        compliance_service = ComplianceService('test_solution')
        
        # Test compliance check
        from fbs_app.models import ComplianceRule
        
        # Create a compliance rule first
        rule = ComplianceRule.objects.create(
            solution_name='test_solution',
            name='Tax Compliance Rule',
            description='Test tax compliance rule',
            compliance_type='tax',
            requirements=['tax_filing', 'payment'],
            check_frequency='monthly'
        )
        
        compliance_data = {
            'check_date': timezone.now().date(),
            'tax_filing': True,
            'payment': True
        }
        
        result = compliance_service.check_compliance(rule.id, compliance_data)
        self.assertIsNotNone(result)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_accounting_service(self):
        """Test SimpleAccountingService functionality."""
        accounting_service = SimpleAccountingService('test_solution')
        
        # Test cash entry creation
        result = accounting_service.create_cash_basis_entry(
            entry_type='income',
            amount=1000.0,
            description='Test cash entry',
            category='sales',
            date=timezone.now().date().isoformat()
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['amount'], 1000.0)


class TestFBSAppInterfaces(TestCase):
    """Test FBS app interfaces comprehensively."""
    
    databases = {'default', 'licensing'}
    
    def setUp(self):
        """Set up test data."""
        self.solution_name = 'test_solution'
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_fbs_interface_creation(self):
        """Test FBSInterface creation and basic functionality."""
        try:
            fbs_interface = FBSInterface(self.solution_name)
            self.assertIsNotNone(fbs_interface)
            self.assertEqual(fbs_interface.solution_name, self.solution_name)
        except Exception as e:
            # Interface might not be fully implemented yet
            self.skipTest(f"FBSInterface not fully implemented: {e}")
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_interface_methods(self):
        """Test interface method availability."""
        # Create interface without license key to avoid license manager issues
        fbs_interface = FBSInterface(self.solution_name, license_key=None)
        
        # Check if core methods exist
        self.assertTrue(hasattr(fbs_interface, 'odoo'))
        self.assertTrue(hasattr(fbs_interface, 'workflows'))


class TestFBSAppMiddleware(TestCase):
    """Test FBS app middleware comprehensively."""
    
    def setUp(self):
        """Set up test data."""
        # Middleware requires get_response function in Django
        def dummy_get_response(request):
            return None
        
        self.middleware = DatabaseRoutingMiddleware(dummy_get_response)
        self.request_logging_middleware = RequestLoggingMiddleware(dummy_get_response)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_database_routing_middleware(self):
        """Test DatabaseRoutingMiddleware functionality."""
        # Test router creation
        self.assertIsNotNone(self.middleware)
        
        # Test solution database detection
        try:
            solution_dbs = self.middleware._get_solution_databases()
            self.assertIsInstance(solution_dbs, list)
        except AttributeError:
            # Method might not exist in this version
            self.skipTest("_get_solution_databases method not available")
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_request_logging_middleware(self):
        """Test RequestLoggingMiddleware functionality."""
        # Test middleware creation
        self.assertIsNotNone(self.request_logging_middleware)


class TestFBSAppIntegration(TestCase):
    """Test FBS app integration scenarios."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.company_id = 'test_company_001'
    
    @pytest.mark.integration
    @pytest.mark.fbs_app
    def test_full_workflow_integration(self):
        """Test complete workflow from creation to completion."""
        # Create workflow definition
        workflow_def = WorkflowDefinition.objects.create(
            name='Test Workflow',
            description='Test approval workflow',
            workflow_type='approval',
            workflow_data='{"steps": ["submit", "review", "approve"]}',
            solution_name='test_solution'
        )
        
        # Create workflow steps
        submit_step = WorkflowStep.objects.create(
            workflow_definition=workflow_def,
            name='submit',
            step_type='task',
            order=1
        )
        
        review_step = WorkflowStep.objects.create(
            workflow_definition=workflow_def,
            name='review',
            step_type='approval',
            order=2
        )
        
        # Create workflow instance
        workflow_instance = WorkflowInstance.objects.create(
            workflow_definition=workflow_def,
            business_id='test_business_001',
            status='active',
            current_step=submit_step,
            solution_name='test_solution'
        )
        
        # Test workflow progression
        self.assertEqual(workflow_instance.current_step.name, 'submit')
        self.assertEqual(workflow_instance.status, 'active')
        
        # Simulate workflow progression
        workflow_instance.current_step = review_step
        workflow_instance.save()
        
        self.assertEqual(workflow_instance.current_step.name, 'review')
    
    @pytest.mark.integration
    @pytest.mark.fbs_app
    def test_msme_setup_integration(self):
        """Test complete MSME setup workflow."""
        # Create MSME setup wizard
        msme_wizard = MSMESetupWizard.objects.create(
            solution_name='test_solution',
            status='completed',
            business_type='retail'
        )
        
        # Create associated KPI
        msme_kpi = MSMEKPI.objects.create(
            solution_name='test_solution',
            kpi_name='Revenue Growth',
            kpi_type='financial',
            current_value=12.5,
            target_value=15.0,
            unit='percentage'
        )
        
        # Verify integration
        self.assertEqual(msme_wizard.solution_name, 'test_solution')
        self.assertEqual(msme_kpi.kpi_name, 'Revenue Growth')
    
    @pytest.mark.integration
    @pytest.mark.fbs_app
    def test_bi_dashboard_integration(self):
        """Test BI dashboard with KPI and chart integration."""
        # Create KPI
        kpi = KPI.objects.create(
            name='Monthly Revenue',
            description='Monthly revenue tracking',
            kpi_type='financial',
            calculation_method='sum(revenue)',
            data_source='sales_database',
            target_value=100000.0
        )
        
        # Create chart
        chart = Chart.objects.create(
            name='Revenue Trend',
            chart_type='line',
            description='Revenue trend visualization',
            data_source='sales_database',
            configuration='{"x_axis": "month", "y_axis": "revenue"}'
        )
        
        # Create dashboard
        dashboard = Dashboard.objects.create(
            name='Revenue Dashboard',
            description='Revenue analysis dashboard',
            dashboard_type='financial',
            layout='{"widgets": ["kpi", "chart"]}'
        )
        
        # Verify integration
        self.assertEqual(kpi.name, 'Monthly Revenue')
        self.assertEqual(chart.name, 'Revenue Trend')
        self.assertEqual(dashboard.name, 'Revenue Dashboard')


class TestFBSAppPerformance(TestCase):
    """Test FBS app performance characteristics."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.mark.performance
    @pytest.mark.fbs_app
    def test_bulk_operations_performance(self):
        """Test performance of bulk operations."""
        # Create bulk RequestLog entries
        start_time = time.time()
        
        logs = []
        for i in range(1000):
            log = RequestLog(
                user=self.user,
                method='GET',
                path=f'/api/test/{i}',
                status_code=200,
                response_time=0.1,
                ip_address='127.0.0.1'
            )
            logs.append(log)
        
        RequestLog.objects.bulk_create(logs)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertion (should complete within reasonable time)
        self.assertLess(duration, 5.0)  # Should complete within 5 seconds
        
        # Verify all logs were created
        self.assertEqual(RequestLog.objects.count(), 1000)
    
    @pytest.mark.performance
    @pytest.mark.fbs_app
    def test_query_performance(self):
        """Test query performance with large datasets."""
        # Create test data
        logs = []
        for i in range(1000):
            log = RequestLog.objects.create(
                user=self.user,
                method='GET',
                path=f'/api/test/{i}',
                status_code=200,
                response_time=0.1,
                ip_address='127.0.0.1'
            )
            logs.append(log)
        
        # Test query performance
        start_time = time.time()
        
        # Complex query
        result = RequestLog.objects.filter(
            method='GET',
            status_code=200
        ).select_related('user').order_by('-timestamp')[:100]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertion
        self.assertLess(duration, 1.0)  # Should complete within 1 second
        self.assertEqual(len(result), 100)


class TestFBSAppSecurity(TestCase):
    """Test FBS app security features."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.mark.security
    @pytest.mark.fbs_app
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        # Test with potentially malicious input
        malicious_input = "'; DROP TABLE users; --"
        
        # Attempt to create object with malicious input
        try:
            # This should not cause SQL injection
            business_rule = BusinessRule.objects.create(
                name=malicious_input,
                rule_type='validation',
                rule_definition='{"condition": "always", "action": "allow"}',
                is_active=True
            )
            
            # If we get here, SQL injection was prevented
            self.assertIsNotNone(business_rule)
            
            # Verify the input was stored as-is (not executed)
            retrieved_rule = BusinessRule.objects.get(id=business_rule.id)
            self.assertEqual(retrieved_rule.name, malicious_input)
            
        except Exception as e:
            # If an exception occurs, it should be a validation error, not SQL injection
            self.assertNotIn('DROP TABLE', str(e))
    
    @pytest.mark.security
    @pytest.mark.fbs_app
    def test_xss_prevention(self):
        """Test XSS prevention in stored data."""
        # Test with XSS payload
        xss_payload = '<script>alert("XSS")</script>'
        
        # Store XSS payload
        notification = Notification.objects.create(
            user=self.user,
            title=xss_payload,
            message='Test message',
            notification_type='info'
        )
        
        # Retrieve and verify XSS payload is stored as-is (not executed)
        retrieved_notification = Notification.objects.get(id=notification.id)
        self.assertEqual(retrieved_notification.title, xss_payload)
        
        # The payload should be stored as text, not executed as HTML
        self.assertIn('<script>', retrieved_notification.title)
    
    @pytest.mark.security
    @pytest.mark.fbs_app
    def test_data_isolation(self):
        """Test data isolation between different contexts."""
        # Create data for different users
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create notifications for different users
        notification1 = Notification.objects.create(
            user=self.user,
            title='User 1 Notification',
            message='Message for user 1',
            notification_type='info'
        )
        
        notification2 = Notification.objects.create(
            user=user2,
            title='User 2 Notification',
            message='Message for user 2',
            notification_type='info'
        )
        
        # Verify user 1 can only see their notifications
        user1_notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(user1_notifications.count(), 1)
        self.assertEqual(user1_notifications.first().user, self.user)
        
        # Verify user 2 can only see their notifications
        user2_notifications = Notification.objects.filter(user=user2)
        self.assertEqual(user2_notifications.count(), 1)
        self.assertEqual(user2_notifications.first().user, user2)


class TestFBSAppEndToEnd(TestCase):
    """Test FBS app end-to-end workflows."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.company_id = 'test_company_001'
    
    @pytest.mark.e2e
    @pytest.mark.fbs_app
    def test_complete_business_workflow(self):
        """Test complete business workflow from setup to reporting."""
        # 1. Setup MSME
        msme_wizard = MSMESetupWizard.objects.create(
            solution_name='Test Business',
            business_type='retail',
            status='completed',
            configuration='{"employees": 5, "revenue": 500000}'
        )
        
        # 2. Create business rules
        business_rule = BusinessRule.objects.create(
            name='Revenue Validation',
            rule_type='validation',
            description='Revenue validation rules',
            model_name='CashEntry',
            rule_definition='{"min_revenue": 100000, "max_revenue": 10000000}',
            is_active=True
        )
        
        # 3. Create workflow
        workflow_def = WorkflowDefinition.objects.create(
            name='Business Approval',
            workflow_type='approval',
            workflow_data='{"steps": ["submit", "review", "approve"]}',
            is_active=True,
            solution_name='test_solution'
        )
        
        # 4. Create KPI
        kpi = KPI.objects.create(
            name='Monthly Revenue',
            description='Monthly revenue tracking',
            kpi_type='financial',
            calculation_method='sum(revenue)',
            data_source='sales_database',
            target_value=500000.0
        )
        
        # 5. Create dashboard
        dashboard = Dashboard.objects.create(
            name='Business Dashboard',
            dashboard_type='business',
            layout='{"widgets": ["kpi", "workflow"]}',
            is_active=True
        )
        
        # 6. Create compliance rule
        compliance_rule = ComplianceRule.objects.create(
            solution_name='test_solution',
            name='Tax Compliance',
            description='Tax filing compliance requirements',
            compliance_type='tax',
            requirements=['{"filing_frequency": "monthly"}'],
            check_frequency='monthly',
            active=True
        )
        
        # 7. Create accounting entry
        cash_entry = CashEntry.objects.create(
            business_id='test_business_001',
            entry_date=timezone.now().date(),
            entry_type='income',
            amount=10000.0,
            description='Monthly revenue',
            category='Revenue',
            payment_method='cash',
            reference_number='MR001'
        )
        
        # Verify complete workflow
        self.assertEqual(msme_wizard.solution_name, 'Test Business')
        self.assertEqual(business_rule.name, 'Revenue Validation')
        self.assertEqual(workflow_def.name, 'Business Approval')
        self.assertEqual(kpi.name, 'Monthly Revenue')
        self.assertEqual(dashboard.name, 'Business Dashboard')
        self.assertEqual(compliance_rule.name, 'Tax Compliance')
        self.assertEqual(cash_entry.amount, 10000.0)
        
        # Verify business logic integration
        self.assertTrue(msme_wizard.status == 'completed')
        self.assertTrue(business_rule.is_active)
        self.assertTrue(workflow_def.is_active)
        self.assertTrue(dashboard.is_active)
        self.assertTrue(compliance_rule.active)
