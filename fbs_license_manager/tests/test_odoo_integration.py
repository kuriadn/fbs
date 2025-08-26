"""
Test Odoo-Driven License Manager Integration

Tests the integration between License Manager and FBS virtual fields system.
"""

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json

from ..services import OdooLicenseService


class OdooLicenseIntegrationTestCase(TestCase):
    """Test case for Odoo-driven License Manager integration"""
    
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
            'data': {'id': 456}
        }
        self.mock_odoo.update_record.return_value = {
            'success': True,
            'data': {'id': 456}
        }
        self.mock_odoo.delete_record.return_value = {
            'success': True,
            'message': 'Deleted'
        }
        self.mock_odoo.get_record.return_value = {
            'success': True,
            'data': {
                'id': 456,
                'name': 'Test Company',
                'email': 'test@company.com',
                'is_company': True
            }
        }
        self.mock_odoo.get_records.return_value = {
            'success': True,
            'data': [
                {'id': 456, 'name': 'Company 1'},
                {'id': 789, 'name': 'Company 2'}
            ]
        }
        
        self.mock_virtual_fields.set_custom_field.return_value = {
            'success': True,
            'message': 'Field set'
        }
        
        # Mock virtual fields get_custom_fields method
        self.mock_virtual_fields.get_custom_fields.return_value = {
            'success': True,
            'data': {
                'license_key': 'TEST-LICENSE-123',
                'license_type': 'premium',
                'license_status': 'active',
                'expiry_date': '2024-12-31',
                'feature_flags': '{"msme": true, "bi": true, "dms": true}',
                'max_users': 100,
                'max_storage_gb': 1000,
                'api_rate_limit': 10000,
                'billing_cycle': 'monthly',
                'billing_amount': '99.99',
                'contact_person': 'John Doe'
            }
        }
        
        # Wire up the mocks
        self.mock_fbs_interface.odoo = self.mock_odoo
        self.mock_fbs_interface.fields = self.mock_virtual_fields
        
        # Create service with mocked interface
        self.odoo_license_service = OdooLicenseService(
            self.company_id, 
            self.mock_fbs_interface
        )
    
    def test_service_initialization(self):
        """Test that service initializes correctly"""
        self.assertEqual(self.odoo_license_service.company_id, self.company_id)
        self.assertIsNotNone(self.odoo_license_service.odoo_licenses)
        self.assertIsNotNone(self.odoo_license_service.virtual_fields)
    
    def test_create_license_success(self):
        """Test successful license creation with virtual fields"""
        license_data = {
            'company_name': 'Test Company',
            'email': 'test@company.com',
            'phone': '+1234567890',
            'address': {
                'street': '123 Test St',
                'city': 'Test City',
                'zip': '12345'
            },
            'license_key': 'TEST-LICENSE-123',
            'license_type': 'premium',
            'status': 'active',
            'expiry_date': datetime.now() + timedelta(days=365),
            'features': {
                'msme': True,
                'bi': True,
                'dms': True
            },
            'max_users': 100,
            'max_storage_gb': 1000,
            'api_rate_limit': 10000,
            'billing_cycle': 'monthly',
            'billing_amount': 99.99,
            'contact_person': 'John Doe'
        }
        
        result = self.odoo_license_service.create_license(license_data, self.user)
        
        # Verify success
        self.assertTrue(result['success'])
        self.assertEqual(result['odoo_id'], 456)
        
        # Verify Odoo company creation was called
        self.mock_odoo.create_record.assert_called_once()
        call_args = self.mock_odoo.create_record.call_args
        self.assertEqual(call_args[0][0], 'res.partner')  # model_name
        
        # Verify virtual fields were set (should be 11 fields based on test data)
        self.assertEqual(self.mock_virtual_fields.set_custom_field.call_count, 11)
    
    def test_create_license_no_odoo_integration(self):
        """Test license creation without Odoo integration"""
        service = OdooLicenseService(self.company_id, None)
        
        license_data = {'company_name': 'Test Company'}
        result = service.create_license(license_data, self.user)
        
        self.assertFalse(result['success'])
        self.assertIn('Odoo integration required', result['error'])
    
    def test_get_license_success(self):
        """Test successful license retrieval with virtual fields"""
        result = self.odoo_license_service.get_license(456)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['id'], 456)
        self.assertEqual(result['data']['name'], 'Test Company')
        
        # Verify features were parsed from JSON
        self.assertIn('features', result['data'])
        self.assertIsInstance(result['data']['features'], dict)
        self.assertTrue(result['data']['features']['msme'])
    
    def test_update_license_success(self):
        """Test successful license update"""
        update_data = {
            'name': 'Updated Company',
            'license_type': 'enterprise',
            'status': 'suspended',
            'max_users': 200
        }
        
        result = self.odoo_license_service.update_license(456, update_data)
        
        self.assertTrue(result['success'])
        
        # Verify Odoo update was called
        self.mock_odoo.update_record.assert_called_once()
        
        # Verify virtual fields were updated
        self.assertEqual(self.mock_virtual_fields.set_custom_field.call_count, 3)
    
    def test_delete_license_success(self):
        """Test successful license deletion"""
        result = self.odoo_license_service.delete_license(456)
        
        self.assertTrue(result['success'])
        self.mock_odoo.delete_record.assert_called_once_with('res.partner', 456)
    
    def test_search_licenses_success(self):
        """Test successful license search"""
        result = self.odoo_license_service.search_licenses({'company_name': 'Company'})
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        self.assertEqual(len(result['data']), 2)
        
        # Verify company filter was added
        self.mock_odoo.get_records.assert_called_once()
        call_args = self.mock_odoo.get_records.call_args
        domain = call_args[0][1]  # domain parameter
        self.assertIn(('is_company', '=', True), domain)
    
    def test_build_search_domain(self):
        """Test search domain building"""
        filters = {
            'company_name': 'Test',
            'email': 'test@example.com',
            'city': 'Test City',
            'country_id': 1
        }
        
        domain = self.odoo_license_service._build_search_domain(filters)
        
        # Should have 5 conditions (4 filters + is_company)
        self.assertEqual(len(domain), 5)
        
        # Check company filter is always added
        company_filter = domain[0]
        self.assertEqual(company_filter[0], 'is_company')
        self.assertEqual(company_filter[1], '=')
        self.assertEqual(company_filter[2], True)
    
    def test_check_feature_access_success(self):
        """Test successful feature access check"""
        result = self.odoo_license_service.check_feature_access(456, 'msme')
        
        self.assertTrue(result['success'])
        self.assertTrue(result['access'])
        self.assertIn('Feature msme access granted', result['message'])
    
    def test_check_feature_access_disabled(self):
        """Test feature access check for disabled feature"""
        # Mock a license without the feature enabled
        self.mock_virtual_fields.get_custom_fields.return_value = {
            'success': True,
            'data': {
                'feature_flags': '{"msme": false, "bi": true}'
            }
        }
        
        result = self.odoo_license_service.check_feature_access(456, 'msme')
        
        self.assertTrue(result['success'])
        self.assertFalse(result['access'])
        self.assertIn('Feature msme not enabled', result['message'])
    
    def test_check_feature_access_limit_reached(self):
        """Test feature access check when usage limit is reached"""
        # Mock a license with usage limit reached
        self.mock_virtual_fields.get_custom_fields.return_value = {
            'success': True,
            'data': {
                'feature_flags': '{"users": true}',
                'current_users': 100,
                'max_users': 100
            }
        }
        
        result = self.odoo_license_service.check_feature_access(456, 'users')
        
        self.assertTrue(result['success'])
        self.assertFalse(result['access'])
        self.assertIn('Feature users usage limit reached', result['message'])
        self.assertEqual(result['current'], 100)
        self.assertEqual(result['limit'], 100)
    
    def test_update_feature_usage_success(self):
        """Test successful feature usage update"""
        # Mock current usage
        self.mock_virtual_fields.get_custom_field.return_value = {
            'success': True,
            'data': {'value': 50}
        }
        
        result = self.odoo_license_service.update_feature_usage(456, 'users', 5)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['current_usage'], 5)
        self.assertIn('Updated users usage to 5', result['message'])
    
    def test_update_feature_usage_no_virtual_fields(self):
        """Test feature usage update without virtual fields"""
        service = OdooLicenseService(self.company_id, None)
        
        result = service.update_feature_usage(456, 'users', 5)
        
        self.assertFalse(result['success'])
        self.assertIn('Virtual fields not available', result['error'])
    
    def test_virtual_fields_error_handling(self):
        """Test that virtual field errors don't fail main operations"""
        # Make virtual fields fail
        self.mock_virtual_fields.set_custom_field.return_value = {
            'success': False,
            'error': 'Virtual field error'
        }
        
        license_data = {
            'company_name': 'Test Company',
            'license_type': 'premium'
        }
        
        # Should still succeed even if virtual fields fail
        result = self.odoo_license_service.create_license(license_data, self.user)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['odoo_id'], 456)
    
    def test_license_data_validation(self):
        """Test license data validation and processing"""
        license_data = {
            'company_name': 'Test Company',
            'features': {
                'msme': True,
                'bi': False,
                'dms': True
            },
            'max_users': 150,
            'expiry_date': datetime.now() + timedelta(days=180)
        }
        
        result = self.odoo_license_service.create_license(license_data, self.user)
        
        self.assertTrue(result['success'])
        
        # Verify features were properly encoded as JSON
        feature_calls = [
            call for call in self.mock_virtual_fields.set_custom_field.call_args_list
            if call[0][2] == 'feature_flags'  # field_name
        ]
        
        self.assertEqual(len(feature_calls), 1)
        feature_call = feature_calls[0]
        feature_json = feature_call[0][3]  # field_value
        
        # Parse JSON and verify content
        parsed_features = json.loads(feature_json)
        self.assertTrue(parsed_features['msme'])
        self.assertFalse(parsed_features['bi'])
        self.assertTrue(parsed_features['dms'])
    
    def test_address_handling(self):
        """Test address field handling in license creation"""
        license_data = {
            'company_name': 'Test Company',
            'address': {
                'street': '123 Main St',
                'city': 'Test City',
                'state_id': 5,
                'country_id': 1,
                'zip': '12345'
            }
        }
        
        result = self.odoo_license_service.create_license(license_data, self.user)
        
        self.assertTrue(result['success'])
        
        # Verify address fields were passed to Odoo
        odoo_call = self.mock_odoo.create_record.call_args
        odoo_data = odoo_call[0][1]  # data parameter
        
        self.assertEqual(odoo_data['street'], '123 Main St')
        self.assertEqual(odoo_data['city'], 'Test City')
        self.assertEqual(odoo_data['state_id'], 5)
        self.assertEqual(odoo_data['country_id'], 1)
        self.assertEqual(odoo_data['zip'], '12345')
    
    def test_company_creation_flags(self):
        """Test that company creation flags are set correctly"""
        license_data = {
            'company_name': 'Test Company'
        }
        
        result = self.odoo_license_service.create_license(license_data, self.user)
        
        self.assertTrue(result['success'])
        
        # Verify company flags were set
        odoo_call = self.mock_odoo.create_record.call_args
        odoo_data = odoo_call[0][1]  # data parameter
        
        self.assertTrue(odoo_data['is_company'])
        self.assertEqual(odoo_data['customer_rank'], 1)
        self.assertEqual(odoo_data['company_id'], self.company_id)
