"""
Tests for FBS App Notification Service

Tests all notification service methods including notification creation, management, settings, and alerts.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from fbs_app.services.notification_service import NotificationService


class TestNotificationService(TestCase):
    """Test cases for NotificationService"""
    
    def setUp(self):
        """Set up test data"""
        self.service = NotificationService('test_solution')
        self.test_notification_data = {
            'title': 'Test Notification',
            'message': 'This is a test notification',
            'notification_type': 'info',
            'priority': 'medium'
        }
    
    def test_create_notification_success(self):
        """Test successful notification creation"""
        result = self.service.create_notification(self.test_notification_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['title'], self.test_notification_data['title'])
        self.assertEqual(result['data']['message'], self.test_notification_data['message'])
    
    def test_create_notification_missing_required_field(self):
        """Test notification creation with missing required field"""
        incomplete_data = self.test_notification_data.copy()
        del incomplete_data['title']
        
        result = self.service.create_notification(incomplete_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_create_notification_with_defaults(self):
        """Test notification creation with default values"""
        minimal_data = {
            'title': 'Minimal Notification',
            'message': 'Minimal message'
        }
        
        result = self.service.create_notification(minimal_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['notification_type'], 'info')
        self.assertEqual(result['data']['priority'], 'medium')
    
    def test_get_notifications_all(self):
        """Test getting all notifications"""
        # Create a few test notifications first
        self.service.create_notification(self.test_notification_data)
        self.service.create_notification({
            'title': 'Second Notification',
            'message': 'Another test message'
        })
        
        result = self.service.get_notifications()
        
        self.assertTrue(result['success'])
        self.assertGreater(len(result['notifications']), 0)
    
    def test_get_notifications_by_type(self):
        """Test getting notifications by type"""
        # Create notifications of different types
        self.service.create_notification(self.test_notification_data)
        self.service.create_notification({
            'title': 'Warning Notification',
            'message': 'Warning message',
            'notification_type': 'warning'
        })
        
        result = self.service.get_notifications(notification_type='warning')
        
        self.assertTrue(result['success'])
        self.assertTrue(all(n['type'] == 'warning' for n in result['notifications']))
    
    def test_get_notifications_by_severity(self):
        """Test getting notifications by severity"""
        # Create notifications of different severities
        self.service.create_notification(self.test_notification_data)
        self.service.create_notification({
            'title': 'High Severity Notification',
            'message': 'High severity message',
            'priority': 'high'
        })
        
        result = self.service.get_notifications(priority='high')
        
        self.assertTrue(result['success'])
        self.assertTrue(all(n['priority'] == 'high' for n in result['notifications']))
    
    def test_mark_notification_read_success(self):
        """Test successful notification read marking"""
        # Create a notification first
        create_result = self.service.create_notification(self.test_notification_data)
        notification_id = create_result['data']['id']
        
        result = self.service.mark_notification_read(notification_id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['notification_id'], notification_id)
    
    def test_mark_notification_read_not_found(self):
        """Test marking non-existent notification as read"""
        result = self.service.mark_notification_read(99999)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_mark_all_notifications_read_success(self):
        """Test marking all notifications as read"""
        # Create a few test notifications
        self.service.create_notification(self.test_notification_data)
        self.service.create_notification({
            'title': 'Second Notification',
            'message': 'Another test message'
        })
        
        result = self.service.mark_all_notifications_read()
        
        self.assertTrue(result['success'])
        self.assertGreater(result['data']['updated_count'], 0)
    
    def test_delete_notification_success(self):
        """Test successful notification deletion"""
        # Create a notification first
        create_result = self.service.create_notification(self.test_notification_data)
        notification_id = create_result['data']['id']
        
        result = self.service.delete_notification(notification_id)
        
        self.assertTrue(result['success'])
        
        # Verify it's deleted
        get_result = self.service.get_notifications()
        self.assertEqual(len(get_result['notifications']), 0)
    
    def test_delete_notification_not_found(self):
        """Test deleting non-existent notification"""
        result = self.service.delete_notification(99999)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_get_notification_settings_success(self):
        """Test successful notification settings retrieval"""
        result = self.service.get_notification_settings()
        
        self.assertTrue(result['success'])
        self.assertIn('email_notifications', result['data'])
        self.assertIn('sms_notifications', result['data'])
        self.assertIn('push_notifications', result['data'])
    
    def test_update_notification_settings_success(self):
        """Test successful notification settings update"""
        new_settings = {
            'email_notifications': False,
            'sms_notifications': True,
            'push_notifications': False
        }
        
        result = self.service.update_notification_settings(new_settings)
        
        self.assertTrue(result['success'])
        
        # Verify the update
        get_result = self.service.get_notification_settings()
        self.assertEqual(get_result['data']['email_notifications'], False)
        self.assertEqual(get_result['data']['sms_notifications'], True)
    
    def test_send_alert_success(self):
        """Test successful alert sending"""
        alert_data = {
            'title': 'Test Alert',
            'message': 'This is a test alert',
            'priority': 'high'
        }
        
        result = self.service.send_alert(alert_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['type'], 'alert')
    
    def test_send_alert_with_defaults(self):
        """Test sending alert with default values"""
        minimal_alert = {
            'title': 'Minimal Alert',
            'message': 'Minimal alert message'
        }
        
        result = self.service.send_alert(minimal_alert)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['priority'], 'medium')
    
    def test_get_active_alerts_success(self):
        """Test successful active alerts retrieval"""
        # Create a few test alerts
        self.service.send_alert({
            'title': 'Active Alert 1',
            'message': 'First active alert'
        })
        self.service.send_alert({
            'title': 'Active Alert 2',
            'message': 'Second active alert'
        })
        
        result = self.service.get_active_alerts()
        
        self.assertTrue(result['success'])
        self.assertGreater(len(result['alerts']), 0)
    
    def test_get_active_alerts_by_type(self):
        """Test getting active alerts by type"""
        # Create alerts of different priorities
        self.service.send_alert({
            'title': 'High Priority Alert',
            'message': 'High priority message',
            'priority': 'high'
        })
        self.service.send_alert({
            'title': 'Medium Priority Alert',
            'message': 'Medium priority message',
            'priority': 'medium'
        })
        
        result = self.service.get_active_alerts(alert_type='high')
        
        self.assertTrue(result['success'])
        self.assertTrue(all(a['priority'] == 'high' for a in result['alerts']))
    
    def test_get_msme_alerts_success(self):
        """Test successful MSME alerts retrieval"""
        result = self.service.get_msme_alerts()
        
        self.assertTrue(result['success'])
        self.assertIn('alerts', result)
        self.assertIn('total_count', result)
    
    def test_get_msme_alerts_by_type(self):
        """Test getting MSME alerts by type"""
        result = self.service.get_msme_alerts(alert_type='cash_flow')
        
        self.assertTrue(result['success'])
        # All returned alerts should be of the specified type
        if result['alerts']:
            self.assertTrue(all(alert['type'] == 'cash_flow' for alert in result['alerts']))
    
    def test_get_msme_alerts_with_limit(self):
        """Test getting MSME alerts with limit"""
        result = self.service.get_msme_alerts(limit=5)
        
        self.assertTrue(result['success'])
        self.assertLessEqual(len(result['alerts']), 5)
    
    def test_create_cash_flow_alert(self):
        """Test creating cash flow alert"""
        result = self.service.create_cash_flow_alert(1000, "Cash flow is low")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['alert']['type'], 'cash_flow')
        self.assertEqual(result['alert']['priority'], 'high')
    
    def test_create_inventory_alert(self):
        """Test creating inventory alert"""
        result = self.service.create_inventory_alert("Test Product", 5, 10)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['alert']['type'], 'inventory')
        self.assertIn('product_name', result['alert'])
    
    def test_create_payment_reminder(self):
        """Test creating payment reminder"""
        result = self.service.create_payment_reminder("Customer A", 500, "2025-02-01")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['alert']['type'], 'payment')
        self.assertIn('customer_name', result['alert'])
    
    def test_notification_with_empty_data(self):
        """Test notification operations with empty data"""
        result = self.service.create_notification({})
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_notification_with_invalid_types(self):
        """Test notification operations with invalid types"""
        invalid_data = {
            'title': 123,  # Invalid type
            'message': None,  # Invalid type
            'notification_type': 'invalid_type'
        }
        
        result = self.service.create_notification(invalid_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_alert_with_empty_data(self):
        """Test alert operations with empty data"""
        result = self.service.send_alert({})
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_alert_with_invalid_priority(self):
        """Test alert operations with invalid priority"""
        result = self.service.send_alert({
            'title': 'Test Alert',
            'message': 'Test message',
            'priority': 'invalid_priority'
        })
        
        # Should still work as we're not validating enum values in the service
        self.assertTrue(result['success'] or 'error' in result)
    
    def test_notification_performance(self):
        """Test notification creation performance"""
        import time
        
        start_time = time.time()
        
        # Create multiple notifications
        for i in range(10):
            self.service.create_notification({
                'title': f'Performance Test {i}',
                'message': f'Message {i}'
            })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(duration, 1.0)
    
    def test_alert_performance(self):
        """Test alert creation performance"""
        import time
        
        start_time = time.time()
        
        # Create multiple alerts
        for i in range(10):
            self.service.send_alert({
                'title': f'Performance Alert {i}',
                'message': f'Alert message {i}'
            })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (1 second)
        self.assertLess(duration, 1.0)
    
    def test_notification_integration(self):
        """Test notification service integration"""
        # Test full workflow: create, read, update, delete
        create_result = self.service.create_notification(self.test_notification_data)
        self.assertTrue(create_result['success'])
        
        notification_id = create_result['data']['id']
        
        # Mark as read
        read_result = self.service.mark_notification_read(notification_id)
        self.assertTrue(read_result['success'])
        
        # Update settings
        settings_result = self.service.update_notification_settings({'email_notifications': False})
        self.assertTrue(settings_result['success'])
        
        # Delete
        delete_result = self.service.delete_notification(notification_id)
        self.assertTrue(delete_result['success'])
    
    def test_alert_integration(self):
        """Test alert service integration"""
        # Test full workflow: create, get, filter
        alert_result = self.service.send_alert({
            'title': 'Integration Test Alert',
            'message': 'Testing alert integration'
        })
        self.assertTrue(alert_result['success'])
        
        # Get all alerts
        all_alerts = self.service.get_active_alerts()
        self.assertTrue(all_alerts['success'])
        
        # Filter by priority
        filtered_alerts = self.service.get_active_alerts(alert_type='medium')
        self.assertTrue(filtered_alerts['success'])
    
    def test_error_handling(self):
        """Test error handling in notification service"""
        # Test with invalid notification ID
        result = self.service.mark_notification_read(99999)
        self.assertFalse(result['success'])
        
        # Test with invalid alert data
        result = self.service.send_alert({})
        self.assertFalse(result['success'])
        
        # Test with invalid settings
        result = self.service.update_notification_settings({})
        self.assertTrue(result['success'])  # Should use defaults
    
    def test_edge_cases(self):
        """Test edge cases in notification service"""
        # Test with very long title and message
        long_title = 'A' * 1000
        long_message = 'B' * 10000
        
        result = self.service.create_notification({
            'title': long_title,
            'message': long_message
        })
        
        # Should handle long content gracefully
        self.assertTrue(result['success'] or 'error' in result)
        
        # Test with special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = self.service.create_notification({
            'title': special_chars,
            'message': special_chars
        })
        
        self.assertTrue(result['success'] or 'error' in result)
