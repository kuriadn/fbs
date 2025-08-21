"""
Tests for FBS App Compliance Service

Tests all compliance service methods including compliance rules, checking, audit trails, and reporting.
"""

import pytest
from unittest.mock import MagicMock
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from fbs_app.services.compliance_service import ComplianceService

class TestComplianceService(TestCase):
    """Test cases for ComplianceService"""
    
    def setUp(self):
        """Set up test data"""
        self.service = ComplianceService('test_solution')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.test_compliance_rule_data = {
            'name': 'Test Compliance Rule',
            'description': 'Test compliance rule description',
            'compliance_type': 'tax',
            'requirements': ['requirement1', 'requirement2'],
            'check_frequency': 'monthly',
            'active': True
        }
    
    def test_create_compliance_rule_success(self):
        """Test successful compliance rule creation"""
        result = self.service.create_compliance_rule(self.test_compliance_rule_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['name'], self.test_compliance_rule_data['name'])
        self.assertEqual(result['data']['compliance_type'], self.test_compliance_rule_data['compliance_type'])
    
    def test_create_compliance_rule_missing_required_field(self):
        """Test compliance rule creation with missing required field"""
        incomplete_data = {'description': 'Missing name field'}
        result = self.service.create_compliance_rule(incomplete_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_get_compliance_rules_all(self):
        """Test getting all compliance rules"""
        # Create a compliance rule first
        self.service.create_compliance_rule(self.test_compliance_rule_data)
        
        result = self.service.get_compliance_rules()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
    
    def test_get_compliance_rules_by_type(self):
        """Test getting compliance rules by type"""
        # Create a compliance rule first
        self.service.create_compliance_rule(self.test_compliance_rule_data)
        
        result = self.service.get_compliance_rules(compliance_type='tax')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertTrue(all(r['compliance_type'] == 'tax' for r in result['data']))
    
    def test_check_compliance_tax_success(self):
        """Test successful tax compliance check"""
        # Create a compliance rule first
        create_result = self.service.create_compliance_rule(self.test_compliance_rule_data)
        rule_id = create_result['data']['id']
        
        compliance_data = {'tax_amount': 1000, 'filing_date': '2024-01-15'}
        
        result = self.service.check_compliance(rule_id, compliance_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_check_compliance_payroll_success(self):
        """Test successful payroll compliance check"""
        # Create a compliance rule first
        payroll_rule_data = {
            'name': 'Payroll Compliance Rule',
            'description': 'Payroll compliance rule',
            'compliance_type': 'payroll',
            'requirements': ['requirement1'],
            'check_frequency': 'monthly',
            'active': True
        }
        create_result = self.service.create_compliance_rule(payroll_rule_data)
        rule_id = create_result['data']['id']
        
        compliance_data = {'employee_count': 10, 'payroll_date': '2024-01-31'}
        
        result = self.service.check_compliance(rule_id, compliance_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_check_compliance_rule_not_found(self):
        """Test compliance check with non-existent rule"""
        compliance_data = {'tax_amount': 1000}
        
        result = self.service.check_compliance(99999, compliance_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_check_compliance_unknown_type(self):
        """Test compliance check with unknown type"""
        # Create a compliance rule first
        create_result = self.service.create_compliance_rule(self.test_compliance_rule_data)
        rule_id = create_result['data']['id']
        
        compliance_data = {'some_data': 'value'}
        
        result = self.service.check_compliance(rule_id, compliance_data)
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_get_compliance_status_all(self):
        """Test getting overall compliance status"""
        # Create some compliance rules first
        self.service.create_compliance_rule(self.test_compliance_rule_data)
        self.service.create_compliance_rule({
            'name': 'Second Rule',
            'description': 'Second rule description',
            'compliance_type': 'payroll',
            'requirements': ['req1'],
            'check_frequency': 'monthly',
            'active': True
        })
        
        result = self.service.get_compliance_status()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_get_compliance_status_by_type(self):
        """Test getting compliance status by type"""
        # Create a compliance rule first
        self.service.create_compliance_rule(self.test_compliance_rule_data)
        
        result = self.service.get_compliance_status(compliance_type='tax')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_create_audit_trail_success(self):
        """Test successful audit trail creation"""
        audit_data = {
            'record_type': 'compliance_rule',
            'record_id': 1,
            'action': 'created',
            'user_id': str(self.user.id),
            'details': {'message': 'Rule created for testing'}
        }
        
        result = self.service.create_audit_trail(
            audit_data['record_type'],
            audit_data['record_id'],
            audit_data['action'],
            audit_data['user_id'],
            audit_data['details']
        )
        
        self.assertTrue(result['success'])
        self.assertIn('audit_id', result)
        self.assertIn('message', result)
        self.assertEqual(result['message'], 'Audit trail created successfully')
    
    def test_get_audit_trails_all(self):
        """Test getting all audit trails"""
        # Create an audit trail first
        self.service.create_audit_trail(
            'compliance_rule',
            1,
            'created',
            str(self.user.id),
            {'message': 'Test audit trail'}
        )
        
        result = self.service.get_audit_trails()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
    
    def test_get_audit_trails_by_entity_type(self):
        """Test getting audit trails by entity type"""
        # Create an audit trail first
        self.service.create_audit_trail(
            'compliance_rule',
            1,
            'created',
            str(self.user.id),
            {'message': 'Test audit trail'}
        )
        
        result = self.service.get_audit_trails(entity_type='compliance_rule')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertTrue(all(t['record_type'] == 'compliance_rule' for t in result['data']))
    
    def test_get_audit_trails_by_entity_id(self):
        """Test getting audit trails by entity ID"""
        # Create an audit trail first
        self.service.create_audit_trail(
            'compliance_rule',
            '123',  # record_id is a string in the model
            'created',
            str(self.user.id),
            {'message': 'Test audit trail'}
        )
        
        result = self.service.get_audit_trails(entity_id=123)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertTrue(all(t['record_id'] == '123' for t in result['data']))
    
    def test_generate_compliance_report_monthly(self):
        """Test generating monthly compliance report"""
        result = self.service.generate_compliance_report('monthly')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['report_type'], 'monthly')
    
    def test_generate_compliance_report_quarterly(self):
        """Test generating quarterly compliance report"""
        result = self.service.generate_compliance_report('quarterly')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['report_type'], 'quarterly')
    
    def test_generate_compliance_report_annual(self):
        """Test generating annual compliance report"""
        result = self.service.generate_compliance_report('annual')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['report_type'], 'annual')
    
    def test_generate_compliance_report_unknown_type(self):
        """Test generating compliance report with unknown type"""
        result = self.service.generate_compliance_report('unknown_type')
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_generate_monthly_compliance_report(self):
        """Test monthly compliance report generation"""
        result = self.service._generate_monthly_compliance_report({})
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_generate_quarterly_compliance_report(self):
        """Test quarterly compliance report generation"""
        result = self.service._generate_quarterly_compliance_report({})
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_generate_annual_compliance_report(self):
        """Test annual compliance report generation"""
        result = self.service._generate_annual_compliance_report({})
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_check_tax_compliance(self):
        """Test tax compliance check helper method"""
        result = self.service._check_tax_compliance({'tax_amount': 1000})
        
        # Should return boolean for helper methods
        self.assertIsInstance(result, bool)
    
    def test_check_payroll_compliance(self):
        """Test payroll compliance check helper method"""
        result = self.service._check_payroll_compliance({'employee_count': 10})
        
        # Should return boolean for helper methods
        self.assertIsInstance(result, bool)
    
    def test_create_compliance_rule_exception_handling(self):
        """Test exception handling in compliance rule creation"""
        # Test with invalid data that might cause exceptions
        invalid_data = {'name': None, 'compliance_type': 'invalid_type'}
        result = self.service.create_compliance_rule(invalid_data)
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_get_compliance_rules_exception_handling(self):
        """Test exception handling in getting compliance rules"""
        # Test with invalid parameters
        result = self.service.get_compliance_rules(compliance_type='invalid_type')
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_check_compliance_exception_handling(self):
        """Test exception handling in compliance checking"""
        # Test with invalid data that might cause exceptions
        invalid_data = {'tax_amount': 'invalid_type'}
        
        result = self.service.check_compliance(99999, invalid_data)
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_bulk_compliance_operations(self):
        """Test performance of bulk compliance operations"""
        # Create multiple compliance rules
        rules = []
        for i in range(5):
            rule_data = {
                'name': f'Bulk Rule {i}',
                'description': f'Bulk rule {i}',
                'compliance_type': 'tax',
                'requirements': [f'req{i}'],
                'check_frequency': 'monthly',
                'active': True
            }
            result = self.service.create_compliance_rule(rule_data)
            if result['success']:
                rules.append(result['data'])
        
        # Test bulk retrieval
        result = self.service.get_compliance_rules()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreaterEqual(len(result['data']), len(rules))
    
    def test_full_compliance_workflow(self):
        """Test complete compliance workflow from rule creation to reporting"""
        # 1. Create compliance rule
        create_result = self.service.create_compliance_rule(self.test_compliance_rule_data)
        self.assertTrue(create_result['success'])
        rule_id = create_result['data']['id']
        
        # 2. Check compliance
        check_result = self.service.check_compliance(rule_id, {'tax_amount': 1000})
        self.assertTrue(check_result['success'])
        
        # 3. Create audit trail
        audit_result = self.service.create_audit_trail(
            'compliance_rule',
            rule_id,
            'compliance_checked',
            str(self.user.id),
            {'result': 'compliant'}
        )
        self.assertTrue(audit_result['success'])
        
        # 4. Generate report
        report_result = self.service.generate_compliance_report('monthly')
        self.assertTrue(report_result['success'])
        
        # 5. Check final status
        status_result = self.service.get_compliance_status()
        self.assertTrue(status_result['success'])
    
    def test_compliance_with_empty_data(self):
        """Test compliance operations with empty data"""
        result = self.service.create_compliance_rule({})
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_compliance_with_invalid_types(self):
        """Test compliance operations with invalid types"""
        # Test with invalid compliance type
        invalid_data = {
            'name': 'Invalid Rule',
            'compliance_type': 'invalid_type'
        }
        
        result = self.service.create_compliance_rule(invalid_data)
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
