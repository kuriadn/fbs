"""
Tests for FBS App Workflow Service

Tests all workflow service methods including workflow definitions, instances, approvals, and analytics.
"""

import pytest
from unittest.mock import MagicMock
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from fbs_app.services.workflow_service import WorkflowService


class TestWorkflowService(TestCase):
    """Test cases for WorkflowService"""
    
    def setUp(self):
        """Set up test data"""
        self.service = WorkflowService(solution_name='test_solution')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.test_workflow_data = {
            'name': 'Test Workflow',
            'description': 'Test workflow description',
            'workflow_type': 'approval',
            'version': '1.0',
            'is_active': True,
            'workflow_data': {
                'steps': [
                    {'name': 'Step 1', 'action': 'review'},
                    {'name': 'Step 2', 'action': 'approve'}
                ]
            }
        }
    
    def test_create_workflow_definition_success(self):
        """Test successful workflow definition creation"""
        result = self.service.create_workflow_definition(self.test_workflow_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['name'], self.test_workflow_data['name'])
        self.assertEqual(result['data']['workflow_type'], self.test_workflow_data['workflow_type'])
    
    def test_create_workflow_definition_missing_required_field(self):
        """Test workflow definition creation with missing required field"""
        incomplete_data = {'description': 'Missing name field'}
        result = self.service.create_workflow_definition(incomplete_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_get_workflow_definitions_all(self):
        """Test getting all workflow definitions"""
        # Create a workflow first
        self.service.create_workflow_definition(self.test_workflow_data)
        
        result = self.service.get_workflow_definitions()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
    
    def test_get_workflow_definitions_by_type(self):
        """Test getting workflow definitions by type"""
        # Create a workflow first
        self.service.create_workflow_definition(self.test_workflow_data)
        
        result = self.service.get_workflow_definitions(workflow_type='approval')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertTrue(all(w['workflow_type'] == 'approval' for w in result['data']))
    
    def test_start_workflow_success(self):
        """Test successful workflow start"""
        # Create a workflow definition first
        create_result = self.service.create_workflow_definition(self.test_workflow_data)
        workflow_id = create_result['data']['id']
        
        initial_data = {
            'business_id': 'test_business',
            'workflow_data': {'document_id': 123}
        }
        
        result = self.service.start_workflow(workflow_id, initial_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_start_workflow_definition_not_found(self):
        """Test starting workflow with non-existent definition"""
        initial_data = {'business_id': 'test_business'}
        
        result = self.service.start_workflow(99999, initial_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_get_active_workflows_all(self):
        """Test getting all active workflows"""
        # Create and start a workflow first
        create_result = self.service.create_workflow_definition(self.test_workflow_data)
        workflow_id = create_result['data']['id']
        self.service.start_workflow(workflow_id, {'business_id': 'test_business'})
        
        result = self.service.get_active_workflows()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
    
    def test_get_active_workflows_by_user(self):
        """Test getting active workflows for specific user"""
        # Create and start a workflow first
        create_result = self.service.create_workflow_definition(self.test_workflow_data)
        workflow_id = create_result['data']['id']
        self.service.start_workflow(workflow_id, {'business_id': 'test_business'})
        
        result = self.service.get_active_workflows(user_id=self.user.id)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_execute_workflow_step_success(self):
        """Test successful workflow step execution"""
        # Create and start a workflow first
        create_result = self.service.create_workflow_definition(self.test_workflow_data)
        workflow_id = create_result['data']['id']
        start_result = self.service.start_workflow(workflow_id, {'business_id': 'test_business'})
        instance_id = start_result['data']['instance']['id']
        
        step_data = {
            'step_name': 'Step 1',
            'action': 'complete',
            'user': self.user
        }
        
        result = self.service.execute_workflow_step(instance_id, step_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_execute_workflow_step_instance_not_found(self):
        """Test executing step on non-existent workflow instance"""
        step_data = {
            'step_name': 'Step 1',
            'action': 'complete'
        }
        
        result = self.service.execute_workflow_step(99999, step_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_create_approval_request_success(self):
        """Test successful approval request creation"""
        approval_data = {
            'title': 'Test Approval',
            'description': 'Test approval request',
            'requester_id': self.user.id,
            'approver_id': self.user.id,
            'priority': 'medium'
        }
        
        result = self.service.create_approval_request(approval_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['title'], approval_data['title'])
    
    def test_get_approval_requests_all(self):
        """Test getting all approval requests"""
        # Create an approval request first
        self.service.create_approval_request({
            'title': 'Test Approval',
            'description': 'Test approval request',
            'requester_id': self.user.id,
            'approver_id': self.user.id
        })
        
        result = self.service.get_approval_requests()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
    
    def test_get_approval_requests_by_status(self):
        """Test getting approval requests by status"""
        # Create an approval request first
        self.service.create_approval_request({
            'title': 'Test Approval',
            'description': 'Test approval request',
            'requester_id': self.user.id,
            'approver_id': self.user.id
        })
        
        result = self.service.get_approval_requests(status='pending')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertTrue(all(r['status'] == 'pending' for r in result['data']))
    
    def test_get_approval_requests_by_user(self):
        """Test getting approval requests by user"""
        # Create an approval request first
        self.service.create_approval_request({
            'title': 'Test Approval',
            'description': 'Test approval request',
            'requester_id': self.user.id,
            'approver_id': self.user.id
        })
        
        result = self.service.get_approval_requests(user_id=self.user.id)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertTrue(all(r['requester_id'] == self.user.id for r in result['data']))
    
    def test_respond_to_approval_approve(self):
        """Test approving an approval request"""
        # Create an approval request first
        create_result = self.service.create_approval_request({
            'title': 'Test Approval',
            'description': 'Test approval request',
            'requester_id': self.user.id,
            'approver_id': self.user.id
        })
        approval_id = create_result['data']['id']
        
        result = self.service.respond_to_approval(approval_id, 'approve', 'Approved')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_respond_to_approval_reject(self):
        """Test rejecting an approval request"""
        # Create an approval request first
        create_result = self.service.create_approval_request({
            'title': 'Test Approval',
            'description': 'Test approval request',
            'requester_id': self.user.id,
            'approver_id': self.user.id
        })
        approval_id = create_result['data']['id']
        
        result = self.service.respond_to_approval(approval_id, 'reject', 'Rejected')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_respond_to_approval_not_found(self):
        """Test responding to non-existent approval request"""
        result = self.service.respond_to_approval(99999, 'approve', 'Approved')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_get_workflow_analytics_all(self):
        """Test getting workflow analytics for all types"""
        # Create and start some workflows first
        create_result = self.service.create_workflow_definition(self.test_workflow_data)
        workflow_id = create_result['data']['id']
        self.service.start_workflow(workflow_id, {'business_id': 'test_business'})
        
        result = self.service.get_workflow_analytics()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_get_workflow_analytics_by_type(self):
        """Test getting workflow analytics by type"""
        # Create and start some workflows first
        create_result = self.service.create_workflow_definition(self.test_workflow_data)
        workflow_id = create_result['data']['id']
        self.service.start_workflow(workflow_id, {'business_id': 'test_business'})
        
        result = self.service.get_workflow_analytics(workflow_type='approval')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_create_workflow_definition_exception_handling(self):
        """Test exception handling in workflow definition creation"""
        # Test with invalid data that might cause exceptions
        invalid_data = {'name': None, 'workflow_type': 'invalid_type'}
        result = self.service.create_workflow_definition(invalid_data)
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_get_workflow_definitions_exception_handling(self):
        """Test exception handling in getting workflow definitions"""
        # Test with invalid parameters
        result = self.service.get_workflow_definitions(workflow_type='invalid_type')
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_bulk_workflow_operations(self):
        """Test performance of bulk workflow operations"""
        # Create multiple workflow definitions
        workflows = []
        for i in range(5):
            workflow_data = {
                'name': f'Bulk Workflow {i}',
                'description': f'Bulk workflow {i}',
                'workflow_type': 'approval',
                'version': '1.0',
                'workflow_data': {'steps': [{'name': 'Step 1', 'action': 'review'}]}
            }
            result = self.service.create_workflow_definition(workflow_data)
            if result['success']:
                workflows.append(result['data'])
        
        # Test bulk retrieval
        result = self.service.get_workflow_definitions()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreaterEqual(len(result['data']), len(workflows))
    
    def test_full_workflow_lifecycle(self):
        """Test complete workflow lifecycle from definition to completion"""
        # 1. Create workflow definition
        create_result = self.service.create_workflow_definition(self.test_workflow_data)
        self.assertTrue(create_result['success'])
        workflow_id = create_result['data']['id']
        
        # 2. Start workflow
        start_result = self.service.start_workflow(workflow_id, {'business_id': 'test_business'})
        self.assertTrue(start_result['success'])
        instance_id = start_result['data']['instance']['id']
        
        # 3. Execute steps
        step_result = self.service.execute_workflow_step(instance_id, {
            'step_name': 'Step 1',
            'action': 'complete',
            'user': self.user
        })
        self.assertTrue(step_result['success'])
        
        # 4. Check final state
        workflows = self.service.get_active_workflows()
        self.assertTrue(workflows['success'])
    
    def test_workflow_with_empty_data(self):
        """Test workflow operations with empty data"""
        result = self.service.create_workflow_definition({})
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_workflow_with_invalid_states(self):
        """Test workflow operations with invalid states"""
        # Test with invalid workflow type
        invalid_data = {
            'name': 'Invalid Workflow',
            'workflow_type': 'invalid_type'
        }
        
        result = self.service.create_workflow_definition(invalid_data)
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
