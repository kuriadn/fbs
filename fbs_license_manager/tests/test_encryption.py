"""
Tests for license key encryption functionality
"""

import pytest
from django.test import TestCase
from django.conf import settings
from ..models import LICSolutionLicense


class LicenseEncryptionTest(TestCase):
    """Test license key encryption and decryption"""
    
    databases = {'default', 'licensing'}
    
    def setUp(self):
        """Set up test data"""
        self.test_license_key = "TEST-LICENSE-KEY-12345"
        self.solution_name = "test_solution"
    
    def test_license_key_encryption(self):
        """Test that license keys are automatically encrypted"""
        # Create license with plain text key
        license_obj = LICSolutionLicense.objects.create(
            solution_name=self.solution_name,
            license_type='trial',
            license_key=self.test_license_key,
            features='[]',
            limits='{}'
        )
        
        # Verify key is encrypted in database
        self.assertNotEqual(license_obj.license_key, self.test_license_key)
        self.assertTrue(license_obj._is_encrypted(license_obj.license_key))
    
    def test_license_key_decryption(self):
        """Test that license keys can be decrypted"""
        # Create license with plain text key
        license_obj = LICSolutionLicense.objects.create(
            solution_name=self.solution_name,
            license_type='trial',
            license_key=self.test_license_key,
            features='[]',
            limits='{}'
        )
        
        # Verify decryption works
        decrypted_key = license_obj.get_decrypted_license_key()
        self.assertEqual(decrypted_key, self.test_license_key)
    
    def test_encryption_key_generation(self):
        """Test that encryption keys are generated if not provided"""
        # Clear any existing encryption key
        if hasattr(settings, 'FBS_LICENSE_ENCRYPTION_KEY'):
            delattr(settings, 'FBS_LICENSE_ENCRYPTION_KEY')
        
        # Create license - should generate key automatically
        license_obj = LICSolutionLicense.objects.create(
            solution_name=self.solution_name,
            license_type='trial',
            license_key=self.test_license_key,
            features='[]',
            limits='{}'
        )
        
        # Verify encryption still works
        self.assertTrue(license_obj._is_encrypted(license_obj.license_key))
        decrypted_key = license_obj.get_decrypted_license_key()
        self.assertEqual(decrypted_key, self.test_license_key)
    
    def test_empty_license_key(self):
        """Test handling of empty license keys"""
        # Create license without key
        license_obj = LICSolutionLicense.objects.create(
            solution_name=self.solution_name,
            license_type='trial',
            license_key=None,
            features='[]',
            limits='{}'
        )
        
        # Verify no encryption errors
        self.assertIsNone(license_obj.license_key)
        self.assertIsNone(license_obj.get_decrypted_license_key())
    
    def test_encryption_fallback(self):
        """Test encryption fallback behavior"""
        # Create license with plain text key
        license_obj = LICSolutionLicense.objects.create(
            solution_name=self.solution_name,
            license_type='trial',
            license_key=self.test_license_key,
            features='[]',
            limits='{}'
        )
        
        # Verify encryption and decryption work
        self.assertTrue(license_obj._is_encrypted(license_obj.license_key))
        decrypted_key = license_obj.get_decrypted_license_key()
        self.assertEqual(decrypted_key, self.test_license_key)
