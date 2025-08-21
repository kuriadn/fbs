"""
FBS App Notification Service

Service for managing MSME-specific notifications, alerts, and follow-ups.
"""

import logging
from typing import Dict, Any, Optional, List
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

logger = logging.getLogger('fbs_app')


class NotificationService:
    """Service for managing MSME-specific notifications"""
    
    def __init__(self, solution_name):
        self.solution_name = solution_name
        self.fbs_config = getattr(settings, 'FBS_APP', {})
        self.logger = logging.getLogger(f'fbs_app.notifications.{solution_name}')
        
        # Initialize notification settings
        self._notification_settings = {
            'email_notifications': True,
            'sms_notifications': False,
            'push_notifications': True,
            'alert_frequency': 'immediate'
        }
    
    def get_msme_alerts(self, alert_type=None, limit=50):
        """Get MSME alerts for the solution"""
        try:
            # Simulate getting alerts from the solution database
            alerts = []
            
            # Generate sample alerts based on KPI data
            kpi_data = self._get_kpi_data()
            
            # Cash flow alerts
            if kpi_data.get('cash_flow', {}).get('current_balance', 0) < 1000:
                alerts.append({
                    'id': 'cash_flow_low',
                    'type': 'cash_flow',
                    'title': 'Low Cash Flow Alert',
                    'message': f"Current cash balance is ${kpi_data.get('cash_flow', {}).get('current_balance', 0)}. Consider reviewing expenses.",
                    'severity': 'high',
                    'created_at': timezone.now().isoformat(),
                    'action_required': True
                })
            
            # Inventory alerts
            low_stock_items = kpi_data.get('inventory', {}).get('low_stock_items', [])
            if low_stock_items:
                alerts.append({
                    'id': 'inventory_low',
                    'type': 'inventory',
                    'title': 'Low Stock Alert',
                    'message': f"{len(low_stock_items)} items are running low on stock.",
                    'severity': 'medium',
                    'created_at': timezone.now().isoformat(),
                    'action_required': True,
                    'details': low_stock_items
                })
            
            # Payment reminders
            overdue_payments = kpi_data.get('customers', {}).get('overdue_payments', [])
            if overdue_payments:
                alerts.append({
                    'id': 'payments_overdue',
                    'type': 'payment',
                    'title': 'Overdue Payments',
                    'message': f"{len(overdue_payments)} payments are overdue.",
                    'severity': 'high',
                    'created_at': timezone.now().isoformat(),
                    'action_required': True,
                    'details': overdue_payments
                })
            
            # Filter by type if specified
            if alert_type:
                alerts = [alert for alert in alerts if alert['type'] == alert_type]
            
            return {
                'success': True,
                'alerts': alerts[:limit],
                'total_count': len(alerts)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting MSME alerts: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_cash_flow_alert(self, threshold_amount, alert_message=None):
        """Create a cash flow alert"""
        try:
            alert = {
                'id': f'cash_flow_{timezone.now().timestamp()}',
                'type': 'cash_flow',
                'title': 'Cash Flow Alert',
                'message': alert_message or f"Cash flow has dropped below ${threshold_amount}",
                'priority': 'high',
                'created_at': timezone.now().isoformat(),
                'action_required': True,
                'threshold_amount': threshold_amount
            }
            
            # Store alert in database
            from ..models import Notification
            notification = Notification.objects.create(
                solution_name=self.solution_name,
                notification_type='cash_flow_alert',
                title=alert['title'],
                message=alert['message'],
                priority='high',
                created_at=timezone.now()
            )
            
            return {
                'success': True,
                'alert_id': notification.id,
                'alert': alert
            }
            
        except Exception as e:
            self.logger.error(f"Error creating cash flow alert: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_inventory_alert(self, product_name, current_stock, threshold=10):
        """Create an inventory alert"""
        try:
            alert = {
                'id': f'inventory_{timezone.now().timestamp()}',
                'type': 'inventory',
                'title': 'Low Stock Alert',
                'message': f"Product '{product_name}' is running low on stock. Current: {current_stock}, Threshold: {threshold}",
                'priority': 'medium',
                'created_at': timezone.now().isoformat(),
                'action_required': True,
                'product_name': product_name,
                'current_stock': current_stock,
                'threshold': threshold
            }
            
            # Store alert in database
            from ..models import Notification
            notification = Notification.objects.create(
                solution_name=self.solution_name,
                notification_type='inventory_alert',
                title=alert['title'],
                message=alert['message'],
                priority='medium',
                created_at=timezone.now()
            )
            
            return {
                'success': True,
                'alert_id': notification.id,
                'alert': alert
            }
            
        except Exception as e:
            self.logger.error(f"Error creating inventory alert: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_payment_reminder(self, customer_name, amount, due_date):
        """Create a payment reminder"""
        try:
            alert = {
                'id': f'payment_{timezone.now().timestamp()}',
                'type': 'payment',
                'title': 'Payment Reminder',
                'message': f"Payment reminder for {customer_name}. Amount: ${amount}, Due: {due_date}",
                'priority': 'medium',
                'created_at': timezone.now().isoformat(),
                'action_required': True,
                'customer_name': customer_name,
                'amount': amount,
                'due_date': due_date
            }
            
            # Store alert in database
            from ..models import Notification
            notification = Notification.objects.create(
                solution_name=self.solution_name,
                notification_type='payment_reminder',
                title=alert['title'],
                message=alert['message'],
                priority='medium',
                created_at=timezone.now()
            )
            
            return {
                'success': True,
                'alert_id': notification.id,
                'alert': alert
            }
            
        except Exception as e:
            self.logger.error(f"Error creating payment reminder: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_notifications(self, notification_type=None, priority=None, limit=50):
        """Get notifications for the solution"""
        try:
            from ..models import Notification
            
            # Build query
            query = {'solution_name': self.solution_name}
            if notification_type:
                query['notification_type'] = notification_type
            if priority:
                query['priority'] = priority
            
            # Get notifications
            notifications = Notification.objects.filter(**query).order_by('-created_at')[:limit]
            
            notification_data = []
            for notification in notifications:
                notification_data.append({
                    'id': notification.id,
                    'type': notification.notification_type,
                    'title': notification.title,
                    'message': notification.message,
                    'priority': notification.priority,
                    'created_at': notification.created_at.isoformat(),
                    'is_read': notification.is_read
                })
            
            return {
                'success': True,
                'notifications': notification_data,
                'count': len(notification_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting notifications: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def mark_notification_read(self, notification_id):
        """Mark a notification as read"""
        try:
            from ..models import Notification
            
            try:
                notification = Notification.objects.get(id=notification_id)
            except Notification.DoesNotExist:
                return {'success': False, 'error': 'Notification not found'}
            
            # Mark as read
            notification.read = True
            notification.read_at = timezone.now()
            notification.save()
            
            return {
                'success': True,
                'notification_id': notification.id,
                'message': 'Notification marked as read'
            }
            
        except Exception as e:
            self.logger.error(f"Error marking notification as read: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_notification(self, notification_id):
        """Delete a notification"""
        try:
            from ..models import Notification
            
            try:
                notification = Notification.objects.get(id=notification_id)
            except Notification.DoesNotExist:
                return {'success': False, 'error': 'Notification not found'}
            
            # Delete notification
            notification.delete()
            
            return {
                'success': True,
                'message': 'Notification deleted successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_kpi_data(self):
        """Get KPI data for generating alerts"""
        try:
            # This would normally query the database for KPI data
            # For now, return sample data
            return {
                'cash_flow': {
                    'current_balance': 500,
                    'monthly_expenses': 2000,
                    'monthly_income': 3000
                },
                'inventory': {
                    'total_items': 150,
                    'low_stock_items': ['Product A', 'Product B'],
                    'out_of_stock_items': []
                },
                'customers': {
                    'total_customers': 45,
                    'active_customers': 38,
                    'overdue_payments': [
                        {'customer': 'Customer A', 'amount': 500, 'days_overdue': 15},
                        {'customer': 'Customer B', 'amount': 300, 'days_overdue': 8}
                    ]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting KPI data: {str(e)}")
            return {}
    
    # Missing methods that the interface expects
    def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new notification"""
        try:
            from ..models import Notification
            
            notification = Notification.objects.create(
                title=notification_data['title'],
                message=notification_data['message'],
                notification_type=notification_data.get('notification_type', 'info'),
                priority=notification_data.get('priority', 'medium'),
                user_id=notification_data.get('user_id'),
                solution_name=self.solution_name,
                is_read=False
            )
            
            return {
                'success': True,
                'data': {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'priority': notification.priority,
                    'is_read': notification.is_read
                }
            }
        except Exception as e:
            self.logger.error(f"Error creating notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def mark_all_notifications_read(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Mark all notifications as read"""
        try:
            from ..models import Notification
            
            query = {'solution_name': self.solution_name, 'is_read': False}
            if user_id:
                query['user_id'] = user_id
            
            updated_count = Notification.objects.filter(**query).update(
                is_read=True,
                read_at=timezone.now()
            )
            
            return {
                'success': True,
                'data': {
                    'updated_count': updated_count,
                    'message': f'{updated_count} notifications marked as read'
                }
            }
        except Exception as e:
            self.logger.error(f"Error marking all notifications as read: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_notification_settings(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get notification settings"""
        try:
            # Return the current settings from the service instance
            return {
                'success': True,
                'data': self._notification_settings.copy()
            }
        except Exception as e:
            self.logger.error(f"Error getting notification settings: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_notification_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification settings"""
        try:
            # Update the settings in the service instance
            for key, value in settings_data.items():
                if key in self._notification_settings:
                    self._notification_settings[key] = value
            
            return {
                'success': True,
                'data': self._notification_settings.copy(),
                'message': 'Notification settings updated successfully'
            }
        except Exception as e:
            self.logger.error(f"Error updating notification settings: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an alert notification"""
        try:
            from ..models import Notification
            
            # Create alert notification
            notification = Notification.objects.create(
                title=alert_data['title'],
                message=alert_data['message'],
                notification_type='alert',
                priority=alert_data.get('priority', 'medium'),
                user_id=alert_data.get('user_id'),
                solution_name=self.solution_name,
                is_read=False
            )
            
            return {
                'success': True,
                'data': {
                    'id': notification.id,
                    'title': notification.title,
                    'type': 'alert',
                    'priority': notification.priority
                }
            }
        except Exception as e:
            self.logger.error(f"Error sending alert: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_active_alerts(self, alert_type: Optional[str] = None) -> Dict[str, Any]:
        """Get active alerts"""
        try:
            from ..models import Notification
            
            query = {
                'solution_name': self.solution_name,
                'notification_type': 'alert',
                'is_read': False
            }
            if alert_type:
                query['priority'] = alert_type
            
            alerts = Notification.objects.filter(**query).order_by('-created_at')
            alert_list = []
            
            for alert in alerts:
                alert_list.append({
                    'id': alert.id,
                    'title': alert.title,
                    'message': alert.message,
                    'type': alert.notification_type,
                    'priority': alert.priority,
                    'created_at': alert.created_at.isoformat()
                })
            
            return {
                'success': True,
                'alerts': alert_list,
                'count': len(alert_list)
            }
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {str(e)}")
            return {'success': False, 'error': str(e)}
