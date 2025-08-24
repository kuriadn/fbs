"""
FBS App Workflow Service

Service for managing business workflow automation.
"""

import logging
from typing import Dict, Any, List, Optional
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger('fbs_app')


class WorkflowService:
    """Service for managing business workflows and process automation"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        self.fbs_config = getattr(settings, 'FBS_APP', {})
    
    def create_workflow_instance(self, workflow_definition_id: int, record_id: int, 
                                model_name: str, database_name: str, user: User,
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new workflow instance"""
        try:
            from ..models import WorkflowDefinition, WorkflowInstance
            
            # Get workflow definition
            try:
                workflow_def = WorkflowDefinition.objects.get(id=workflow_definition_id)
            except WorkflowDefinition.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Workflow definition not found',
                    'message': f'Workflow definition {workflow_definition_id} does not exist'
                }
            
            # Check if instance already exists
            existing_instance = WorkflowInstance.objects.filter(
                workflow_definition=workflow_def,
                odoo_record_id=record_id,
                odoo_model_name=model_name,
                database__name=database_name
            ).first()
            
            if existing_instance:
                return {
                    'success': True,
                    'data': {
                        'instance': existing_instance,
                        'message': 'Workflow instance already exists'
                    },
                    'message': 'Workflow instance already exists'
                }
            
            # Create new instance
            instance = WorkflowInstance.objects.create(
                workflow_definition=workflow_def,
                odoo_record_id=record_id,
                odoo_model_name=model_name,
                database_name=database_name,
                current_state=workflow_def.initial_state,
                context_data=context or {},
                initiated_by=user,
                status='running'
            )
            
            logger.info(f"Created workflow instance: {instance.id}")
            
            return {
                'success': True,
                'data': {
                    'instance': instance,
                    'workflow_definition': workflow_def
                },
                'message': 'Workflow instance created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating workflow instance: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create workflow instance'
            }
    
    def execute_workflow(self, instance_id: int, user: User = None) -> Dict[str, Any]:
        """Execute a workflow instance"""
        try:
            from ..models import WorkflowInstance, WorkflowTransition
            
            # Get workflow instance
            try:
                instance = WorkflowInstance.objects.get(id=instance_id)
            except WorkflowInstance.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Workflow instance not found',
                    'message': f'Workflow instance {instance_id} does not exist'
                }
            
            if instance.status != 'running':
                return {
                    'success': False,
                    'error': 'Workflow is not in running state',
                    'message': f'Workflow status is {instance.status}'
                }
            
            # Get workflow definition
            definition = instance.workflow_definition
            
            # Build execution context
            context = self._build_execution_context(instance, user)
            
            # Execute current state actions
            state_result = self._execute_state_actions(definition, instance.current_state, context, user)
            
            if not state_result['success']:
                return state_result
            
            # Check for available transitions
            available_transitions = self._get_available_transitions(instance, context)
            
            if available_transitions:
                # Auto-transition if only one available and no approval required
                auto_transitions = [t for t in available_transitions if not t.requires_approval]
                
                if len(auto_transitions) == 1:
                    transition = auto_transitions[0]
                    transition_result = self._execute_transition(instance, transition, context, user)
                    
                    if transition_result['success']:
                        return {
                            'success': True,
                            'data': {
                                'instance': instance,
                                'transition': transition,
                                'new_state': instance.current_state
                            },
                            'message': 'Workflow transitioned automatically'
                        }
            
            return {
                'success': True,
                'data': {
                    'instance': instance,
                    'available_transitions': available_transitions
                },
                'message': 'Workflow executed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute workflow'
            }
    
    def execute_transition(self, instance_id: int, transition_id: int, 
                          user: User, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow transition"""
        try:
            from ..models import WorkflowInstance, WorkflowTransition
            
            # Get workflow instance and transition
            try:
                instance = WorkflowInstance.objects.get(id=instance_id)
                transition = WorkflowTransition.objects.get(id=transition_id)
            except (WorkflowInstance.DoesNotExist, WorkflowTransition.DoesNotExist):
                return {
                    'success': False,
                    'error': 'Instance or transition not found',
                    'message': 'Workflow instance or transition does not exist'
                }
            
            # Validate transition
            if not self._can_execute_transition(instance, transition, user):
                return {
                    'success': False,
                    'error': 'Transition not allowed',
                    'message': 'Cannot execute this transition'
                }
            
            # Execute transition
            result = self._execute_transition(instance, transition, context or {}, user)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing transition: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute transition'
            }
    
    def get_workflow_status(self, instance_id: int) -> Dict[str, Any]:
        """Get current status of a workflow instance"""
        try:
            from ..models import WorkflowInstance
            
            try:
                instance = WorkflowInstance.objects.get(id=instance_id)
            except WorkflowInstance.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Workflow instance not found',
                    'message': f'Workflow instance {instance_id} does not exist'
                }
            
            return {
                'success': True,
                'data': {
                    'instance_id': instance.id,
                    'current_state': instance.current_state,
                    'status': instance.status,
                    'initiated_by': instance.initiated_by.username if instance.initiated_by else None,
                    'created_at': instance.created_at,
                    'updated_at': instance.updated_at,
                    'context_data': instance.context_data
                },
                'message': 'Workflow status retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get workflow status'
            }
    
    def _build_execution_context(self, instance, user: User) -> Dict[str, Any]:
        """Build execution context for workflow"""
        context = {
            'instance': instance,
            'user': user,
            'current_state': instance.current_state,
            'record_id': instance.odoo_record_id,
            'model_name': instance.odoo_model_name,
            'database_name': instance.database_name,
            'timestamp': timezone.now(),
            'context_data': instance.context_data or {}
        }
        return context
    
    def _execute_state_actions(self, definition, current_state: str, 
                              context: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Execute actions for current state"""
        try:
            # Get state actions from definition
            state_actions = definition.get_state_actions(current_state)
            
            if not state_actions:
                return {'success': True, 'message': 'No actions for current state'}
            
            # Execute each action
            for action in state_actions:
                action_result = self._execute_action(action, context, user)
                if not action_result['success']:
                    return action_result
            
            return {'success': True, 'message': 'State actions executed successfully'}
            
        except Exception as e:
            logger.error(f"Error executing state actions: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute state actions'
            }
    
    def _get_available_transitions(self, instance, context: Dict[str, Any]) -> List:
        """Get available transitions for current state"""
        try:
            from ..models import WorkflowTransition
            
            # Get transitions from current state
            transitions = WorkflowTransition.objects.filter(
                workflow_definition=instance.workflow_definition,
                from_state=instance.current_state,
                active=True
            )
            
            # Filter by conditions
            available_transitions = []
            for transition in transitions:
                if self._evaluate_transition_conditions(transition, context):
                    available_transitions.append(transition)
            
            return available_transitions
            
        except Exception as e:
            logger.error(f"Error getting available transitions: {str(e)}")
            return []
    
    def _can_execute_transition(self, instance, transition, user: User) -> bool:
        """Check if transition can be executed"""
        try:
            # Check if transition is active
            if not transition.active:
                return False
            
            # Check if user has permission
            if transition.requires_approval and not self._user_can_approve(transition, user):
                return False
            
            # Check if transition is from current state
            if transition.from_state != instance.current_state:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking transition execution: {str(e)}")
            return False
    
    def _execute_transition(self, instance, transition, context: Dict[str, Any], 
                           user: User) -> Dict[str, Any]:
        """Execute a workflow transition"""
        try:
            # Update instance state
            instance.current_state = transition.to_state
            instance.updated_at = timezone.now()
            instance.save(update_fields=['current_state', 'updated_at'])
            
            # Execute transition actions
            if transition.actions:
                for action in transition.actions:
                    action_result = self._execute_action(action, context, user)
                    if not action_result['success']:
                        return action_result
            
            logger.info(f"Workflow {instance.id} transitioned from {transition.from_state} to {transition.to_state}")
            
            return {
                'success': True,
                'data': {
                    'instance': instance,
                    'transition': transition,
                    'new_state': transition.to_state
                },
                'message': 'Transition executed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error executing transition: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute transition'
            }
    
    def _execute_action(self, action, context: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Execute a workflow action"""
        try:
            # This is a placeholder - in the full implementation,
            # you would have action types and execution logic
            logger.info(f"Executing action: {action}")
            return {'success': True, 'message': 'Action executed'}
            
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute action'
            }
    
    def _evaluate_transition_conditions(self, transition, context: Dict[str, Any]) -> bool:
        """Evaluate transition conditions"""
        try:
            # This is a placeholder - in the full implementation,
            # you would evaluate conditions based on context
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating transition conditions: {str(e)}")
            return False
    
    def _user_can_approve(self, transition, user: User) -> bool:
        """Check if user can approve transition"""
        try:
            # This is a placeholder - in the full implementation,
            # you would check user permissions
            return user.is_staff if user else False
            
        except Exception as e:
            logger.error(f"Error checking user approval permissions: {str(e)}")
            return False
    
    # Missing methods that the interface expects
    def create_workflow_definition(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow definition"""
        try:
            from ..models import WorkflowDefinition
            
            workflow_def = WorkflowDefinition.objects.create(
                name=workflow_data['name'],
                workflow_type=workflow_data.get('workflow_type', 'general'),
                description=workflow_data.get('description', ''),
                version=workflow_data.get('version', '1.0'),
                is_active=workflow_data.get('is_active', True),
                is_template=workflow_data.get('is_template', False),
                trigger_conditions=workflow_data.get('trigger_conditions', {}),
                workflow_data=workflow_data.get('workflow_data', {}),
                estimated_duration=workflow_data.get('estimated_duration'),
                created_by=workflow_data.get('created_by'),
                solution_name=self.solution_name
            )
            
            return {
                'success': True,
                'data': {
                    'id': workflow_def.id,
                    'name': workflow_def.name,
                    'workflow_type': workflow_def.workflow_type,
                    'description': workflow_def.description,
                    'version': workflow_def.version,
                    'is_active': workflow_def.is_active,
                    'is_template': workflow_def.is_template
                }
            }
        except Exception as e:
            logger.error(f"Error creating workflow definition: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_workflow_definitions(self, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all workflow definitions or by type"""
        try:
            from ..models import WorkflowDefinition
            
            query = {'is_active': True, 'solution_name': self.solution_name}
            if workflow_type:
                query['workflow_type'] = workflow_type
            
            workflows = WorkflowDefinition.objects.filter(**query)
            workflow_list = []
            
            for workflow in workflows:
                workflow_list.append({
                    'id': workflow.id,
                    'name': workflow.name,
                    'workflow_type': workflow.workflow_type,
                    'description': workflow.description,
                    'version': workflow.version,
                    'is_active': workflow.is_active,
                    'is_template': workflow.is_template
                })
            
            return {
                'success': True,
                'data': workflow_list,
                'count': len(workflow_list)
            }
        except Exception as e:
            logger.error(f"Error getting workflow definitions: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def start_workflow(self, workflow_definition_id: int, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new workflow instance"""
        try:
            from ..models import WorkflowDefinition, WorkflowInstance
            
            workflow_def = WorkflowDefinition.objects.get(id=workflow_definition_id)
            
            # Create instance with correct fields
            instance = WorkflowInstance.objects.create(
                workflow_definition=workflow_def,
                business_id=initial_data.get('business_id', 'default'),
                status='active',
                workflow_data=initial_data.get('workflow_data', {}),
                notes=initial_data.get('notes', ''),
                solution_name=self.solution_name
            )
            
            return {
                'success': True,
                'data': {
                    'instance': {
                        'id': instance.id,
                        'status': instance.status,
                        'business_id': instance.business_id
                    },
                    'workflow_definition': {
                        'id': workflow_def.id,
                        'name': workflow_def.name,
                        'workflow_type': workflow_def.workflow_type
                    }
                }
            }
        except WorkflowDefinition.DoesNotExist:
            return {'success': False, 'error': 'Workflow definition not found'}
        except Exception as e:
            logger.error(f"Error starting workflow: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_active_workflows(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get active workflow instances"""
        try:
            from ..models import WorkflowInstance
            
            query = {'status': 'active'}
            if user_id:
                query['current_user_id'] = user_id
            
            instances = WorkflowInstance.objects.filter(**query)
            instance_list = []
            
            for instance in instances:
                instance_list.append({
                    'id': instance.id,
                    'workflow_name': instance.workflow_definition.name,
                    'business_id': instance.business_id,
                    'status': instance.status,
                    'started_at': instance.started_at.isoformat()
                })
            
            return {
                'success': True,
                'data': instance_list,
                'count': len(instance_list)
            }
        except Exception as e:
            logger.error(f"Error getting active workflows: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def execute_workflow_step(self, workflow_instance_id: int, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow step"""
        try:
            from ..models import WorkflowInstance
            
            instance = WorkflowInstance.objects.get(id=workflow_instance_id)
            
            # Update workflow data with step execution info
            current_workflow_data = instance.workflow_data or {}
            step_execution = {
                'step_name': step_data.get('step_name', 'unknown'),
                'action': step_data.get('action', 'unknown'),
                'executed_at': timezone.now().isoformat(),
                'user': str(step_data.get('user', 'unknown'))
            }
            
            if 'step_executions' not in current_workflow_data:
                current_workflow_data['step_executions'] = []
            
            current_workflow_data['step_executions'].append(step_execution)
            instance.workflow_data = current_workflow_data
            instance.save()
            
            return {
                'success': True,
                'data': {
                    'id': instance.id,
                    'step_executed': step_execution,
                    'workflow_data': current_workflow_data
                }
            }
        except WorkflowInstance.DoesNotExist:
            return {'success': False, 'error': 'Workflow instance not found'}
        except Exception as e:
            logger.error(f"Error executing workflow step: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_approval_request(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an approval request"""
        try:
            from ..models import ApprovalRequest
            
            approval = ApprovalRequest.objects.create(
                title=approval_data['title'],
                approval_type=approval_data.get('approval_type', 'general'),
                description=approval_data.get('description', ''),
                requester_id=approval_data.get('requester_id', 1),
                approver_id=approval_data.get('approver_id'),
                request_data=approval_data.get('request_data', {}),
                status='pending'
            )
            
            return {
                'success': True,
                'data': {
                    'id': approval.id,
                    'title': approval.title,
                    'status': approval.status
                }
            }
        except Exception as e:
            logger.error(f"Error creating approval request: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_approval_requests(self, status: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get approval requests"""
        try:
            from ..models import ApprovalRequest
            
            query = {}
            if status:
                query['status'] = status
            if user_id:
                query['requester_id'] = user_id
            
            approvals = ApprovalRequest.objects.filter(**query)
            approval_list = []
            
            for approval in approvals:
                approval_list.append({
                    'id': approval.id,
                    'title': approval.title,
                    'approval_type': approval.approval_type,
                    'status': approval.status,
                    'requester_id': approval.requester.id,
                    'approver_id': approval.approver.id if approval.approver else None,
                    'created_at': approval.created_at.isoformat()
                })
            
            return {
                'success': True,
                'data': approval_list,
                'count': len(approval_list)
            }
        except Exception as e:
            logger.error(f"Error getting approval requests: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def respond_to_approval(self, approval_id: int, response: str, comments: str = '') -> Dict[str, Any]:
        """Respond to an approval request"""
        try:
            from ..models import ApprovalRequest, ApprovalResponse
            
            approval = ApprovalRequest.objects.get(id=approval_id)
            
            # Create response
            approval_response = ApprovalResponse.objects.create(
                approval_request=approval,
                responder_id=approval.approver_id,
                response=response,
                comments=comments
            )
            
            # Update approval status
            approval.status = 'approved' if response == 'approve' else 'rejected'
            approval.save()
            
            return {
                'success': True,
                'data': {
                    'id': approval_response.id,
                    'response': response,
                    'status': approval.status
                }
            }
        except ApprovalRequest.DoesNotExist:
            return {'success': False, 'error': 'Approval request not found'}
        except Exception as e:
            logger.error(f"Error responding to approval: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_workflow_analytics(self, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow analytics and metrics"""
        try:
            from ..models import WorkflowInstance, WorkflowDefinition
            
            query = {}
            if workflow_type:
                query['workflow_definition__workflow_type'] = workflow_type
            
            instances = WorkflowInstance.objects.filter(**query)
            
            # Simple analytics
            total_instances = instances.count()
            running_instances = instances.filter(status='running').count()
            completed_instances = instances.filter(status='completed').count()
            
            return {
                'success': True,
                'data': {
                    'total_instances': total_instances,
                    'running_instances': running_instances,
                    'completed_instances': completed_instances,
                    'completion_rate': (completed_instances / total_instances * 100) if total_instances > 0 else 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting workflow analytics: {str(e)}")
            return {'success': False, 'error': str(e)}
