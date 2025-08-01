"""
Workflow Engine

Main workflow execution engine that orchestrates workflow instances,
state transitions, and integrates with Odoo client.
"""

from typing import Dict, Any, List, Optional
from django.contrib.auth.models import User
from django.utils import timezone
from .workflow_models import WorkflowDefinition, WorkflowInstance, WorkflowTransition, WorkflowExecutionLog
from .workflow_actions import WorkflowActionRegistry
from ..services.odoo_client import odoo_client
import logging

logger = logging.getLogger('fayvad_core.workflows')


class WorkflowEngine:
    """
    Main workflow execution engine
    """
    
    def __init__(self):
        self.odoo_client = odoo_client
    
    def create_workflow_instance(self, workflow_definition: WorkflowDefinition, 
                                record_id: int, model_name: str, database: str,
                                user: User, context: Dict[str, Any] = None) -> WorkflowInstance:
        """
        Create a new workflow instance
        """
        try:
            # Check if instance already exists
            existing_instance = WorkflowInstance.objects.filter(
                workflow_definition=workflow_definition,
                odoo_record_id=record_id,
                odoo_model_name=model_name,
                database__name=database
            ).first()
            
            if existing_instance:
                logger.info(f"Workflow instance already exists: {existing_instance.id}")
                return existing_instance
            
            # Create new instance
            instance = WorkflowInstance.objects.create(
                workflow_definition=workflow_definition,
                odoo_record_id=record_id,
                odoo_model_name=model_name,
                database_id=database,
                current_state=workflow_definition.initial_state,
                context_data=context or {},
                initiated_by=user
            )
            
            logger.info(f"Created workflow instance: {instance.id}")
            return instance
            
        except Exception as e:
            logger.error(f"Error creating workflow instance: {str(e)}")
            raise
    
    def execute_workflow(self, instance: WorkflowInstance, user: User = None) -> Dict[str, Any]:
        """
        Execute a workflow instance
        """
        try:
            if instance.status != 'running':
                return {
                    'success': False,
                    'error': f'Workflow is not in running state: {instance.status}'
                }
            
            # Get workflow definition
            definition = instance.workflow_definition
            
            # Build execution context
            context = self._build_execution_context(instance, user)
            
            # Execute current state actions
            state_result = self._execute_state_actions(definition, instance.current_state, context, user)
            
            if not state_result['success']:
                # Log failure
                self._log_execution(instance, 'state_actions', 'failed', context, state_result)
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
                        # Continue execution in new state
                        return self.execute_workflow(instance, user)
                    else:
                        return transition_result
            
            # Log successful execution
            self._log_execution(instance, 'state_actions', 'success', context, state_result)
            
            return {
                'success': True,
                'message': 'Workflow executed successfully',
                'data': {
                    'current_state': instance.current_state,
                    'available_transitions': [t.name for t in available_transitions],
                    'requires_approval': any(t.requires_approval for t in available_transitions)
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_transition(self, instance: WorkflowInstance, transition_name: str, 
                          user: User, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a specific transition
        """
        try:
            # Find transition
            transition = WorkflowTransition.objects.filter(
                workflow_definition=instance.workflow_definition,
                from_state=instance.current_state,
                name=transition_name
            ).first()
            
            if not transition:
                return {
                    'success': False,
                    'error': f'Transition not found: {transition_name}'
                }
            
            # Check permissions
            if not self._check_transition_permissions(transition, user):
                return {
                    'success': False,
                    'error': 'Insufficient permissions for transition'
                }
            
            # Build context if not provided
            if context is None:
                context = self._build_execution_context(instance, user)
            
            # Execute transition
            return self._execute_transition(instance, transition, context, user)
            
        except Exception as e:
            logger.error(f"Error executing transition: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_execution_context(self, instance: WorkflowInstance, user: User) -> Dict[str, Any]:
        """
        Build execution context for workflow
        """
        # Get record data from Odoo
        try:
            record_data = self.odoo_client.get_record(
                model_name=instance.odoo_model_name,
                record_id=instance.odoo_record_id,
                token=instance.context_data.get('token'),
                database=instance.database.name
            )
        except Exception as e:
            logger.warning(f"Could not fetch record data: {str(e)}")
            record_data = {}
        
        return {
            'record_id': instance.odoo_record_id,
            'model_name': instance.odoo_model_name,
            'database': instance.database.name,
            'token': instance.context_data.get('token'),
            'record_data': record_data,
            'workflow_data': instance.workflow_data,
            'context_data': instance.context_data,
            'current_state': instance.current_state,
            'user': user,
            'instance_id': str(instance.id)
        }
    
    def _execute_state_actions(self, definition: WorkflowDefinition, state: str, 
                              context: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Execute actions for current state
        """
        try:
            states_config = definition.states or {}
            state_config = states_config.get(state, {})
            actions = state_config.get('actions', [])
            
            results = []
            
            for action_config in actions:
                action_type = action_config.get('type')
                if not action_type:
                    continue
                
                try:
                    action = WorkflowActionRegistry.get_action(action_type, action_config)
                    result = action.execute(context, user)
                    results.append({
                        'action': action.name,
                        'result': result
                    })
                    
                    # Update workflow data with action output
                    if result.get('success') and result.get('data'):
                        context['workflow_data'].update(result['data'])
                    
                except Exception as e:
                    logger.error(f"Action execution failed: {str(e)}")
                    results.append({
                        'action': action_config.get('name', 'unknown'),
                        'result': {'success': False, 'error': str(e)}
                    })
            
            # Check if any actions failed
            failed_actions = [r for r in results if not r['result'].get('success')]
            
            if failed_actions:
                return {
                    'success': False,
                    'error': 'Some actions failed',
                    'data': {'failed_actions': failed_actions}
                }
            
            return {
                'success': True,
                'data': {'executed_actions': results}
            }
            
        except Exception as e:
            logger.error(f"Error executing state actions: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_available_transitions(self, instance: WorkflowInstance, 
                                  context: Dict[str, Any]) -> List[WorkflowTransition]:
        """
        Get available transitions for current state
        """
        transitions = WorkflowTransition.objects.filter(
            workflow_definition=instance.workflow_definition,
            from_state=instance.current_state
        ).order_by('order')
        
        available_transitions = []
        
        for transition in transitions:
            if self._check_transition_conditions(transition, context):
                available_transitions.append(transition)
        
        return available_transitions
    
    def _check_transition_conditions(self, transition: WorkflowTransition, 
                                   context: Dict[str, Any]) -> bool:
        """
        Check if transition conditions are met
        """
        conditions = transition.conditions or {}
        
        for field, condition in conditions.items():
            if field == 'field_value':
                field_name = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if field_name in context.get('record_data', {}):
                    field_value = context['record_data'][field_name]
                    
                    if operator == 'equals' and field_value != value:
                        return False
                    elif operator == 'not_equals' and field_value == value:
                        return False
                    elif operator == 'in' and field_value not in value:
                        return False
                    elif operator == 'not_in' and field_value in value:
                        return False
                    elif operator == 'greater_than' and field_value <= value:
                        return False
                    elif operator == 'less_than' and field_value >= value:
                        return False
        
        return True
    
    def _check_transition_permissions(self, transition: WorkflowTransition, user: User) -> bool:
        """
        Check if user has permissions for transition
        """
        required_roles = transition.required_roles or []
        
        if not required_roles:
            return True
        
        user_groups = set(user.groups.values_list('name', flat=True))
        return any(role in user_groups for role in required_roles)
    
    def _execute_transition(self, instance: WorkflowInstance, transition: WorkflowTransition,
                          context: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Execute a transition
        """
        try:
            # Execute transition actions
            actions = transition.actions or []
            
            for action_config in actions:
                action_type = action_config.get('type')
                if action_type:
                    action = WorkflowActionRegistry.get_action(action_type, action_config)
                    result = action.execute(context, user)
                    
                    if not result.get('success'):
                        return result
            
            # Update instance state
            instance.current_state = transition.to_state
            instance.workflow_data = context['workflow_data']
            instance.last_executed_at = timezone.now()
            instance.save()
            
            # Log transition
            self._log_execution(instance, 'transition', 'success', context, {
                'from_state': transition.from_state,
                'to_state': transition.to_state,
                'transition_name': transition.name
            })
            
            return {
                'success': True,
                'message': f'Transitioned to {transition.to_state}',
                'data': {
                    'from_state': transition.from_state,
                    'to_state': transition.to_state
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing transition: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _log_execution(self, instance: WorkflowInstance, step_name: str, status: str,
                      context: Dict[str, Any], result: Dict[str, Any]):
        """
        Log workflow execution
        """
        try:
            WorkflowExecutionLog.objects.create(
                workflow_instance=instance,
                step_name=step_name,
                step_type='workflow_step',
                status=status,
                input_data=context,
                output_data=result,
                executed_by=context.get('user')
            )
        except Exception as e:
            logger.error(f"Error logging execution: {str(e)}")
    
    def get_workflow_status(self, instance: WorkflowInstance) -> Dict[str, Any]:
        """
        Get comprehensive workflow status
        """
        available_transitions = self._get_available_transitions(
            instance, 
            self._build_execution_context(instance, None)
        )
        
        return {
            'instance_id': str(instance.id),
            'workflow_name': instance.workflow_definition.name,
            'current_state': instance.current_state,
            'status': instance.status,
            'available_transitions': [
                {
                    'name': t.name,
                    'to_state': t.to_state,
                    'requires_approval': t.requires_approval,
                    'button_text': t.button_text,
                    'button_style': t.button_style
                }
                for t in available_transitions
            ],
            'approval_status': instance.approval_status,
            'started_at': instance.started_at,
            'last_executed_at': instance.last_executed_at,
            'completed_at': instance.completed_at
        } 