"""
Comprehensive Model Tests for FBS Core App

This test suite covers all models in the FBS Core App:
- Core models (OdooDatabase, TokenMapping, RequestLog, etc.)
- MSME models (MSMESetupWizard, MSMEKPI, etc.)
- Discovery models (OdooModel, OdooField, etc.)
- Workflow models (WorkflowDefinition, WorkflowInstance, etc.)
- BI models (KPI, Chart, Report, etc.)
- Compliance models (ComplianceRule, AuditTrail, etc.)
- Accounting models (CashEntry, BasicLedger, etc.)
"""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
import time
from fbs_app.models import (
    # Core models
    OdooDatabase, TokenMapping, RequestLog, BusinessRule, CustomField,
    ApprovalRequest, ApprovalResponse, Notification, Handshake, CacheEntry,
    # MSME models
    MSMESetupWizard, MSMEKPI, MSMEAnalytics, MSMECompliance, MSMEMarketing, MSMETemplate,
    # Discovery models
    OdooModule, OdooModel, OdooField, DiscoverySession,
    # Workflow models
    WorkflowDefinition, WorkflowInstance, WorkflowStep, WorkflowTransition,
    # BI models
    KPI, Chart, Report,
    # Compliance models
    ComplianceRule, AuditTrail, RecurringTransaction, ReportSchedule, UserActivityLog,
    # Accounting models
    CashEntry, BasicLedger, IncomeExpense, TaxCalculation
)
from django.utils import timezone
from datetime import timedelta


