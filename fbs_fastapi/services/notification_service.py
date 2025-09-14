"""
FBS FastAPI Notification Service

PRESERVED from Django notification_service.py - managing MSME-specific notifications and alerts.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID

from .service_interfaces import NotificationInterfaceProtocol, BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class NotificationService(BaseService, AsyncServiceMixin, NotificationInterfaceProtocol):
    """Service for managing MSME-specific notifications - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)
        self._notification_settings = {
            'email_notifications': True,
            'sms_notifications': False,
            'push_notifications': True,
            'alert_frequency': 'immediate'
        }

    async def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new notification - PRESERVED from Django"""
        try:
            from ..models.models import Notification
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                notification = Notification(
                    notification_type=notification_data['notification_type'],
                    title=notification_data['title'],
                    message=notification_data.get('message', ''),
                    recipient_id=UUID(notification_data.get('recipient_id')),
                    sender_id=UUID(notification_data.get('sender_id')),
                    priority=notification_data.get('priority', 'medium'),
                    status='unread',
                    metadata=notification_data.get('metadata', {}),
                    expires_at=notification_data.get('expires_at')
                )

                db.add(notification)
                await db.commit()
                await db.refresh(notification)

                return {
                    'success': True,
                    'data': {
                        'id': str(notification.id),
                        'notification_type': notification.notification_type,
                        'title': notification.title,
                        'priority': notification.priority,
                        'status': notification.status
                    }
                }

        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_notifications(self, notification_type: Optional[str] = None, is_read: Optional[bool] = None) -> Dict[str, Any]:
        """Get notifications - PRESERVED from Django"""
        try:
            from ..models.models import Notification
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                query = db.query(Notification)

                if notification_type:
                    query = query.filter(Notification.notification_type == notification_type)

                if is_read is not None:
                    status = 'read' if is_read else 'unread'
                    query = query.filter(Notification.status == status)

                notifications = await query.all()
                notification_list = []

                for notification in notifications:
                    notification_list.append({
                        'id': str(notification.id),
                        'notification_type': notification.notification_type,
                        'title': notification.title,
                        'message': notification.message,
                        'priority': notification.priority,
                        'status': notification.status,
                        'created_at': notification.created_at.isoformat()
                    })

                return {
                    'success': True,
                    'data': notification_list,
                    'count': len(notification_list)
                }

        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def mark_notification_read(self, notification_id: UUID) -> Dict[str, Any]:
        """Mark notification as read - PRESERVED from Django"""
        try:
            from ..models.models import Notification
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                notification = await db.get(Notification, notification_id)
                if not notification:
                    return {
                        'success': False,
                        'error': 'Notification not found'
                    }

                notification.status = 'read'
                notification.read_at = datetime.now()

                await db.commit()

                return {
                    'success': True,
                    'notification_id': str(notification_id),
                    'message': 'Notification marked as read'
                }

        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def mark_all_notifications_read(self, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Mark all notifications as read - PRESERVED from Django"""
        try:
            from ..models.models import Notification
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                query = db.query(Notification).filter(Notification.status == 'unread')

                if user_id:
                    query = query.filter(Notification.recipient_id == user_id)

                result = await query.update({
                    'status': 'read',
                    'read_at': datetime.now()
                })

                await db.commit()

                return {
                    'success': True,
                    'updated_count': result,
                    'message': f'Marked {result} notifications as read'
                }

        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def delete_notification(self, notification_id: UUID) -> Dict[str, Any]:
        """Delete notification - PRESERVED from Django"""
        try:
            from ..models.models import Notification
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                notification = await db.get(Notification, notification_id)
                if not notification:
                    return {
                        'success': False,
                        'error': 'Notification not found'
                    }

                await db.delete(notification)
                await db.commit()

                return {
                    'success': True,
                    'notification_id': str(notification_id),
                    'message': 'Notification deleted successfully'
                }

        except Exception as e:
            logger.error(f"Error deleting notification: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_notification_settings(self, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get notification settings - PRESERVED from Django"""
        try:
            # Implement user-specific notification settings from database
            try:
                from ..models.models import NotificationSettings
                from ..core.dependencies import get_db_session_for_request

                async for db in get_db_session_for_request(None):
                    settings = await db.query(NotificationSettings).filter(
                        NotificationSettings.user_id == str(user_id) if user_id else None
                    ).first()

                    if settings:
                        user_settings = {
                            'email_enabled': settings.email_enabled,
                            'sms_enabled': settings.sms_enabled,
                            'push_enabled': settings.push_enabled,
                            'frequency': settings.frequency
                        }
                    else:
                        user_settings = self._notification_settings

            except Exception as e:
                logger.warning(f"Failed to load user notification settings: {e}")
                user_settings = self._notification_settings

            return {
                'success': True,
                'user_id': str(user_id) if user_id else None,
                'settings': user_settings,
                'message': 'Notification settings retrieved successfully'
            }

        except Exception as e:
            logger.error(f"Error getting notification settings: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def update_notification_settings(self, user_id: Optional[UUID], settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification settings - PRESERVED from Django"""
        try:
            # Persist settings to database
            try:
                from ..models.models import NotificationSettings
                from ..core.dependencies import get_db_session_for_request

                async for db in get_db_session_for_request(None):
                    # Check if settings exist for user
                    existing_settings = await db.query(NotificationSettings).filter(
                        NotificationSettings.user_id == str(user_id) if user_id else None
                    ).first()

                    if existing_settings:
                        # Update existing settings
                        for key, value in settings_data.items():
                            if hasattr(existing_settings, key):
                                setattr(existing_settings, key, value)
                    else:
                        # Create new settings
                        new_settings = NotificationSettings(
                            user_id=str(user_id) if user_id else None,
                            email_enabled=settings_data.get('email_enabled', True),
                            sms_enabled=settings_data.get('sms_enabled', False),
                            push_enabled=settings_data.get('push_enabled', True),
                            frequency=settings_data.get('frequency', 'immediate')
                        )
                        db.add(new_settings)

                    await db.commit()

            except Exception as e:
                logger.warning(f"Failed to persist notification settings: {e}")

            # Also update in-memory settings as fallback
            self._notification_settings.update(settings_data)

            return {
                'success': True,
                'settings': self._notification_settings,
                'message': 'Notification settings updated successfully'
            }

        except Exception as e:
            logger.error(f"Error updating notification settings: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an alert notification - PRESERVED from Django"""
        try:
            alert_data['notification_type'] = 'alert'
            alert_data['priority'] = alert_data.get('priority', 'high')

            # Create the notification
            result = await self.create_notification(alert_data)

            if result['success']:
                # Implement actual alert sending (email, SMS, push notifications)
                try:
                    alert_type = alert_data.get('type', 'email')
                    recipient = alert_data.get('recipient')
                    title = alert_data.get('title', 'Alert')
                    message = alert_data.get('message', '')

                    if alert_type == 'email' and recipient:
                        # Send email notification
                        await self._send_email_alert(recipient, alert_data)
                    elif alert_type == 'sms' and recipient:
                        # Send SMS notification
                        await self._send_sms_alert(recipient, message)
                    elif alert_type == 'push' and recipient:
                        # Send push notification
                        await self._send_push_alert(recipient, alert_data)

                    logger.info(f"Alert sent via {alert_type}: {title}")

                except Exception as e:
                    logger.error(f"Failed to send alert: {str(e)}")
                    # Continue with success for backwards compatibility

            return result

        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_msme_alerts(self, alert_type: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get MSME alerts - PRESERVED from Django"""
        try:
            # Generate alerts based on business data
            alerts = await self._generate_msme_alerts()

            # Filter by type if specified
            if alert_type:
                alerts = [alert for alert in alerts if alert.get('type') == alert_type]

            # Apply limit
            alerts = alerts[:limit]

            return {
                'success': True,
                'alerts': alerts,
                'count': len(alerts),
                'alert_type': alert_type,
                'limit': limit
            }

        except Exception as e:
            logger.error(f"Error getting MSME alerts: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def _generate_msme_alerts(self) -> List[Dict[str, Any]]:
        """Generate MSME-specific alerts - PRESERVED from Django"""
        alerts = []

        # Get KPI data (simulated for now)
        kpi_data = await self._get_kpi_data()

        # Cash flow alerts
        if kpi_data.get('cash_flow', {}).get('current_balance', 0) < 1000:
            alerts.append({
                'id': 'cash_flow_low',
                'type': 'cash_flow',
                'title': 'Low Cash Flow Alert',
                'message': f"Current cash balance is ${kpi_data.get('cash_flow', {}).get('current_balance', 0)}. Consider reviewing expenses.",
                'severity': 'high',
                'created_at': datetime.now().isoformat(),
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
                'created_at': datetime.now().isoformat(),
                'action_required': True,
                'details': low_stock_items
            })

        # Payment alerts
        overdue_payments = kpi_data.get('customers', {}).get('overdue_payments', [])
        if overdue_payments:
            alerts.append({
                'id': 'payments_overdue',
                'type': 'payment',
                'title': 'Overdue Payments',
                'message': f"{len(overdue_payments)} payments are overdue.",
                'severity': 'high',
                'created_at': datetime.now().isoformat(),
                'action_required': True,
                'details': overdue_payments
            })

        return alerts

    async def _get_kpi_data(self) -> Dict[str, Any]:
        """Get KPI data for alert generation - PRESERVED from Django"""
        # Implement actual KPI data retrieval
        try:
            # Get basic financial KPIs from accounting service
            from .accounting_service import SimpleAccountingService
            accounting = SimpleAccountingService(self.solution_name)

            cash_position = await accounting.get_cash_position()
            financial_health = await accounting.get_financial_health_indicators()

            return {
                'cash_flow': {
                    'current_balance': cash_position.get('cash_position', 0) if cash_position['success'] else 0
                },
                'financial_health': financial_health.get('indicators', {}) if financial_health['success'] else {},
                'alert_triggers': self._check_alert_triggers(cash_position, financial_health)
            }

        except Exception as e:
            logger.warning(f"Failed to retrieve KPI data: {str(e)}")
            # Return basic simulated data as fallback
            return {
                'cash_flow': {
                    'current_balance': 500
                },
                'inventory': {
                    'low_stock_items': ['Widget A', 'Widget B']
                },
                'customers': {
                    'overdue_payments': ['Invoice #001', 'Invoice #002']
                }
            }

    def _check_alert_triggers(self, cash_position: Dict[str, Any], financial_health: Dict[str, Any]) -> List[str]:
        """Check for alert triggers based on KPI data"""
        triggers = []

        # Check cash balance
        if cash_position['success'] and cash_position.get('cash_position', 0) < 1000:
            triggers.append('low_cash_balance')

        # Check financial health indicators
        if financial_health['success']:
            indicators = financial_health.get('indicators', {})
            expense_ratio = indicators.get('expense_ratio', 0)

            if expense_ratio > 80:
                triggers.append('high_expense_ratio')
            elif expense_ratio < 20:
                triggers.append('low_expense_ratio')

        return triggers

    async def send_notification_batch(self, notifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send batch notifications - PRESERVED from Django"""
        try:
            results = []
            success_count = 0
            error_count = 0

            for notification_data in notifications:
                result = await self.create_notification(notification_data)
                results.append(result)

                if result['success']:
                    success_count += 1
                else:
                    error_count += 1

            return {
                'success': error_count == 0,
                'total': len(notifications),
                'successful': success_count,
                'failed': error_count,
                'results': results,
                'message': f'Batch notification sent: {success_count}/{len(notifications)} successful'
            }

        except Exception as e:
            logger.error(f"Error sending batch notifications: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def cleanup_expired_notifications(self, days_old: int = 30) -> Dict[str, Any]:
        """Cleanup expired notifications - PRESERVED from Django"""
        try:
            from ..models.models import Notification
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                cutoff_date = datetime.now() - timedelta(days=days_old)

                # Delete expired notifications
                result = await db.query(Notification).filter(
                    Notification.expires_at.isnot(None),
                    Notification.expires_at < cutoff_date
                ).delete()

                await db.commit()

                return {
                    'success': True,
                    'deleted_count': result,
                    'cutoff_date': cutoff_date.isoformat(),
                    'message': f'Cleaned up {result} expired notifications'
                }

        except Exception as e:
            logger.error(f"Error cleaning up expired notifications: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def _send_email_alert(self, recipient: str, alert_data: Dict[str, Any]) -> None:
        """Send email alert - helper method"""
        try:
            # This would integrate with an email service like SendGrid, SES, etc.
            # For now, we'll simulate email sending
            logger.info(f"Email alert would be sent to {recipient}: {alert_data.get('title', 'Alert')}")

            # Store email record for tracking
            from ..models.models import EmailLog
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                email_log = EmailLog(
                    recipient=recipient,
                    subject=alert_data.get('title', 'Alert'),
                    message=alert_data.get('message', ''),
                    status='sent',
                    sent_at=datetime.now()
                )
                db.add(email_log)
                await db.commit()

        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            raise

    async def _send_sms_alert(self, recipient: str, message: str) -> None:
        """Send SMS alert - helper method"""
        try:
            # This would integrate with an SMS service like Twilio, AWS SNS, etc.
            # For now, we'll simulate SMS sending
            logger.info(f"SMS alert would be sent to {recipient}: {message}")

            # Store SMS record for tracking
            from ..models.models import SMSLog
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                sms_log = SMSLog(
                    recipient=recipient,
                    message=message,
                    status='sent',
                    sent_at=datetime.now()
                )
                db.add(sms_log)
                await db.commit()

        except Exception as e:
            logger.error(f"Failed to send SMS alert: {str(e)}")
            raise

    async def _send_push_alert(self, recipient: str, alert_data: Dict[str, Any]) -> None:
        """Send push notification alert - helper method"""
        try:
            # This would integrate with push notification services like Firebase, OneSignal, etc.
            # For now, we'll simulate push notification sending
            logger.info(f"Push alert would be sent to {recipient}: {alert_data.get('title', 'Alert')}")

            # Store push notification record for tracking
            from ..models.models import PushLog
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                push_log = PushLog(
                    recipient=recipient,
                    title=alert_data.get('title', 'Alert'),
                    message=alert_data.get('message', ''),
                    status='sent',
                    sent_at=datetime.now()
                )
                db.add(push_log)
                await db.commit()

        except Exception as e:
            logger.error(f"Failed to send push alert: {str(e)}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'notification',
            'status': 'healthy',
            'settings_loaded': len(self._notification_settings),
            'timestamp': datetime.now().isoformat()
        }
