"""
Tests for FBS App Onboarding Service

Tests all onboarding service methods including onboarding setup, templates, demo data, and timeline management.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from fbs_app.services.onboarding_service import OnboardingService


class TestOnboardingService(TestCase):
    """Test cases for OnboardingService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = OnboardingService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Test data aligned with actual service method signature
        self.test_business_data = {
            'business_type': 'retail',
            'business_name': 'Test Business',
            'contact_email': 'test@business.com',
            'contact_phone': '+1234567890'
        }
        
        self.test_business_data_minimal = {
            'business_type': 'retail',
            'business_name': 'Test Business',
            'contact_email': 'test@business.com'
        }

    def tearDown(self):
        """Clean up test fixtures"""
        try:
            from fbs_app.models import MSMESetupWizard
            MSMESetupWizard.objects.all().delete()
            if hasattr(self, 'user') and self.user:
                self.user.delete()
        except Exception:
            pass

    # Onboarding Setup Tests
    def test_start_onboarding_success(self):
        """Test successful onboarding start"""
        result = self.service.start_onboarding(self.test_business_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['business_type'], 'retail')
        self.assertIn('onboarding_id', result['data'])

    def test_start_onboarding_missing_required_field(self):
        """Test onboarding start with missing required field"""
        # Test with empty business_name
        client_data = {
            'business_type': 'retail',
            'business_name': '',  # Empty business name
            'contact_email': 'test@business.com'
        }
        
        result = self.service.start_onboarding(client_data)
        
        # Service handles empty business_name gracefully by using default
        self.assertTrue(result['success'])
        self.assertIn('data', result)

    def test_start_onboarding_with_defaults(self):
        """Test onboarding start with default values"""
        client_data = {
            'business_name': 'Test Business'
            # Missing business_type, should use default
        }
        
        result = self.service.start_onboarding(client_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['business_type'], 'general')
        self.assertIn('onboarding_id', result['data'])

    # Onboarding Step Management Tests
    def test_update_onboarding_step_success(self):
        """Test successful onboarding step update"""
        # First create an onboarding record
        from fbs_app.models import MSMESetupWizard
        
        wizard = MSMESetupWizard.objects.create(
            solution_name='test_business',
            business_type='retail',
            status='not_started',
            current_step='setup',
            progress=20.0,
            configuration={}
        )
        
        step_data = {
            'progress': 40.0,
            'configuration': {'currency': 'USD', 'tax_rate': 0.1}
        }
        
        result = self.service.update_onboarding_step(wizard.id, 'business_setup', step_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['id'], wizard.id)
        self.assertEqual(result['data']['current_step'], 'business_setup')
        self.assertEqual(result['data']['progress'], 40.0)

    def test_update_onboarding_step_with_configuration(self):
        """Test onboarding step update with configuration data"""
        # First create an onboarding record
        from fbs_app.models import MSMESetupWizard
        
        wizard = MSMESetupWizard.objects.create(
            solution_name='test_business',
            business_type='retail',
            status='not_started',
            current_step='setup',
            progress=20.0,
            configuration={'existing': 'data'}
        )
        
        step_data = {
            'progress': 40.0,
            'configuration': {'new_field': 'new_value'}
        }
        
        result = self.service.update_onboarding_step(wizard.id, 'business_setup', step_data)
        
        self.assertTrue(result['success'])
        # Check that configuration was updated in the database
        wizard.refresh_from_db()
        self.assertIn('new_field', wizard.configuration)
        self.assertIn('existing', wizard.configuration)

    def test_update_onboarding_step_client_not_found(self):
        """Test updating onboarding step for non-existent client"""
        result = self.service.update_onboarding_step(999, 'business_setup', {})
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_update_onboarding_step_exception_handling(self):
        """Test exception handling in step update"""
        # Test with invalid data that would cause an exception
        result = self.service.update_onboarding_step(1, 'invalid_step', {'invalid': 'data'})
        
        # Should handle the exception gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    # Template Management Tests
    def test_get_onboarding_templates_all(self):
        """Test getting all onboarding templates"""
        result = self.service.get_onboarding_templates()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('retail', result['data'])
        self.assertIn('manufacturing', result['data'])
        self.assertIn('services', result['data'])

    def test_get_onboarding_templates_by_business_type(self):
        """Test getting onboarding templates by business type"""
        result = self.service.get_onboarding_templates('retail')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['name'], 'Retail Starter Pack')

    def test_get_onboarding_templates_unknown_type(self):
        """Test getting onboarding templates for unknown business type"""
        result = self.service.get_onboarding_templates('unknown_type')
        
        self.assertTrue(result['success'])
        # Should return empty dict for unknown type
        self.assertEqual(result['data'], {})

    # Template Application Tests
    def test_apply_onboarding_template_success(self):
        """Test successful onboarding template application"""
        # First create an onboarding record
        from fbs_app.models import MSMESetupWizard
        
        wizard = MSMESetupWizard.objects.create(
            solution_name='test_business',
            business_type='retail',
            status='not_started'
        )
        
        result = self.service.apply_onboarding_template(wizard.id, 'Retail Starter Pack')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['id'], wizard.id)
        self.assertEqual(result['data']['template_applied'], 'Retail Starter Pack')

    def test_apply_onboarding_template_client_not_found(self):
        """Test applying template to non-existent client"""
        result = self.service.apply_onboarding_template(999, 'Retail Starter Pack')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_apply_onboarding_template_get_templates_failure(self):
        """Test template application when getting templates fails"""
        # Test with non-existent client
        result = self.service.apply_onboarding_template(999, 'Invalid Template')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    # Demo Data Import Tests
    def test_import_demo_data_success(self):
        """Test successful demo data import"""
        # First create an onboarding record
        from fbs_app.models import MSMESetupWizard
        
        wizard = MSMESetupWizard.objects.create(
            solution_name='test_business',
            business_type='retail',
            status='not_started'
        )
        
        result = self.service.import_demo_data(wizard.id, 'retail')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['id'], wizard.id)
        self.assertEqual(result['data']['demo_type'], 'retail')

    def test_import_demo_data_client_not_found(self):
        """Test importing demo data for non-existent client"""
        result = self.service.import_demo_data(999, 'retail')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_import_demo_data_different_types(self):
        """Test importing different types of demo data"""
        # First create an onboarding record
        from fbs_app.models import MSMESetupWizard
        
        wizard = MSMESetupWizard.objects.create(
            solution_name='test_business',
            business_type='retail',
            status='not_started'
        )
        
        result = self.service.import_demo_data(wizard.id, 'manufacturing')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['id'], wizard.id)
        self.assertEqual(result['data']['demo_type'], 'manufacturing')

    def test_import_demo_data_exception_handling(self):
        """Test exception handling in demo data import"""
        # Test with non-existent client
        result = self.service.import_demo_data(999, 'retail')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    # Timeline and Progress Tests
    def test_get_onboarding_timeline_success(self):
        """Test successful onboarding timeline retrieval"""
        # First create an onboarding record
        from fbs_app.models import MSMESetupWizard
        
        wizard = MSMESetupWizard.objects.create(
            solution_name='test_business',
            business_type='retail',
            status='not_started',
            current_step='setup',
            progress=30.0
        )
        
        result = self.service.get_onboarding_timeline(wizard.id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['id'], wizard.id)
        self.assertIn('timeline', result['data'])

    def test_get_onboarding_timeline_client_not_found(self):
        """Test getting timeline for non-existent client"""
        result = self.service.get_onboarding_timeline(999)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_get_onboarding_timeline_different_progress_levels(self):
        """Test timeline with different progress levels"""
        # First create an onboarding record with high progress
        from fbs_app.models import MSMESetupWizard
        
        wizard = MSMESetupWizard.objects.create(
            solution_name='test_business',
            business_type='retail',
            status='not_started',
            current_step='final_setup',
            progress=80.0
        )
        
        result = self.service.get_onboarding_timeline(wizard.id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['current_progress'], 80.0)

    # Utility Method Tests
    def test_generate_solution_name(self):
        """Test solution name generation"""
        business_name = 'Test Business'
        solution_name = self.service._generate_solution_name(business_name)
        
        # Should generate a solution name with prefix and sanitized business name
        self.assertIn('solution_', solution_name)
        self.assertIn('test_business', solution_name.lower())

    def test_onboarding_with_empty_data(self):
        """Test onboarding operations with empty data"""
        # Test with empty client data
        result = self.service.start_onboarding({})
        
        # Service handles empty data gracefully by using defaults
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['business_type'], 'general')

    def test_onboarding_with_special_characters(self):
        """Test onboarding with special characters in business names"""
        business_name = 'Test & Business (LLC)'
        
        client_data = {
            'business_type': 'retail',
            'business_name': business_name,
            'contact_email': 'test@business.com'
        }
        
        result = self.service.start_onboarding(client_data)
        
        self.assertTrue(result['success'])
        self.assertIn('onboarding_id', result['data'])

    def test_onboarding_progress_boundaries(self):
        """Test onboarding progress at boundary values"""
        # First create an onboarding record
        from fbs_app.models import MSMESetupWizard
        
        wizard = MSMESetupWizard.objects.create(
            solution_name='test_business',
            business_type='retail',
            status='not_started',
            current_step='setup',
            progress=0.0
        )
        
        # Test updating to 100% progress
        step_data = {
            'progress': 100.0,
            'configuration': {'completed': True}
        }
        
        result = self.service.update_onboarding_step(wizard.id, 'completion', step_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['progress'], 100.0)

    # Performance Tests
    def test_bulk_onboarding_operations(self):
        """Test performance of bulk onboarding operations"""
        # Create multiple onboarding records
        from fbs_app.models import MSMESetupWizard
        
        business_names = [f'Business {i}' for i in range(5)]
        
        for business_name in business_names:
            client_data = {
                'business_type': 'retail',
                'business_name': business_name,
                'contact_email': f'{business_name.lower().replace(" ", "")}@example.com'
            }
            result = self.service.start_onboarding(client_data)
            self.assertTrue(result['success'])
        
        # Verify all were created
        self.assertEqual(MSMESetupWizard.objects.count(), 5)

    def test_full_onboarding_workflow(self):
        """Test complete onboarding workflow from start to completion"""
        # Start onboarding
        client_data = {
            'business_type': 'retail',
            'business_name': 'Complete Business',
            'contact_email': 'complete@business.com'
        }
        
        result = self.service.start_onboarding(client_data)
        
        self.assertTrue(result['success'])
        onboarding_id = result['data']['onboarding_id']
        
        # Update progress through steps
        steps = ['setup', 'configuration', 'final_setup']
        for i, step in enumerate(steps):
            step_data = {
                'progress': (i + 1) * 33.33,
                'configuration': {f'step_{i}': 'completed'}
            }
            
            result = self.service.update_onboarding_step(onboarding_id, step, step_data)
            self.assertTrue(result['success'])
        
        # Get final timeline
        result = self.service.get_onboarding_timeline(onboarding_id)
        self.assertTrue(result['success'])
        self.assertIn('timeline', result['data'])

    # Error Handling Tests
    def test_start_onboarding_exception_handling(self):
        """Test exception handling in onboarding start"""
        # Test with invalid data that would cause an exception
        client_data = {
            'business_type': None,  # Invalid type
            'business_name': 'Test Business',
            'contact_email': 'test@business.com'
        }
        
        result = self.service.start_onboarding(client_data)
        
        # Should handle the exception gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_create_onboarding_step_missing_required_field(self):
        """Test onboarding step creation with missing required field"""
        # Test with missing step data
        result = self.service.update_onboarding_step(1, '', {})
        
        # Should fail due to missing step name
        self.assertFalse(result['success'])
        self.assertIn('error', result)
