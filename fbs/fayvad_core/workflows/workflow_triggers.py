"""
Workflow Triggers

System for automatically triggering workflows based on Odoo events and conditions.
This provides the automation layer that connects Odoo events to workflow execution.
"""

from typing import Dict, Any, List, Optional
from django.contrib.auth.models import User
from django.utils import timezone
from .workflow_models import WorkflowDefinition, WorkflowInstance
from .workflow_engine import WorkflowEngine
from ..services.odoo_client import odoo_client
import logging

logger = logging.getLogger('fayvad_core.workflows.triggers')

workflow_engine = WorkflowEngine()


class WorkflowTrigger:
    """
    Base class for workflow triggers
    """
    
    def __init__(self, trigger_config: Dict[str, Any]):
        self.config = trigger_config
        self.name = trigger_config.get('name', self.__class__.__name__)
    
    def should_trigger(self, event_data: Dict[str, Any]) -> bool:
        """
        Check if this trigger should fire based on event data
        """
        raise NotImplementedError
    
    def execute(self, event_data: Dict[str, Any], user: User = None) -> Dict[str, Any]:
        """
        Execute the trigger and start workflows
        """
        raise NotImplementedError


class RecordCreateTrigger(WorkflowTrigger):
    """Trigger workflows on record creation"""
    
    def should_trigger(self, event_data: Dict[str, Any]) -> bool:
        """Check if record creation should trigger workflow"""
        event_type = event_data.get('event_type')
        return event_type == 'create'
    
    def execute(self, event_data: Dict[str, Any], user: User = None) -> Dict[str, Any]:
        """Execute workflows for record creation"""
        try:
            model_name = event_data.get('model_name')
            record_id = event_data.get('record_id')
            database = event_data.get('database')
            
            if not all([model_name, record_id, database]):
                return {
                    'success': False,
                    'error': 'Missing required event data'
                }
            
            # Find applicable workflow definitions
            workflows = WorkflowDefinition.objects.filter(
                model_name=model_name,
                database__name=database,
                trigger_type='on_create',
                active=True
            )
            
            triggered_workflows = []
            
            for workflow in workflows:
                # Check trigger conditions
                if self._check_conditions(workflow.trigger_conditions, event_data):
                    # Create workflow instance
                    instance = workflow_engine.create_workflow_instance(
                        workflow_definition=workflow,
                        record_id=record_id,
                        model_name=model_name,
                        database=database,
                        user=user,
                        context=event_data
                    )
                    
                    # Execute workflow
                    result = workflow_engine.execute_workflow(instance, user)
                    
                    triggered_workflows.append({
                        'workflow_id': str(workflow.id),
                        'workflow_name': workflow.name,
                        'instance_id': str(instance.id),
                        'result': result
                    })
            
            return {
                'success': True,
                'data': {
                    'triggered_workflows': triggered_workflows,
                    'count': len(triggered_workflows)
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing record create trigger: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_conditions(self, conditions: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Check if trigger conditions are met"""
        if not conditions:
            return True
        
        # Simple condition checking - can be extended
        for field, condition in conditions.items():
            if field == 'field_value':
                field_name = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if field_name in event_data.get('record_data', {}):
                    field_value = event_data['record_data'][field_name]
                    
                    if operator == 'equals' and field_value != value:
                        return False
                    elif operator == 'not_equals' and field_value == value:
                        return False
                    elif operator == 'in' and field_value not in value:
                        return False
                    elif operator == 'not_in' and field_value in value:
                        return False
        
        return True


class RecordUpdateTrigger(WorkflowTrigger):
    """Trigger workflows on record updates"""
    
    def should_trigger(self, event_data: Dict[str, Any]) -> bool:
        """Check if record update should trigger workflow"""
        event_type = event_data.get('event_type')
        return event_type == 'update'
    
    def execute(self, event_data: Dict[str, Any], user: User = None) -> Dict[str, Any]:
        """Execute workflows for record updates"""
        try:
            model_name = event_data.get('model_name')
            record_id = event_data.get('record_id')
            database = event_data.get('database')
            changed_fields = event_data.get('changed_fields', {})
            
            if not all([model_name, record_id, database]):
                return {
                    'success': False,
                    'error': 'Missing required event data'
                }
            
            # Find applicable workflow definitions
            workflows = WorkflowDefinition.objects.filter(
                model_name=model_name,
                database__name=database,
                trigger_type='on_update',
                active=True
            )
            
            triggered_workflows = []
            
            for workflow in workflows:
                # Check if any changed fields match trigger conditions
                if self._check_field_changes(workflow.trigger_conditions, changed_fields):
                    # Create workflow instance
                    instance = workflow_engine.create_workflow_instance(
                        workflow_definition=workflow,
                        record_id=record_id,
                        model_name=model_name,
                        database=database,
                        user=user,
                        context=event_data
                    )
                    
                    # Execute workflow
                    result = workflow_engine.execute_workflow(instance, user)
                    
                    triggered_workflows.append({
                        'workflow_id': str(workflow.id),
                        'workflow_name': workflow.name,
                        'instance_id': str(instance.id),
                        'result': result
                    })
            
            return {
                'success': True,
                'data': {
                    'triggered_workflows': triggered_workflows,
                    'count': len(triggered_workflows)
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing record update trigger: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_field_changes(self, conditions: Dict[str, Any], changed_fields: Dict[str, Any]) -> bool:
        """Check if field changes match trigger conditions"""
        if not conditions:
            return True
        
        # Check if any monitored fields have changed
        monitored_fields = conditions.get('monitored_fields', [])
        if monitored_fields:
            return any(field in changed_fields for field in monitored_fields)
        
        return True


class StateChangeTrigger(WorkflowTrigger):
    """Trigger workflows on state changes"""
    
    def should_trigger(self, event_data: Dict[str, Any]) -> bool:
        """Check if state change should trigger workflow"""
        event_type = event_data.get('event_type')
        return event_type == 'state_change'
    
    def execute(self, event_data: Dict[str, Any], user: User = None) -> Dict[str, Any]:
        """Execute workflows for state changes"""
        try:
            model_name = event_data.get('model_name')
            record_id = event_data.get('record_id')
            database = event_data.get('database')
            old_state = event_data.get('old_state')
            new_state = event_data.get('new_state')
            
            if not all([model_name, record_id, database, new_state]):
                return {
                    'success': False,
                    'error': 'Missing required event data'
                }
            
            # Find applicable workflow definitions
            workflows = WorkflowDefinition.objects.filter(
                model_name=model_name,
                database__name=database,
                trigger_type='on_state_change',
                active=True
            )
            
            triggered_workflows = []
            
            for workflow in workflows:
                # Check if state change matches trigger conditions
                if self._check_state_change(workflow.trigger_conditions, old_state, new_state):
                    # Create workflow instance
                    instance = workflow_engine.create_workflow_instance(
                        workflow_definition=workflow,
                        record_id=record_id,
                        model_name=model_name,
                        database=database,
                        user=user,
                        context=event_data
                    )
                    
                    # Execute workflow
                    result = workflow_engine.execute_workflow(instance, user)
                    
                    triggered_workflows.append({
                        'workflow_id': str(workflow.id),
                        'workflow_name': workflow.name,
                        'instance_id': str(instance.id),
                        'result': result
                    })
            
            return {
                'success': True,
                'data': {
                    'triggered_workflows': triggered_workflows,
                    'count': len(triggered_workflows)
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing state change trigger: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_state_change(self, conditions: Dict[str, Any], old_state: str, new_state: str) -> bool:
        """Check if state change matches trigger conditions"""
        if not conditions:
            return True
        
        # Check from_state condition
        from_states = conditions.get('from_states', [])
        if from_states and old_state not in from_states:
            return False
        
        # Check to_state condition
        to_states = conditions.get('to_states', [])
        if to_states and new_state not in to_states:
            return False
        
        return True


class TriggerRegistry:
    """
    Registry for workflow triggers
    """
    
    _triggers = {}
    
    @classmethod
    def register(cls, trigger_type: str, trigger_class: type):
        """Register a new trigger type"""
        cls._triggers[trigger_type] = trigger_class
    
    @classmethod
    def get_trigger(cls, trigger_type: str, config: Dict[str, Any]) -> WorkflowTrigger:
        """Get trigger instance by type"""
        if trigger_type not in cls._triggers:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
        
        trigger_class = cls._triggers[trigger_type]
        return trigger_class(config)
    
    @classmethod
    def list_triggers(cls) -> List[str]:
        """List all registered trigger types"""
        return list(cls._triggers.keys())


# Register built-in triggers
TriggerRegistry.register('record_create', RecordCreateTrigger)
TriggerRegistry.register('record_update', RecordUpdateTrigger)
TriggerRegistry.register('state_change', StateChangeTrigger)


class WorkflowTriggerManager:
    """
    Manager for handling workflow triggers
    """
    
    def __init__(self):
        self.registry = TriggerRegistry()
    
    def handle_event(self, event_data: Dict[str, Any], user: User = None) -> Dict[str, Any]:
        """
        Handle an event and trigger appropriate workflows
        """
        try:
            event_type = event_data.get('event_type')
            
            # Find applicable triggers
            triggered_workflows = []
            
            for trigger_type in self.registry.list_triggers():
                trigger = self.registry.get_trigger(trigger_type, {})
                
                if trigger.should_trigger(event_data):
                    result = trigger.execute(event_data, user)
                    if result.get('success'):
                        triggered_workflows.extend(result.get('data', {}).get('triggered_workflows', []))
            
            return {
                'success': True,
                'data': {
                    'triggered_workflows': triggered_workflows,
                    'count': len(triggered_workflows)
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling workflow event: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def trigger_manual_workflow(self, workflow_definition_id: str, record_id: int,
                              model_name: str, database: str, user: User,
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Manually trigger a workflow
        """
        try:
            workflow_definition = WorkflowDefinition.objects.get(
                id=workflow_definition_id, active=True
            )
            
            # Create workflow instance
            instance = workflow_engine.create_workflow_instance(
                workflow_definition=workflow_definition,
                record_id=record_id,
                model_name=model_name,
                database=database,
                user=user,
                context=context or {}
            )
            
            # Execute workflow
            result = workflow_engine.execute_workflow(instance, user)
            
            return {
                'success': True,
                'data': {
                    'workflow_id': str(workflow_definition.id),
                    'workflow_name': workflow_definition.name,
                    'instance_id': str(instance.id),
                    'result': result
                }
            }
            
        except Exception as e:
            logger.error(f"Error triggering manual workflow: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Global trigger manager instance
trigger_manager = WorkflowTriggerManager() 