class TestFBSAppCoreModels(TestCase):
    """Test FBS Core App core models."""
    
    databases = {'default'}
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_odoo_database_model(self):
        """Test OdooDatabase model creation."""
        database = OdooDatabase.objects.create(
            name='test_db',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin123'
        )
        
        self.assertEqual(database.name, 'test_db')
        self.assertEqual(database.host, 'localhost')
        self.assertEqual(database.port, 8069)
        self.assertTrue(database.is_active)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_token_mapping_model(self):
        """Test TokenMapping model creation."""
        database = OdooDatabase.objects.create(
            name='test_db',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin123'
        )
        
        token_mapping = TokenMapping.objects.create(
            user=self.user,
            database=database,
            token='test_token_123'
        )
        
        self.assertEqual(token_mapping.user, self.user)
        self.assertEqual(token_mapping.database, database)
        self.assertEqual(token_mapping.token, 'test_token_123')
        self.assertTrue(token_mapping.is_active)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_request_log_model(self):
        """Test RequestLog model creation."""
        database = OdooDatabase.objects.create(
            name='test_db',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin123'
        )
        
        request_log = RequestLog.objects.create(
            user=self.user,
            database=database,
            method='GET',
            path='/api/test',
            status_code=200,
            response_time=150.5,
            ip_address='127.0.0.1',
            user_agent='Test Browser',
            request_data={'param': 'value'},
            response_data={'result': 'success'}
        )
        
        self.assertEqual(request_log.user, self.user)
        self.assertEqual(request_log.method, 'GET')
        self.assertEqual(request_log.status_code, 200)
        self.assertEqual(request_log.response_time, 150.5)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_business_rule_model(self):
        """Test BusinessRule model creation."""
        business_rule = BusinessRule.objects.create(
            name='test_rule',
            rule_type='validation',
            rule_definition='{"condition": "value > 0"}',
            is_active=True
        )
        
        self.assertEqual(business_rule.name, 'test_rule')
        self.assertEqual(business_rule.rule_type, 'validation')
        self.assertTrue(business_rule.is_active)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_approval_request_model(self):
        """Test ApprovalRequest model creation."""
        approval_request = ApprovalRequest.objects.create(
            title='Test Approval Request',
            description='This is a test approval request',
            approval_type='workflow',
            status='pending',
            requester=self.user,
            solution_name='test_solution',
            request_data={'workflow_id': 123}
        )
        
        self.assertEqual(approval_request.title, 'Test Approval Request')
        self.assertEqual(approval_request.approval_type, 'workflow')
        self.assertEqual(approval_request.status, 'pending')
        self.assertEqual(approval_request.requester, self.user)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_approval_response_model(self):
        """Test ApprovalResponse model creation."""
        approval_request = ApprovalRequest.objects.create(
            title='Test Approval Request',
            description='This is a test approval request',
            approval_type='workflow',
            status='pending',
            requester=self.user,
            solution_name='test_solution',
            request_data={'workflow_id': 123}
        )
        
        approval_response = ApprovalResponse.objects.create(
            approval_request=approval_request,
            responder=self.user,
            response='approve',
            comments='Looks good'
        )
        
        self.assertEqual(approval_response.approval_request, approval_request)
        self.assertEqual(approval_response.responder, self.user)
        self.assertEqual(approval_response.response, 'approve')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_notification_model(self):
        """Test Notification model creation."""
        notification = Notification.objects.create(
            title='Test Notification',
            message='This is a test notification',
            notification_type='info',
            priority='medium',
            user=self.user,
            solution_name='test_solution'
        )
        
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.notification_type, 'info')
        self.assertEqual(notification.priority, 'medium')
        self.assertEqual(notification.user, self.user)
        self.assertFalse(notification.is_read)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_handshake_model(self):
        """Test Handshake model creation."""
        from datetime import datetime, timedelta
        
        handshake = Handshake.objects.create(
            handshake_id='handshake_123',
            solution_name='acme_corp',
            secret_key='secret_key_456',
            status='pending',
            expires_at=datetime.now() + timedelta(hours=24)
        )
        
        self.assertEqual(handshake.handshake_id, 'handshake_123')
        self.assertEqual(handshake.solution_name, 'acme_corp')
        self.assertEqual(handshake.secret_key, 'secret_key_456')
        self.assertEqual(handshake.status, 'pending')
        self.assertIsNotNone(handshake.expires_at)
        self.assertIsNotNone(handshake.created_at)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_cache_entry_model(self):
        """Test CacheEntry model creation."""
        cache_entry = CacheEntry.objects.create(
            key='test_cache_key',
            value='test_cache_value',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        self.assertEqual(cache_entry.key, 'test_cache_key')
        self.assertEqual(cache_entry.value, 'test_cache_value')
        self.assertGreater(cache_entry.expires_at, timezone.now())
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_custom_field_model(self):
        """Test CustomField model creation."""
        custom_field = CustomField.objects.create(
            model_name='Customer',
            record_id=123,
            field_name='preferred_contact_method',
            field_type='choice',
            field_value='email',
            database_name='acme_db',
            solution_name='acme_corp',
            is_active=True
        )
        
        self.assertEqual(custom_field.model_name, 'Customer')
        self.assertEqual(custom_field.record_id, 123)
        self.assertEqual(custom_field.field_name, 'preferred_contact_method')
        self.assertEqual(custom_field.field_type, 'choice')
        self.assertEqual(custom_field.field_value, 'email')
        self.assertEqual(custom_field.database_name, 'acme_db')
        self.assertEqual(custom_field.solution_name, 'acme_corp')
        self.assertTrue(custom_field.is_active)


class TestFBSAppMSMEModels(TestCase):
    """Test FBS Core App MSME models."""
    
    databases = {'default'}
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_msme_setup_wizard_model(self):
        """Test MSMESetupWizard model creation."""
        setup_wizard = MSMESetupWizard.objects.create(
            solution_name='test_solution',
            status='in_progress',
            current_step='business_setup',
            total_steps=5,
            progress=20.0,
            business_type='retail',
            configuration={'employees': 50, 'revenue': 1000000}
        )
        
        self.assertEqual(setup_wizard.solution_name, 'test_solution')
        self.assertEqual(setup_wizard.status, 'in_progress')
        self.assertEqual(setup_wizard.current_step, 'business_setup')
        self.assertEqual(setup_wizard.total_steps, 5)
        self.assertEqual(setup_wizard.progress, 20.0)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_msme_kpi_model(self):
        """Test MSMEKPI model creation."""
        kpi = MSMEKPI.objects.create(
            solution_name='test_solution',
            kpi_name='Revenue Growth',
            kpi_type='financial',
            current_value=12.5,
            target_value=15.0,
            unit='percentage',
            period='monthly',
            trend='up'
        )
        
        self.assertEqual(kpi.solution_name, 'test_solution')
        self.assertEqual(kpi.kpi_name, 'Revenue Growth')
        self.assertEqual(kpi.kpi_type, 'financial')
        self.assertEqual(kpi.current_value, 12.5)
        self.assertEqual(kpi.target_value, 15.0)
        self.assertEqual(kpi.unit, 'percentage')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_msme_analytics_model(self):
        """Test MSMEAnalytics model creation."""
        from datetime import date
        
        analytics = MSMEAnalytics.objects.create(
            solution_name='test_solution',
            metric_name='customer_satisfaction',
            metric_value=4.5,
            metric_type='rating',
            period='monthly',
            date=date(2024, 1, 15),
            context={'source': 'survey'}
        )
        
        self.assertEqual(analytics.solution_name, 'test_solution')
        self.assertEqual(analytics.metric_name, 'customer_satisfaction')
        self.assertEqual(analytics.metric_value, 4.5)
        self.assertEqual(analytics.metric_type, 'rating')
        self.assertEqual(analytics.date, date(2024, 1, 15))
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_msme_compliance_model(self):
        """Test MSMECompliance model creation."""
        compliance = MSMECompliance.objects.create(
            solution_name='test_solution',
            compliance_type='tax',
            status='compliant',
            due_date='2024-04-15',
            requirements=['filing', 'payment'],
            documents=['tax_return.pdf'],
            notes='All requirements met'
        )
        
        self.assertEqual(compliance.solution_name, 'test_solution')
        self.assertEqual(compliance.compliance_type, 'tax')
        self.assertEqual(compliance.status, 'compliant')
        self.assertEqual(compliance.due_date, '2024-04-15')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_msme_marketing_model(self):
        """Test MSMEMarketing model creation."""
        marketing = MSMEMarketing.objects.create(
            solution_name='test_solution',
            campaign_name='Q1 Campaign',
            campaign_type='promotional',
            budget=50000,
            start_date='2024-01-01',
            end_date='2024-03-31',
            status='active'
        )
        
        self.assertEqual(marketing.solution_name, 'test_solution')
        self.assertEqual(marketing.campaign_name, 'Q1 Campaign')
        self.assertEqual(marketing.campaign_type, 'promotional')
        self.assertEqual(marketing.budget, 50000)
        self.assertEqual(marketing.start_date, '2024-01-01')
        self.assertEqual(marketing.end_date, '2024-03-31')
        self.assertEqual(marketing.status, 'active')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_msme_template_model(self):
        """Test MSMETemplate model creation."""
        template = MSMETemplate.objects.create(
            name='Retail Business Template',
            business_type='retail',
            description='Standard template for retail businesses',
            configuration={'inventory': True, 'pos': True, 'customer_management': True},
            is_active=True
        )
        
        self.assertEqual(template.name, 'Retail Business Template')
        self.assertEqual(template.business_type, 'retail')
        self.assertEqual(template.description, 'Standard template for retail businesses')
        self.assertEqual(template.configuration, {'inventory': True, 'pos': True, 'customer_management': True})
        self.assertTrue(template.is_active)


class TestFBSAppDiscoveryModels(TestCase):
    """Test FBS Core App Discovery models."""
    
    databases = {'default'}
    
    def setUp(self):
        """Set up test data."""
        pass
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_odoo_module_model(self):
        """Test OdooModule model creation."""
        module = OdooModule.objects.create(
            technical_name='sale',
            display_name='Sales',
            version='16.0',
            is_installed=True
        )
        
        self.assertEqual(module.technical_name, 'sale')
        self.assertEqual(module.display_name, 'Sales')
        self.assertEqual(module.version, '16.0')
        self.assertTrue(module.is_installed)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_odoo_model_model(self):
        """Test OdooModel model creation."""
        model = OdooModel.objects.create(
            database_name='test_db',
            model_name='res.partner',
            technical_name='res.partner',
            display_name='Contact',
            description='Business Partners and Contacts',
            module_name='base',
            is_active=True,
            is_installed=True,
            model_type='business',
            capabilities=['create', 'read', 'write', 'delete'],
            constraints={'required_fields': ['name']}
        )
        
        self.assertEqual(model.database_name, 'test_db')
        self.assertEqual(model.model_name, 'res.partner')
        self.assertEqual(model.technical_name, 'res.partner')
        self.assertEqual(model.display_name, 'Contact')
        self.assertEqual(model.module_name, 'base')
        self.assertEqual(model.model_type, 'business')
        self.assertTrue(model.is_active)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_odoo_field_model(self):
        """Test OdooField model creation."""
        # First create the OdooModel
        odoo_model = OdooModel.objects.create(
            database_name='test_db',
            model_name='res.partner',
            technical_name='res.partner',
            display_name='Contact',
            description='Business Partners and Contacts',
            module_name='base',
            is_active=True,
            is_installed=True,
            model_type='business',
            capabilities=['create', 'read', 'write', 'delete'],
            constraints={'required_fields': ['name']}
        )
        
        field = OdooField.objects.create(
            odoo_model=odoo_model,
            field_name='name',
            technical_name='name',
            display_name='Name',
            field_type='char',
            required=True,
            readonly=False,
            computed=False,
            stored=True,
            default_value='',
            help_text='Name of the partner',
            selection_options=[],
            relation_model='',
            field_constraints={'max_length': 128}
        )
        
        self.assertEqual(field.odoo_model, odoo_model)
        self.assertEqual(field.field_name, 'name')
        self.assertEqual(field.technical_name, 'name')
        self.assertEqual(field.display_name, 'Name')
        self.assertEqual(field.field_type, 'char')
        self.assertTrue(field.required)
        self.assertFalse(field.readonly)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_discovery_session_model(self):
        """Test DiscoverySession model creation."""
        session = DiscoverySession.objects.create(
            session_id='discovery_123',
            database_name='test_db',
            session_type='full',
            status='running',
            total_models=0,
            total_fields=0,
            total_modules=0,
            errors=[],
            configuration={'scan_depth': 'deep', 'include_custom': True}
        )
        
        self.assertEqual(session.session_id, 'discovery_123')
        self.assertEqual(session.database_name, 'test_db')
        self.assertEqual(session.session_type, 'full')
        self.assertEqual(session.status, 'running')
        self.assertEqual(session.total_models, 0)
        self.assertEqual(session.total_fields, 0)
        self.assertEqual(session.total_modules, 0)
        self.assertEqual(session.errors, [])
        self.assertEqual(session.configuration, {'scan_depth': 'deep', 'include_custom': True})


class TestFBSAppWorkflowModels(TestCase):
    """Test FBS Core App Workflow models."""
    
    databases = {'default'}
    
    def setUp(self):
        """Set up test data."""
        pass
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_workflow_definition_model(self):
        """Test WorkflowDefinition model creation."""
        workflow = WorkflowDefinition.objects.create(
            name='approval_workflow',
            description='Standard approval workflow',
            workflow_type='approval',
            version='1.0',
            trigger_conditions={'event': 'document_submitted'},
            workflow_data={'steps': ['submit', 'review', 'approve']},
            estimated_duration=24,
            is_active=True
        )
        
        self.assertEqual(workflow.name, 'approval_workflow')
        self.assertEqual(workflow.description, 'Standard approval workflow')
        self.assertEqual(workflow.workflow_type, 'approval')
        self.assertEqual(workflow.version, '1.0')
        self.assertEqual(workflow.estimated_duration, 24)
        self.assertTrue(workflow.is_active)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_workflow_instance_model(self):
        """Test WorkflowInstance model creation."""
        workflow_def = WorkflowDefinition.objects.create(
            name='approval_workflow',
            description='Standard approval workflow',
            workflow_type='approval',
            version='1.0',
            trigger_conditions={'event': 'document_submitted'},
            workflow_data={'steps': ['submit', 'review', 'approve']},
            estimated_duration=24,
            is_active=True
        )
        
        instance = WorkflowInstance.objects.create(
            workflow_definition=workflow_def,
            business_id='business_123',
            status='active',
            workflow_data={'request_id': '12345'},
            notes='Test workflow instance'
        )
        
        self.assertEqual(instance.workflow_definition, workflow_def)
        self.assertEqual(instance.business_id, 'business_123')
        self.assertEqual(instance.status, 'active')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_workflow_step_model(self):
        """Test WorkflowStep model creation."""
        workflow_def = WorkflowDefinition.objects.create(
            name='approval_workflow',
            description='Standard approval workflow',
            workflow_type='approval',
            version='1.0',
            trigger_conditions={'event': 'document_submitted'},
            workflow_data={'steps': ['submit', 'review', 'approve']},
            estimated_duration=24,
            is_active=True
        )
        
        step = WorkflowStep.objects.create(
            workflow_definition=workflow_def,
            name='review',
            step_type='approval',
            order=2,
            is_required=True,
            estimated_duration=4,
            assigned_role='manager',
            step_data={'approver_role': 'manager', 'timeout_hours': 24},
            conditions={'document_status': 'submitted'},
            actions=['send_notification', 'update_status']
        )
        
        self.assertEqual(step.workflow_definition, workflow_def)
        self.assertEqual(step.name, 'review')
        self.assertEqual(step.step_type, 'approval')
        self.assertEqual(step.order, 2)
        self.assertTrue(step.is_required)
        self.assertEqual(step.estimated_duration, 4)
        self.assertEqual(step.assigned_role, 'manager')
        self.assertEqual(step.step_data, {'approver_role': 'manager', 'timeout_hours': 24})
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_workflow_transition_model(self):
        """Test WorkflowTransition model creation."""
        workflow_def = WorkflowDefinition.objects.create(
            name='approval_workflow',
            description='Standard approval workflow',
            workflow_type='approval',
            version='1.0',
            trigger_conditions={'event': 'document_submitted'},
            workflow_data={'steps': ['submit', 'review', 'approve']},
            estimated_duration=24,
            is_active=True
        )
        
        # Create the steps first
        from_step = WorkflowStep.objects.create(
            workflow_definition=workflow_def,
            name='submit',
            step_type='task',
            order=1,
            is_required=True,
            step_data={'form_fields': ['title', 'description']},
            conditions={},
            actions=[]
        )
        
        to_step = WorkflowStep.objects.create(
            workflow_definition=workflow_def,
            name='review',
            step_type='approval',
            order=2,
            is_required=True,
            step_data={'approver_role': 'manager'},
            conditions={},
            actions=[]
        )
        
        transition = WorkflowTransition.objects.create(
            workflow_definition=workflow_def,
            from_step=from_step,
            to_step=to_step,
            transition_type='automatic',
            conditions={'status': 'submitted'},
            actions=['update_status'],
            is_default=True
        )
        
        self.assertEqual(transition.workflow_definition, workflow_def)
        self.assertEqual(transition.from_step, from_step)
        self.assertEqual(transition.to_step, to_step)
        self.assertEqual(transition.transition_type, 'automatic')
        self.assertTrue(transition.is_default)


class TestFBSAppBIModels(TestCase):
    """Test FBS Core App BI models."""
    
    databases = {'default'}
    
    def setUp(self):
        """Set up test data."""
        pass
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_kpi_model(self):
        """Test KPI model creation."""
        kpi = KPI.objects.create(
            name='revenue_growth',
            description='Monthly revenue growth percentage',
            kpi_type='financial',
            calculation_method='percentage_change',
            data_source='sales_data',
            target_value=15.0,
            warning_threshold=10.0,
            critical_threshold=5.0,
            unit='percentage',
            frequency='monthly',
            is_active=True
        )
        
        self.assertEqual(kpi.name, 'revenue_growth')
        self.assertEqual(kpi.description, 'Monthly revenue growth percentage')
        self.assertEqual(kpi.kpi_type, 'financial')
        self.assertEqual(kpi.calculation_method, 'percentage_change')
        self.assertEqual(kpi.target_value, 15.0)
        self.assertEqual(kpi.unit, 'percentage')
        self.assertEqual(kpi.frequency, 'monthly')
        self.assertTrue(kpi.is_active)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_chart_model(self):
        """Test Chart model creation."""
        chart = Chart.objects.create(
            name='revenue_trend',
            chart_type='line',
            description='Revenue trend over time',
            data_source='sales_data',
            configuration={'x_axis': 'date', 'y_axis': 'revenue'},
            is_active=True
        )
        
        self.assertEqual(chart.name, 'revenue_trend')
        self.assertEqual(chart.chart_type, 'line')
        self.assertEqual(chart.description, 'Revenue trend over time')
        self.assertEqual(chart.data_source, 'sales_data')
        self.assertEqual(chart.configuration, {'x_axis': 'date', 'y_axis': 'revenue'})
        self.assertTrue(chart.is_active)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_report_model(self):
        """Test Report model creation."""
        report = Report.objects.create(
            name='monthly_sales',
            description='Monthly sales report',
            report_type='sales',
            data_source='sales_data',
            query_parameters={'month': '2024-01'},
            output_format='pdf',
            template='Monthly sales template',
            is_scheduled=True,
            is_active=True
        )
        
        self.assertEqual(report.name, 'monthly_sales')
        self.assertEqual(report.description, 'Monthly sales report')
        self.assertEqual(report.report_type, 'sales')
        self.assertEqual(report.data_source, 'sales_data')
        self.assertEqual(report.output_format, 'pdf')
        self.assertTrue(report.is_scheduled)
        self.assertTrue(report.is_active)


class TestFBSAppComplianceModels(TestCase):
    """Test FBS Core App Compliance models."""
    
    databases = {'default'}
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_compliance_rule_model(self):
        """Test ComplianceRule model creation."""
        rule = ComplianceRule.objects.create(
            solution_name='acme_corp',
            name='tax_filing',
            description='Monthly tax filing requirement',
            compliance_type='tax',
            requirements=['file_monthly_return', 'pay_taxes'],
            check_frequency='monthly',
            active=True
        )
        
        self.assertEqual(rule.solution_name, 'acme_corp')
        self.assertEqual(rule.name, 'tax_filing')
        self.assertEqual(rule.description, 'Monthly tax filing requirement')
        self.assertEqual(rule.compliance_type, 'tax')
        self.assertEqual(rule.requirements, ['file_monthly_return', 'pay_taxes'])
        self.assertEqual(rule.check_frequency, 'monthly')
        self.assertTrue(rule.active)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_audit_trail_model(self):
        """Test AuditTrail model creation."""
        audit = AuditTrail.objects.create(
            solution_name='acme_corp',
            record_type='sale',
            record_id='sale_123',
            action='create',
            user_id='user_456',
            details={'amount': 1000, 'customer': 'John Doe'},
            ip_address='192.168.1.1'
        )
        
        self.assertEqual(audit.solution_name, 'acme_corp')
        self.assertEqual(audit.record_type, 'sale')
        self.assertEqual(audit.record_id, 'sale_123')
        self.assertEqual(audit.action, 'create')
        self.assertEqual(audit.user_id, 'user_456')
        self.assertEqual(audit.details, {'amount': 1000, 'customer': 'John Doe'})
        self.assertEqual(audit.ip_address, '192.168.1.1')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_report_schedule_model(self):
        """Test ReportSchedule model creation."""
        from datetime import datetime, timedelta
        
        schedule = ReportSchedule.objects.create(
            solution_name='acme_corp',
            name='monthly_sales_report',
            report_type='sales',
            frequency='monthly',
            next_run=datetime.now() + timedelta(days=30),
            active=True,
            configuration={'format': 'pdf', 'recipients': ['manager@acme.com']}
        )
        
        self.assertEqual(schedule.solution_name, 'acme_corp')
        self.assertEqual(schedule.name, 'monthly_sales_report')
        self.assertEqual(schedule.report_type, 'sales')
        self.assertEqual(schedule.frequency, 'monthly')
        self.assertTrue(schedule.active)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_recurring_transaction_model(self):
        """Test RecurringTransaction model creation."""
        from datetime import date
        
        transaction = RecurringTransaction.objects.create(
            solution_name='acme_corp',
            name='monthly_rent',
            transaction_type='expense',
            amount=2000.00,
            frequency='monthly',
            start_date=date(2024, 1, 1),
            description='Monthly office rent payment',
            active=True
        )
        
        self.assertEqual(transaction.solution_name, 'acme_corp')
        self.assertEqual(transaction.name, 'monthly_rent')
        self.assertEqual(transaction.transaction_type, 'expense')
        self.assertEqual(transaction.amount, 2000.00)
        self.assertEqual(transaction.frequency, 'monthly')
        self.assertEqual(transaction.start_date, date(2024, 1, 1))
        self.assertTrue(transaction.active)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_user_activity_log_model(self):
        """Test UserActivityLog model creation."""
        log = UserActivityLog.objects.create(
            solution_name='acme_corp',
            user_id='user_123',
            action='login',
            details={'method': 'password', 'success': True},
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            session_id='session_789'
        )
        
        self.assertEqual(log.solution_name, 'acme_corp')
        self.assertEqual(log.user_id, 'user_123')
        self.assertEqual(log.action, 'login')
        self.assertEqual(log.details, {'method': 'password', 'success': True})
        self.assertEqual(log.ip_address, '192.168.1.100')
        self.assertEqual(log.session_id, 'session_789')


class TestFBSAppAccountingModels(TestCase):
    """Test FBS Core App Accounting models."""
    
    databases = {'default'}
    
    def setUp(self):
        """Set up test data."""
        pass
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_basic_ledger_model(self):
        """Test BasicLedger model creation."""
        from datetime import date
        
        ledger = BasicLedger.objects.create(
            business_id='acme_corp',
            entry_date=date(2024, 1, 15),
            account='Cash',
            account_type='asset',
            debit_amount=1000.00,
            credit_amount=0.00,
            description='Initial cash deposit',
            reference='INIT-001',
            reference_type='initial',
            balance=1000.00
        )
        
        self.assertEqual(ledger.business_id, 'acme_corp')
        self.assertEqual(ledger.entry_date, date(2024, 1, 15))
        self.assertEqual(ledger.account, 'Cash')
        self.assertEqual(ledger.account_type, 'asset')
        self.assertEqual(ledger.debit_amount, 1000.00)
        self.assertEqual(ledger.credit_amount, 0.00)
        self.assertEqual(ledger.description, 'Initial cash deposit')
        self.assertEqual(ledger.balance, 1000.00)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_cash_entry_model(self):
        """Test CashEntry model creation."""
        from datetime import date
        
        entry = CashEntry.objects.create(
            business_id='acme_corp',
            entry_date=date(2024, 1, 15),
            entry_type='income',
            amount=1000.00,
            description='Service payment',
            category='Services',
            subcategory='Consulting',
            payment_method='bank_transfer',
            reference_number='INV-001',
            vendor_customer='Client ABC',
            tax_amount=100.00,
            tax_rate=10.00,
            notes='Monthly consulting services'
        )
        
        self.assertEqual(entry.business_id, 'acme_corp')
        self.assertEqual(entry.entry_date, date(2024, 1, 15))
        self.assertEqual(entry.entry_type, 'income')
        self.assertEqual(entry.amount, 1000.00)
        self.assertEqual(entry.description, 'Service payment')
        self.assertEqual(entry.category, 'Services')
        self.assertEqual(entry.payment_method, 'bank_transfer')
        self.assertEqual(entry.tax_amount, 100.00)
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_income_expense_model(self):
        """Test IncomeExpense model creation."""
        from datetime import date
        
        transaction = IncomeExpense.objects.create(
            business_id='acme_corp',
            transaction_date=date(2024, 1, 15),
            transaction_type='income',
            amount=1000.00,
            description='Service payment',
            category='Services',
            subcategory='Consulting',
            account='Accounts Receivable',
            invoice_number='INV-001',
            vendor_customer='Client ABC',
            payment_terms='Net 30',
            due_date=date(2024, 2, 14),
            payment_status='pending',
            tax_amount=100.00,
            tax_rate=10.00,
            notes='Monthly consulting services'
        )
        
        self.assertEqual(transaction.business_id, 'acme_corp')
        self.assertEqual(transaction.transaction_date, date(2024, 1, 15))
        self.assertEqual(transaction.transaction_type, 'income')
        self.assertEqual(transaction.amount, 1000.00)
        self.assertEqual(transaction.description, 'Service payment')
        self.assertEqual(transaction.category, 'Services')
        self.assertEqual(transaction.account, 'Accounts Receivable')
        self.assertEqual(transaction.payment_status, 'pending')
    
    @pytest.mark.unit
    @pytest.mark.fbs_app
    def test_tax_calculation_model(self):
        """Test TaxCalculation model creation."""
        from datetime import date
        
        tax = TaxCalculation.objects.create(
            business_id='acme_corp',
            tax_period_start=date(2024, 1, 1),
            tax_period_end=date(2024, 1, 31),
            tax_type='income_tax',
            taxable_amount=10000.00,
            tax_rate=15.00,
            tax_amount=1500.00,
            deductions=1000.00,
            net_tax_amount=500.00,
            due_date=date(2024, 4, 15),
            notes='Q1 income tax calculation'
        )
        
        self.assertEqual(tax.business_id, 'acme_corp')
        self.assertEqual(tax.tax_period_start, date(2024, 1, 1))
        self.assertEqual(tax.tax_period_end, date(2024, 1, 31))
        self.assertEqual(tax.tax_type, 'income_tax')
        self.assertEqual(tax.taxable_amount, 10000.00)
        self.assertEqual(tax.tax_rate, 15.00)
        self.assertEqual(tax.net_tax_amount, 500.00)
        self.assertEqual(tax.due_date, date(2024, 4, 15))
