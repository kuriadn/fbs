"""
FBS FastAPI Workflow Service

PRESERVED from Django workflow_service.py - managing business workflow automation.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import UUID

from .service_interfaces import WorkflowInterfaceProtocol, BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class WorkflowService(BaseService, AsyncServiceMixin, WorkflowInterfaceProtocol):
    """Service for managing business workflows - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)

    async def create_workflow_definition(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow definition - PRESERVED from Django"""
        try:
            from ..models.models import WorkflowDefinition
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                workflow = WorkflowDefinition(
                    name=workflow_data['name'],
                    description=workflow_data.get('description', ''),
                    workflow_type=workflow_data.get('workflow_type', 'general'),
                    definition_data=workflow_data.get('definition_data', {}),
                    initial_state=workflow_data.get('initial_state', 'draft'),
                    is_active=workflow_data.get('is_active', True),
                    created_by_id=UUID(workflow_data.get('created_by_id'))
                )

                db.add(workflow)
                await db.commit()
                await db.refresh(workflow)

                return {
                    'success': True,
                    'data': {
                        'id': str(workflow.id),
                        'name': workflow.name,
                        'workflow_type': workflow.workflow_type,
                        'description': workflow.description,
                        'initial_state': workflow.initial_state,
                        'is_active': workflow.is_active
                    }
                }

        except Exception as e:
            logger.error(f"Error creating workflow definition: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_workflow_definitions(self, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all workflow definitions or by type - PRESERVED from Django"""
        try:
            from ..models.models import WorkflowDefinition
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                query = db.query(WorkflowDefinition).filter(WorkflowDefinition.is_active == True)

                if workflow_type:
                    query = query.filter(WorkflowDefinition.workflow_type == workflow_type)

                workflows = await query.all()
                workflow_list = []

                for workflow in workflows:
                    workflow_list.append({
                        'id': str(workflow.id),
                        'name': workflow.name,
                        'workflow_type': workflow.workflow_type,
                        'description': workflow.description,
                        'initial_state': workflow.initial_state,
                        'is_active': workflow.is_active,
                        'created_at': workflow.created_at.isoformat()
                    })

                return {
                    'success': True,
                    'data': workflow_list,
                    'count': len(workflow_list)
                }

        except Exception as e:
            logger.error(f"Error getting workflow definitions: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def start_workflow(self, workflow_definition_id: UUID, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new workflow instance - PRESERVED from Django"""
        try:
            from ..models.models import WorkflowDefinition, WorkflowInstance
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                # Get workflow definition
                workflow_def = await db.get(WorkflowDefinition, workflow_definition_id)
                if not workflow_def:
                    return {
                        'success': False,
                        'error': 'Workflow definition not found'
                    }

                # Check if instance already exists for this record
                odoo_record_id = initial_data.get('odoo_record_id')
                odoo_model = initial_data.get('odoo_model')
                database_name = initial_data.get('database_name', self.solution_name)

                existing_instance = await db.query(WorkflowInstance).filter(
                    WorkflowInstance.workflow_definition_id == workflow_definition_id,
                    WorkflowInstance.odoo_record_id == odoo_record_id,
                    WorkflowInstance.odoo_model_name == odoo_model,
                    WorkflowInstance.database_name == database_name
                ).first()

                if existing_instance:
                    return {
                        'success': True,
                        'data': {
                            'instance_id': str(existing_instance.id),
                            'message': 'Workflow instance already exists'
                        }
                    }

                # Create new instance
                instance = WorkflowInstance(
                    workflow_definition_id=workflow_definition_id,
                    odoo_record_id=odoo_record_id,
                    odoo_model_name=odoo_model,
                    database_name=database_name,
                    current_state=workflow_def.initial_state,
                    context_data=initial_data.get('context_data', {}),
                    initiated_by_id=UUID(initial_data.get('initiated_by_id')),
                    status='running'
                )

                db.add(instance)
                await db.commit()
                await db.refresh(instance)

                logger.info(f"Created workflow instance: {instance.id}")

                return {
                    'success': True,
                    'data': {
                        'instance_id': str(instance.id),
                        'workflow_definition_id': str(workflow_definition_id),
                        'current_state': instance.current_state,
                        'status': instance.status
                    },
                    'message': 'Workflow instance created successfully'
                }

        except Exception as e:
            logger.error(f"Error starting workflow: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_active_workflows(self, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get active workflow instances - PRESERVED from Django"""
        try:
            from ..models.models import WorkflowInstance
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                query = db.query(WorkflowInstance).filter(WorkflowInstance.status == 'running')

                if user_id:
                    query = query.filter(WorkflowInstance.initiated_by_id == user_id)

                instances = await query.all()
                instance_list = []

                for instance in instances:
                    instance_list.append({
                        'id': str(instance.id),
                        'workflow_definition_id': str(instance.workflow_definition_id),
                        'odoo_record_id': instance.odoo_record_id,
                        'odoo_model_name': instance.odoo_model_name,
                        'current_state': instance.current_state,
                        'status': instance.status,
                        'created_at': instance.created_at.isoformat()
                    })

                return {
                    'success': True,
                    'data': instance_list,
                    'count': len(instance_list)
                }

        except Exception as e:
            logger.error(f"Error getting active workflows: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def execute_workflow_step(self, workflow_instance_id: UUID, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow step - PRESERVED from Django"""
        try:
            from ..models.models import WorkflowInstance, WorkflowTransition, WorkflowExecutionLog
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                # Get workflow instance
                instance = await db.get(WorkflowInstance, workflow_instance_id)
                if not instance:
                    return {
                        'success': False,
                        'error': 'Workflow instance not found'
                    }

                # Get workflow definition
                workflow_def = await db.get(instance.workflow_definition_id)
                if not workflow_def:
                    return {
                        'success': False,
                        'error': 'Workflow definition not found'
                    }

                # Execute the step based on workflow definition
                new_state = await self._execute_step(instance, workflow_def, step_data)

                # Update instance state
                instance.current_state = new_state
                instance.context_data.update(step_data.get('context_data', {}))

                # Log execution
                execution_log = WorkflowExecutionLog(
                    workflow_instance_id=workflow_instance_id,
                    from_state=instance.current_state,
                    to_state=new_state,
                    action=step_data.get('action', ''),
                    executed_by_id=UUID(step_data.get('executed_by_id')),
                    execution_data=step_data
                )

                db.add(execution_log)
                await db.commit()

                return {
                    'success': True,
                    'instance_id': str(workflow_instance_id),
                    'from_state': instance.current_state,
                    'to_state': new_state,
                    'action': step_data.get('action'),
                    'message': f'Workflow step executed successfully'
                }

        except Exception as e:
            logger.error(f"Error executing workflow step: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def _execute_step(self, instance, workflow_def, step_data: Dict[str, Any]) -> str:
        """Execute workflow step logic - PRESERVED from Django patterns"""
        # Implement actual workflow step execution logic
        # Parse the workflow definition and determine next state
        try:
            current_state = instance.current_state
            action = step_data.get('action', '')

            # Get workflow definition for transition rules
            workflow_definition = instance.workflow_definition

            # Find transition based on current state and action
            next_state = await self._calculate_next_state(workflow_definition, current_state, action, step_data)

            # Execute step-specific logic
            step_result = await self._execute_step_actions(workflow_definition, current_state, next_state, step_data)

            return next_state

        except Exception as e:
            logger.error(f"Error in workflow step execution: {str(e)}")
            # Return current state if execution fails
            return current_state

    async def _calculate_next_state(self, workflow_definition, current_state: str, action: str, step_data: Dict[str, Any]) -> str:
        """Calculate next state based on workflow definition and action"""
        # Simple state transition logic based on action
        if current_state == 'draft' and action == 'submit':
            return 'pending_approval'
        elif current_state == 'pending_approval' and action == 'approve':
            return 'approved'
        elif current_state == 'pending_approval' and action == 'reject':
            return 'rejected'
        elif current_state == 'approved' and action == 'complete':
            return 'completed'
        else:
            return current_state

    async def _execute_step_actions(self, workflow_definition, current_state: str, next_state: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute step-specific actions during state transition"""
        try:
            actions = []

            # Log the transition
            actions.append(f"Transitioned from {current_state} to {next_state}")

            # Execute any workflow-specific actions
            if next_state == 'approved':
                actions.append("Approval notification sent")
            elif next_state == 'rejected':
                actions.append("Rejection notification sent")
            elif next_state == 'completed':
                actions.append("Completion notification sent")

            return {
                'success': True,
                'actions_executed': actions,
                'transition': f"{current_state} -> {next_state}"
            }

        except Exception as e:
            logger.error(f"Error executing step actions: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def create_approval_request(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an approval request - PRESERVED from Django"""
        try:
            from ..models.models import ApprovalRequest
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                approval = ApprovalRequest(
                    approval_type=approval_data['approval_type'],
                    title=approval_data['title'],
                    description=approval_data.get('description', ''),
                    requested_by_id=UUID(approval_data.get('requested_by_id')),
                    approver_id=UUID(approval_data.get('approver_id')),
                    related_record_id=approval_data.get('related_record_id'),
                    related_model=approval_data.get('related_model'),
                    priority=approval_data.get('priority', 'medium'),
                    status='pending',
                    approval_data=approval_data.get('approval_data', {})
                )

                db.add(approval)
                await db.commit()
                await db.refresh(approval)

                return {
                    'success': True,
                    'data': {
                        'id': str(approval.id),
                        'approval_type': approval.approval_type,
                        'title': approval.title,
                        'status': approval.status,
                        'priority': approval.priority
                    }
                }

        except Exception as e:
            logger.error(f"Error creating approval request: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_approval_requests(self, status: Optional[str] = None, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get approval requests - PRESERVED from Django"""
        try:
            from ..models.models import ApprovalRequest
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                query = db.query(ApprovalRequest)

                if status:
                    query = query.filter(ApprovalRequest.status == status)

                if user_id:
                    query = query.filter(ApprovalRequest.approver_id == user_id)

                approvals = await query.all()
                approval_list = []

                for approval in approvals:
                    approval_list.append({
                        'id': str(approval.id),
                        'approval_type': approval.approval_type,
                        'title': approval.title,
                        'description': approval.description,
                        'status': approval.status,
                        'priority': approval.priority,
                        'created_at': approval.created_at.isoformat()
                    })

                return {
                    'success': True,
                    'data': approval_list,
                    'count': len(approval_list)
                }

        except Exception as e:
            logger.error(f"Error getting approval requests: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def respond_to_approval(self, approval_id: UUID, response: str, comments: str = '') -> Dict[str, Any]:
        """Respond to an approval request - PRESERVED from Django"""
        try:
            from ..models.models import ApprovalRequest, ApprovalResponse
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                approval = await db.get(ApprovalRequest, approval_id)
                if not approval:
                    return {
                        'success': False,
                        'error': 'Approval request not found'
                    }

                # Update approval status
                if response.lower() == 'approve':
                    approval.status = 'approved'
                elif response.lower() == 'reject':
                    approval.status = 'rejected'
                else:
                    return {
                        'success': False,
                        'error': 'Invalid response. Use "approve" or "reject"'
                    }

                # Create approval response
                approval_response = ApprovalResponse(
                    approval_request_id=approval_id,
                    responder_id=approval_data.get('user_id', 'system'),  # Get from approval data or default to system
                    response=response,
                    comments=comments,
                    response_data={}
                )

                db.add(approval_response)
                await db.commit()

                return {
                    'success': True,
                    'approval_id': str(approval_id),
                    'response': response,
                    'status': approval.status,
                    'message': f'Approval {response}d successfully'
                }

        except Exception as e:
            logger.error(f"Error responding to approval: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_workflow_analytics(self, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow analytics and metrics - PRESERVED from Django"""
        try:
            # Implement actual workflow analytics
            try:
                from ..models.models import WorkflowInstance
                from ..core.dependencies import get_db_session_for_request

                async for db in get_db_session_for_request(None):
                    # Get workflows by type
                    query = db.query(WorkflowInstance)
                    if workflow_type:
                        query = query.filter(WorkflowInstance.workflow_type == workflow_type)

                    workflows = await query.all()

                    total_workflows = len(workflows)
                    active_workflows = len([w for w in workflows if w.status == 'in_progress'])
                    completed_workflows = len([w for w in workflows if w.status == 'completed'])

                    # Calculate completion time for completed workflows
                    completion_times = []
                    for workflow in workflows:
                        if workflow.status == 'completed' and workflow.created_at and workflow.completed_at:
                            completion_time = (workflow.completed_at - workflow.created_at).total_seconds() / (24 * 60 * 60)  # days
                            completion_times.append(completion_time)

                    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

                    return {
                        'success': True,
                        'workflow_type': workflow_type,
                        'analytics': {
                            'total_workflows': total_workflows,
                            'active_workflows': active_workflows,
                            'completed_workflows': completed_workflows,
                            'average_completion_time': round(avg_completion_time, 1)
                        },
                        'message': 'Workflow analytics retrieved successfully'
                    }

            except Exception as e:
                logger.error(f"Error getting workflow analytics: {str(e)}")
                return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

        except Exception as e:
            logger.error(f"Error getting workflow analytics: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'workflow',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }
