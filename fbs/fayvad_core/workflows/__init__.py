"""
Generic Workflow Engine for FBS System

This module provides workflow capabilities that align with Odoo v17 CE best practices:
- Automated Actions (ir.actions.server)
- Workflow Transitions (state machines)
- Business Process Automation
- Approval Workflows
- Scheduled Tasks
"""

from .workflow_engine import WorkflowEngine
from .workflow_models import WorkflowDefinition, WorkflowInstance, WorkflowTransition
from .workflow_actions import WorkflowAction, WorkflowActionRegistry
from .workflow_triggers import WorkflowTrigger, TriggerRegistry

__all__ = [
    'WorkflowEngine',
    'WorkflowDefinition', 
    'WorkflowInstance',
    'WorkflowTransition',
    'WorkflowAction',
    'WorkflowActionRegistry',
    'WorkflowTrigger',
    'TriggerRegistry'
] 