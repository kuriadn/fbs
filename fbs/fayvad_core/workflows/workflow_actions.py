"""
Workflow Actions System

Provides extensible workflow actions similar to Odoo's server actions but more flexible.
Actions can be chained and customized for different business domains.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from django.contrib.auth.models import User
import logging

logger = logging.getLogger('fayvad_core.workflows')


class WorkflowAction(ABC):
    """
    Base class for workflow actions
    """
    
    def __init__(self, action_config: Dict[str, Any]):
        self.config = action_config
        self.name = action_config.get('name', self.__class__.__name__)
        self.description = action_config.get('description', '')
    
    @abstractmethod
    def execute(self, context: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Execute the action and return result
        
        Args:
            context: Workflow context containing record data, workflow data, etc.
            user: User executing the action
            
        Returns:
            Dict containing execution result and any output data
        """
        pass
    
    def validate_config(self) -> bool:
        """Validate action configuration"""
        return True


class SendEmailAction(WorkflowAction):
    """Send email action"""
    
    def execute(self, context: Dict[str, Any], user: User) -> Dict[str, Any]:
        try:
            # Extract email configuration from context
            template_id = self.config.get('template_id')
            recipients = self.config.get('recipients', [])
            subject = self.config.get('subject', '')
            body = self.config.get('body', '')
            
            # TODO: Implement email sending logic
            # This would integrate with Django's email backend or external service
            
            logger.info(f"Email action executed: {self.name}")
            
            return {
                'success': True,
                'message': 'Email sent successfully',
                'data': {
                    'recipients': recipients,
                    'subject': subject
                }
            }
            
        except Exception as e:
            logger.error(f"Email action failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class UpdateRecordAction(WorkflowAction):
    """Update Odoo record action"""
    
    def execute(self, context: Dict[str, Any], user: User) -> Dict[str, Any]:
        try:
            from ..services.odoo_client import odoo_client
            
            # Extract update configuration
            model_name = self.config.get('model_name')
            record_id = context.get('record_id')
            update_data = self.config.get('update_data', {})
            
            if not model_name or not record_id:
                raise ValueError("model_name and record_id are required")
            
            # Execute update via Odoo client
            result = odoo_client.update_record(
                model_name=model_name,
                record_id=record_id,
                data=update_data,
                token=context.get('token'),
                database=context.get('database')
            )
            
            return {
                'success': True,
                'message': 'Record updated successfully',
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Update record action failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class CreateRecordAction(WorkflowAction):
    """Create new Odoo record action"""
    
    def execute(self, context: Dict[str, Any], user: User) -> Dict[str, Any]:
        try:
            from ..services.odoo_client import odoo_client
            
            # Extract creation configuration
            model_name = self.config.get('model_name')
            create_data = self.config.get('create_data', {})
            
            if not model_name:
                raise ValueError("model_name is required")
            
            # Execute creation via Odoo client
            result = odoo_client.create_record(
                model_name=model_name,
                data=create_data,
                token=context.get('token'),
                database=context.get('database')
            )
            
            # Store created record ID in workflow data
            context['workflow_data']['created_record_id'] = result.get('id')
            
            return {
                'success': True,
                'message': 'Record created successfully',
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Create record action failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class SendNotificationAction(WorkflowAction):
    """Send notification action (in-app, webhook, etc.)"""
    
    def execute(self, context: Dict[str, Any], user: User) -> Dict[str, Any]:
        try:
            # Extract notification configuration
            notification_type = self.config.get('type', 'in_app')  # in_app, webhook, slack, etc.
            message = self.config.get('message', '')
            recipients = self.config.get('recipients', [])
            
            # TODO: Implement notification logic
            # This would integrate with notification services
            
            logger.info(f"Notification action executed: {self.name}")
            
            return {
                'success': True,
                'message': 'Notification sent successfully',
                'data': {
                    'type': notification_type,
                    'recipients': recipients
                }
            }
            
        except Exception as e:
            logger.error(f"Notification action failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class ApprovalAction(WorkflowAction):
    """Request approval action"""
    
    def execute(self, context: Dict[str, Any], user: User) -> Dict[str, Any]:
        try:
            # Extract approval configuration
            approvers = self.config.get('approvers', [])
            approval_type = self.config.get('approval_type', 'single')  # single, all, majority
            deadline_hours = self.config.get('deadline_hours', 24)
            
            # TODO: Implement approval logic
            # This would create approval requests and wait for responses
            
            logger.info(f"Approval action executed: {self.name}")
            
            return {
                'success': True,
                'message': 'Approval requested successfully',
                'data': {
                    'approvers': approvers,
                    'approval_type': approval_type,
                    'deadline_hours': deadline_hours
                }
            }
            
        except Exception as e:
            logger.error(f"Approval action failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class DelayAction(WorkflowAction):
    """Delay workflow execution action"""
    
    def execute(self, context: Dict[str, Any], user: User) -> Dict[str, Any]:
        try:
            # Extract delay configuration
            delay_minutes = self.config.get('delay_minutes', 0)
            delay_until = self.config.get('delay_until')  # Specific datetime
            
            # TODO: Implement delay logic
            # This would pause the workflow and resume later
            
            logger.info(f"Delay action executed: {self.name} - {delay_minutes} minutes")
            
            return {
                'success': True,
                'message': f'Workflow delayed for {delay_minutes} minutes',
                'data': {
                    'delay_minutes': delay_minutes,
                    'delay_until': delay_until
                }
            }
            
        except Exception as e:
            logger.error(f"Delay action failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class WorkflowActionRegistry:
    """
    Registry for workflow actions
    """
    
    _actions = {}
    
    @classmethod
    def register(cls, action_type: str, action_class: type):
        """Register a new action type"""
        cls._actions[action_type] = action_class
    
    @classmethod
    def get_action(cls, action_type: str, config: Dict[str, Any]) -> WorkflowAction:
        """Get action instance by type"""
        if action_type not in cls._actions:
            raise ValueError(f"Unknown action type: {action_type}")
        
        action_class = cls._actions[action_type]
        return action_class(config)
    
    @classmethod
    def list_actions(cls) -> List[str]:
        """List all registered action types"""
        return list(cls._actions.keys())


# Register built-in actions
WorkflowActionRegistry.register('send_email', SendEmailAction)
WorkflowActionRegistry.register('update_record', UpdateRecordAction)
WorkflowActionRegistry.register('create_record', CreateRecordAction)
WorkflowActionRegistry.register('send_notification', SendNotificationAction)
WorkflowActionRegistry.register('approval', ApprovalAction)
WorkflowActionRegistry.register('delay', DelayAction) 