"""
Basic Functionality Tests

These tests provide basic unit, integration, end-to-end, performance, and security tests.
They are designed to quickly verify that the overall testing infrastructure (pytest, database setup, user creation) is functioning correctly.
"""

import pytest
import time
from django.test import TestCase
from django.contrib.auth.models import User


@pytest.mark.unit
class TestBasicFunctionality(TestCase):
    """Test basic functionality to verify testing infrastructure."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.mark.unit
    def test_user_creation(self):
        """Test that user creation works."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    @pytest.mark.unit
    def test_user_authentication(self):
        """Test user authentication."""
        self.assertTrue(self.user.is_authenticated)
        self.assertFalse(self.user.is_anonymous)
    
    @pytest.mark.unit
    def test_user_properties(self):
        """Test user properties."""
        self.assertIsNotNone(self.user.id)
        self.assertTrue(hasattr(self.user, 'username'))
        self.assertTrue(hasattr(self.user, 'email'))
        self.assertTrue(hasattr(self.user, 'password'))


@pytest.mark.integration
class TestIntegrationBasics(TestCase):
    """Test basic integration functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass456'
        )
    
    @pytest.mark.integration
    def test_multiple_users(self):
        """Test that multiple users can coexist."""
        self.assertNotEqual(self.user1.id, self.user2.id)
        self.assertNotEqual(self.user1.username, self.user2.username)
        self.assertNotEqual(self.user1.email, self.user2.email)
    
    @pytest.mark.integration
    def test_user_relationships(self):
        """Test basic user relationships."""
        # Users should be different objects
        self.assertIsNot(self.user1, self.user2)
        
        # But both should be User instances
        self.assertIsInstance(self.user1, User)
        self.assertIsInstance(self.user2, User)


@pytest.mark.e2e
class TestEndToEndBasics(TestCase):
    """Test basic end-to-end functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='e2euser',
            email='e2e@example.com',
            password='e2epass123'
        )
    
    @pytest.mark.e2e
    def test_complete_user_lifecycle(self):
        """Test complete user lifecycle."""
        # 1. User creation
        self.assertIsNotNone(self.user.id)
        self.assertEqual(self.user.username, 'e2euser')
        
        # 2. User authentication
        self.assertTrue(self.user.is_authenticated)
        
        # 3. User modification
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'
        self.user.save()
        
        # 4. Verify changes
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, 'John')
        self.assertEqual(updated_user.last_name, 'Doe')
        
        # 5. User deletion (cleanup)
        user_id = self.user.id
        self.user.delete()
        
        # 6. Verify deletion
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)


@pytest.mark.performance
class TestPerformanceBasics(TestCase):
    """Test basic performance functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.users = []
    
    def tearDown(self):
        """Clean up test data."""
        for user in self.users:
            if user.id:
                user.delete()
    
    @pytest.mark.performance
    def test_bulk_user_creation(self):
        """Test bulk user creation performance."""
        start_time = time.time()
        
        # Create multiple users
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'bulkuser{i}',
                email=f'bulkuser{i}@example.com',
                password='testpass123'
            )
            self.users.append(user)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertion (should complete within reasonable time)
        self.assertLess(duration, 10.0)  # Should complete within 10 seconds (more realistic for test environment)
        
        # Verify all users were created
        self.assertEqual(len(self.users), 10)


@pytest.mark.security
class TestSecurityBasics(TestCase):
    """Test basic security functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='secuser',
            email='sec@example.com',
            password='secpass123'
        )
    
    @pytest.mark.security
    def test_password_security(self):
        """Test password security features."""
        # Password should be hashed (not plain text)
        self.assertNotEqual(self.user.password, 'secpass123')
        
        # Password verification should work
        self.assertTrue(self.user.check_password('secpass123'))
        self.assertFalse(self.user.check_password('wrongpassword'))
    
    @pytest.mark.security
    def test_user_isolation(self):
        """Test user data isolation."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Users should be isolated
        self.assertNotEqual(self.user.id, other_user.id)
        self.assertNotEqual(self.user.username, other_user.username)
        
        # Clean up
        other_user.delete()
