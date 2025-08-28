"""
MSME Workflow Service

Comprehensive service for MSME workflow management including:
- Workflow definition and design
- Workflow execution and monitoring
- Approval processes
- Task automation
- Process tracking and reporting
"""

import logging
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json
import uuid

from ..models.workflows import (
    WorkflowDefinition, WorkflowInstance, WorkflowStep, 
    WorkflowTransition, WorkflowExecutionLog
)
from ..models.core import ApprovalRequest, ApprovalResponse

logger = logging.getLogger(__name__)


class MSMEWorkflowService:
    """Service for MSME workflow management operations"""
    
    def __init__(self, user: User):
        self.user = user
        self.logger = logging.getLogger(f"{__name__}.{user.username}")
    
    def create_workflow_definition(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new workflow definition
        
        Args:
            workflow_data: Workflow configuration data
            
        Returns:
            Dict containing creation result
        """
        try:
            with transaction.atomic():
                # Create workflow definition
                workflow = WorkflowDefinition.objects.create(
                    name=workflow_data.get('name'),
                    description=workflow_data.get('description'),
                    workflow_type=workflow_data.get('workflow_type', 'custom'),
                    workflow_data=workflow_data.get('config', {}),
                    created_by=self.user
                )
                
                # Create workflow steps
                steps_data = workflow_data.get('steps', [])
                for step_data in steps_data:
                    step = WorkflowStep.objects.create(
                        workflow=workflow,
                        step_name=step_data.get('name'),
                        step_order=step_data.get('order'),
                        step_type=step_data.get('type', 'manual'),
                        step_config=step_data.get('config', {}),
                        is_required=step_data.get('required', True),
                        estimated_duration=step_data.get('estimated_duration')
                    )
                
                # Create workflow transitions
                transitions_data = workflow_data.get('transitions', [])
                for transition_data in transitions_data:
                    from_step = WorkflowStep.objects.get(
                        workflow=workflow,
                        step_name=transition_data.get('from_step')
                    )
                    to_step = WorkflowStep.objects.get(
                        workflow=workflow,
                        step_name=transition_data.get('to_step')
                    )
                    
                    WorkflowTransition.objects.create(
                        name=transition_data.get('name'),
                        transition_type=transition_data.get('type', 'forward'),
                        conditions=transition_data.get('conditions', {}),
                        from_step=from_step,
                        to_step=to_step
                    )
                
                self.logger.info(f"Workflow definition created: {workflow.name}")
                
                return {
                    'success': True,
                    'workflow_id': workflow.id,
                    'message': 'Workflow definition created successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create workflow definition: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create workflow definition'
            }
    
    def start_workflow_instance(self, workflow_id: int, instance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a new workflow instance
        
        Args:
            workflow_id: Workflow definition ID
            instance_data: Instance-specific data
            
        Returns:
            Dict containing instance creation result
        """
        try:
            with transaction.atomic():
                workflow = WorkflowDefinition.objects.get(id=workflow_id)
                
                # Create workflow instance
                instance = WorkflowInstance.objects.create(
                    instance_id=str(uuid.uuid4()),
                    workflow=workflow,
                    status='active',
                    current_step='start',
                    progress_percentage=0,
                    instance_data=instance_data,
                    initiated_by=self.user
                )
                
                # Get first step
                first_step = WorkflowStep.objects.filter(
                    workflow=workflow
                ).order_by('step_order').first()
                
                if first_step:
                    instance.current_step = first_step.step_name
                    instance.progress_percentage = (1 / workflow.steps.count()) * 100
                    instance.save()
                
                # Log workflow start
                WorkflowExecutionLog.objects.create(
                    workflow_instance=instance,
                    action='workflow_started',
                    action_data={'step': instance.current_step},
                    executed_by=self.user
                )
                
                self.logger.info(f"Workflow instance started: {instance.instance_id}")
                
                return {
                    'success': True,
                    'instance_id': instance.instance_id,
                    'workflow_name': workflow.name,
                    'current_step': instance.current_step,
                    'message': 'Workflow instance started successfully'
                }
                
        except WorkflowDefinition.DoesNotExist:
            return {
                'success': False,
                'error': 'Workflow definition not found',
                'message': 'Workflow definition not found'
            }
        except Exception as e:
            self.logger.error(f"Failed to start workflow instance: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to start workflow instance'
            }
    
    def execute_workflow_step(self, instance_id: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow step
        
        Args:
            instance_id: Workflow instance ID
            step_data: Step execution data
            
        Returns:
            Dict containing step execution result
        """
        try:
            with transaction.atomic():
                instance = WorkflowInstance.objects.get(instance_id=instance_id)
                
                if instance.status != 'active':
                    return {
                        'success': False,
                        'error': 'Workflow instance is not active',
                        'message': 'Cannot execute step on inactive workflow'
                    }
                
                current_step = WorkflowStep.objects.get(
                    workflow=instance.workflow,
                    step_name=instance.current_step
                )
                
                # Execute step based on type
                step_result = self._execute_step(current_step, step_data, instance)
                
                if step_result['success']:
                    # Move to next step
                    next_step = self._get_next_step(instance, current_step, step_result)
                    
                    if next_step:
                        instance.current_step = next_step.step_name
                        instance.progress_percentage = self._calculate_progress(instance)
                        instance.save()
                        
                        # Log step completion
                        WorkflowExecutionLog.objects.create(
                            workflow_instance=instance,
                            action='step_completed',
                            action_data={
                                'step': current_step.step_name,
                                'result': step_result,
                                'next_step': next_step.step_name
                            },
                            executed_by=self.user
                        )
                        
                        message = f"Step '{current_step.step_name}' completed, moved to '{next_step.step_name}'"
                    else:
                        # Workflow completed
                        instance.status = 'completed'
                        instance.completed_at = timezone.now()
                        instance.progress_percentage = 100
                        instance.save()
                        
                        # Log workflow completion
                        WorkflowExecutionLog.objects.create(
                            workflow_instance=instance,
                            action='workflow_completed',
                            action_data={'final_step': current_step.step_name},
                            executed_by=self.user
                        )
                        
                        message = f"Workflow completed successfully"
                else:
                    # Step failed
                    instance.status = 'paused'
                    instance.save()
                    
                    # Log step failure
                    WorkflowExecutionLog.objects.create(
                        workflow_instance=instance,
                        action='step_failed',
                        action_data={
                            'step': current_step.step_name,
                            'error': step_result.get('error', 'Unknown error')
                        },
                        executed_by=self.user
                    )
                    
                    message = f"Step '{current_step.step_name}' failed: {step_result.get('error')}"
                
                return {
                    'success': step_result['success'],
                    'instance_id': instance_id,
                    'step': current_step.step_name,
                    'result': step_result,
                    'next_step': instance.current_step if instance.status == 'active' else None,
                    'status': instance.status,
                    'progress': instance.progress_percentage,
                    'message': message
                }
                
        except WorkflowInstance.DoesNotExist:
            return {
                'success': False,
                'error': 'Workflow instance not found',
                'message': 'Workflow instance not found'
            }
        except Exception as e:
            self.logger.error(f"Failed to execute workflow step: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute workflow step'
            }
    
    def _execute_step(self, step: WorkflowStep, step_data: Dict[str, Any], 
                     instance: WorkflowInstance) -> Dict[str, Any]:
        """Execute a specific workflow step"""
        try:
            step_type = step.step_type
            step_config = step.step_config
            
            if step_type == 'manual':
                return self._execute_manual_step(step, step_data, instance)
            elif step_type == 'automated':
                return self._execute_automated_step(step, step_data, instance)
            elif step_type == 'decision':
                return self._execute_decision_step(step, step_data, instance)
            elif step_type == 'notification':
                return self._execute_notification_step(step, step_data, instance)
            else:
                return {
                    'success': False,
                    'error': f'Unknown step type: {step_type}'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to execute step {step.step_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_manual_step(self, step: WorkflowStep, step_data: Dict[str, Any], 
                           instance: WorkflowInstance) -> Dict[str, Any]:
        """Execute a manual step"""
        # Manual steps require user interaction
        # For now, we'll simulate completion
        return {
            'success': True,
            'message': f"Manual step '{step.step_name}' requires user action",
            'data': step_data
        }
    
    def _execute_automated_step(self, step: WorkflowStep, step_data: Dict[str, Any], 
                              instance: WorkflowInstance) -> Dict[str, Any]:
        """Execute an automated step"""
        try:
            # Get automation configuration
            automation_config = step.step_config.get('automation', {})
            automation_type = automation_config.get('type')
            
            if automation_type == 'data_processing':
                result = self._process_data(step_data, automation_config)
            elif automation_type == 'notification':
                result = self._send_notification(step_data, automation_config)
            elif automation_type == 'approval':
                result = self._create_approval_request(step_data, automation_config, instance)
            else:
                result = {'success': True, 'message': 'Automation completed'}
            
            return {
                'success': result.get('success', True),
                'message': result.get('message', 'Automation completed'),
                'data': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_decision_step(self, step: WorkflowStep, step_data: Dict[str, Any], 
                             instance: WorkflowInstance) -> Dict[str, Any]:
        """Execute a decision step"""
        try:
            # Get decision configuration
            decision_config = step.step_config.get('decision', {})
            decision_type = decision_config.get('type')
            
            if decision_type == 'conditional':
                result = self._evaluate_condition(step_data, decision_config)
            elif decision_type == 'approval':
                result = self._evaluate_approval(step_data, decision_config)
            else:
                result = {'decision': 'continue', 'message': 'Decision completed'}
            
            return {
                'success': True,
                'message': 'Decision step completed',
                'data': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_notification_step(self, step: WorkflowStep, step_data: Dict[str, Any], 
                                 instance: WorkflowInstance) -> Dict[str, Any]:
        """Execute a notification step"""
        try:
            # Get notification configuration
            notification_config = step.step_config.get('notification', {})
            
            # Send notification (placeholder implementation)
            notification_sent = self._send_workflow_notification(
                step_data, notification_config, instance
            )
            
            return {
                'success': notification_sent,
                'message': 'Notification sent' if notification_sent else 'Notification failed',
                'data': {'notification_sent': notification_sent}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_next_step(self, instance: WorkflowInstance, current_step: WorkflowStep, 
                       step_result: Dict[str, Any]) -> Optional[WorkflowStep]:
        """Get the next step in the workflow"""
        try:
            # Get outgoing transitions from current step
            transitions = WorkflowTransition.objects.filter(
                from_step=current_step,
                is_active=True
            )
            
            if not transitions:
                return None
            
            # Evaluate transition conditions
            for transition in transitions:
                if self._evaluate_transition_conditions(transition, step_result):
                    return transition.to_step
            
            # If no conditions match, use default transition
            default_transition = transitions.filter(transition_type='forward').first()
            if default_transition:
                return default_transition.to_step
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get next step: {str(e)}")
            return None
    
    def _evaluate_transition_conditions(self, transition: WorkflowTransition, 
                                      step_result: Dict[str, Any]) -> bool:
        """Evaluate transition conditions"""
        try:
            conditions = transition.conditions
            
            if not conditions:
                return True
            
            # Simple condition evaluation (can be enhanced)
            for condition in conditions:
                field = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if not self._evaluate_condition(field, operator, value, step_result):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate transition conditions: {str(e)}")
            return False
    
    def _evaluate_condition(self, field: str, operator: str, value: Any, 
                          data: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        try:
            actual_value = data.get(field)
            
            if operator == 'equals':
                return actual_value == value
            elif operator == 'not_equals':
                return actual_value != value
            elif operator == 'greater_than':
                return actual_value > value
            elif operator == 'less_than':
                return actual_value < value
            elif operator == 'contains':
                return value in str(actual_value)
            elif operator == 'not_contains':
                return value not in str(actual_value)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to evaluate condition: {str(e)}")
            return False
    
    def _calculate_progress(self, instance: WorkflowInstance) -> float:
        """Calculate workflow progress percentage"""
        try:
            total_steps = instance.workflow.steps.count()
            if total_steps == 0:
                return 0
            
            # Find current step position
            current_step = WorkflowStep.objects.get(
                workflow=instance.workflow,
                step_name=instance.current_step
            )
            
            progress = (current_step.step_order / total_steps) * 100
            return min(progress, 100)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate progress: {str(e)}")
            return 0
    
    def get_workflow_status(self, instance_id: str) -> Dict[str, Any]:
        """Get workflow instance status"""
        try:
            instance = WorkflowInstance.objects.get(instance_id=instance_id)
            
            # Get workflow steps
            steps = []
            for step in instance.workflow.steps.all().order_by('step_order'):
                steps.append({
                    'name': step.step_name,
                    'type': step.step_type,
                    'order': step.step_order,
                    'is_current': step.step_name == instance.current_step,
                    'is_completed': step.step_order < instance.workflow.steps.filter(
                        step_name=instance.current_step
                    ).first().step_order if instance.current_step else False
                })
            
            # Get execution log
            execution_log = WorkflowExecutionLog.objects.filter(
                workflow_instance=instance
            ).order_by('-timestamp')[:10]
            
            log_entries = []
            for entry in execution_log:
                log_entries.append({
                    'action': entry.action,
                    'timestamp': entry.timestamp,
                    'executed_by': entry.executed_by.username,
                    'data': entry.action_data
                })
            
            return {
                'success': True,
                'instance_id': instance_id,
                'workflow_name': instance.workflow.name,
                'status': instance.status,
                'current_step': instance.current_step,
                'progress': instance.progress_percentage,
                'started_at': instance.started_at,
                'completed_at': instance.completed_at,
                'steps': steps,
                'execution_log': log_entries
            }
            
        except WorkflowInstance.DoesNotExist:
            return {
                'success': False,
                'error': 'Workflow instance not found',
                'message': 'Workflow instance not found'
            }
        except Exception as e:
            self.logger.error(f"Failed to get workflow status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get workflow status'
            }
    
    def get_user_workflows(self, user: User = None) -> Dict[str, Any]:
        """Get workflows for a specific user"""
        try:
            if user is None:
                user = self.user
            
            # Get workflow instances where user is involved
            instances = WorkflowInstance.objects.filter(
                initiated_by=user
            ).order_by('-started_at')
            
            workflow_list = []
            for instance in instances:
                workflow_list.append({
                    'instance_id': instance.instance_id,
                    'workflow_name': instance.workflow.name,
                    'status': instance.status,
                    'current_step': instance.current_step,
                    'progress': instance.progress_percentage,
                    'started_at': instance.started_at,
                    'completed_at': instance.completed_at
                })
            
            return {
                'success': True,
                'user': user.username,
                'workflows': workflow_list,
                'total_workflows': len(workflow_list)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user workflows: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get user workflows'
            }
    
    # Placeholder methods for automation
    def _process_data(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Process data based on automation configuration"""
        return {'success': True, 'message': 'Data processing completed'}
    
    def _send_notification(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification based on automation configuration"""
        return {'success': True, 'message': 'Notification sent'}
    
    def _create_approval_request(self, data: Dict[str, Any], config: Dict[str, Any], 
                                instance: WorkflowInstance) -> Dict[str, Any]:
        """Create approval request based on automation configuration"""
        return {'success': True, 'message': 'Approval request created'}
    
    def _evaluate_approval(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate approval decision"""
        return {'decision': 'approved', 'message': 'Approval granted'}
    
    def _send_workflow_notification(self, data: Dict[str, Any], config: Dict[str, Any], 
                                   instance: WorkflowInstance) -> bool:
        """Send workflow notification"""
        return True
