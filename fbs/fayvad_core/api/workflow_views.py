"""
Workflow API Views

RESTful API endpoints for workflow management including:
- Workflow definitions CRUD
- Workflow instances management
- Workflow execution and transitions
- Workflow status and monitoring
"""

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ..workflows.workflow_engine import WorkflowEngine
from ..workflows.workflow_models import WorkflowDefinition, WorkflowInstance, WorkflowTransition
from ..services.odoo_client import odoo_client
from ..auth.drf_auth import JWTAuthentication
import logging

logger = logging.getLogger('fayvad_core.api.workflows')

workflow_engine = WorkflowEngine()


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def workflow_definitions(request):
    """List and create workflow definitions"""
    
    if request.method == 'GET':
        try:
            database = request.GET.get('db')
            model_name = request.GET.get('model')
            
            queryset = WorkflowDefinition.objects.filter(active=True)
            
            if database:
                queryset = queryset.filter(database__name=database)
            
            if model_name:
                queryset = queryset.filter(model_name=model_name)
            
            workflows = []
            for workflow in queryset:
                workflows.append({
                    'id': str(workflow.id),
                    'name': workflow.name,
                    'description': workflow.description,
                    'model_name': workflow.model_name,
                    'database': workflow.database.name,
                    'trigger_type': workflow.trigger_type,
                    'requires_approval': workflow.requires_approval,
                    'is_scheduled': workflow.is_scheduled,
                    'created_at': workflow.created_at,
                    'updated_at': workflow.updated_at
                })
            
            return Response({
                'success': True,
                'data': workflows
            })
            
        except Exception as e:
            logger.error(f"Error listing workflow definitions: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'POST':
        try:
            data = request.data
            
            # Validate required fields
            required_fields = ['name', 'model_name', 'database', 'trigger_type']
            for field in required_fields:
                if field not in data:
                    return Response({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create workflow definition
            workflow = WorkflowDefinition.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                model_name=data['model_name'],
                database_id=data['database'],
                trigger_type=data['trigger_type'],
                trigger_conditions=data.get('trigger_conditions', {}),
                workflow_steps=data.get('workflow_steps', []),
                states=data.get('states', {}),
                initial_state=data.get('initial_state', 'draft'),
                requires_approval=data.get('requires_approval', False),
                approval_roles=data.get('approval_roles', []),
                is_scheduled=data.get('is_scheduled', False),
                schedule_cron=data.get('schedule_cron', ''),
                schedule_interval=data.get('schedule_interval', 0),
                created_by=request.user
            )
            
            return Response({
                'success': True,
                'data': {
                    'id': str(workflow.id),
                    'name': workflow.name,
                    'message': 'Workflow definition created successfully'
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating workflow definition: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def workflow_definition_detail(request, workflow_id):
    """Get, update, or delete a workflow definition"""
    
    try:
        workflow = get_object_or_404(WorkflowDefinition, id=workflow_id, active=True)
        
        if request.method == 'GET':
            return Response({
                'success': True,
                'data': {
                    'id': str(workflow.id),
                    'name': workflow.name,
                    'description': workflow.description,
                    'model_name': workflow.model_name,
                    'database': workflow.database.name,
                    'trigger_type': workflow.trigger_type,
                    'trigger_conditions': workflow.trigger_conditions,
                    'workflow_steps': workflow.workflow_steps,
                    'states': workflow.states,
                    'initial_state': workflow.initial_state,
                    'requires_approval': workflow.requires_approval,
                    'approval_roles': workflow.approval_roles,
                    'is_scheduled': workflow.is_scheduled,
                    'schedule_cron': workflow.schedule_cron,
                    'schedule_interval': workflow.schedule_interval,
                    'created_at': workflow.created_at,
                    'updated_at': workflow.updated_at,
                    'created_by': workflow.created_by.username if workflow.created_by else None
                }
            })
        
        elif request.method == 'PUT':
            data = request.data
            
            # Update fields
            if 'name' in data:
                workflow.name = data['name']
            if 'description' in data:
                workflow.description = data['description']
            if 'trigger_conditions' in data:
                workflow.trigger_conditions = data['trigger_conditions']
            if 'workflow_steps' in data:
                workflow.workflow_steps = data['workflow_steps']
            if 'states' in data:
                workflow.states = data['states']
            if 'initial_state' in data:
                workflow.initial_state = data['initial_state']
            if 'requires_approval' in data:
                workflow.requires_approval = data['requires_approval']
            if 'approval_roles' in data:
                workflow.approval_roles = data['approval_roles']
            if 'is_scheduled' in data:
                workflow.is_scheduled = data['is_scheduled']
            if 'schedule_cron' in data:
                workflow.schedule_cron = data['schedule_cron']
            if 'schedule_interval' in data:
                workflow.schedule_interval = data['schedule_interval']
            
            workflow.save()
            
            return Response({
                'success': True,
                'data': {
                    'id': str(workflow.id),
                    'name': workflow.name,
                    'message': 'Workflow definition updated successfully'
                }
            })
        
        elif request.method == 'DELETE':
            workflow.active = False
            workflow.save()
            
            return Response({
                'success': True,
                'message': 'Workflow definition deleted successfully'
            })
    
    except Exception as e:
        logger.error(f"Error in workflow definition detail: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def workflow_instances(request):
    """List and create workflow instances"""
    
    if request.method == 'GET':
        try:
            database = request.GET.get('db')
            model_name = request.GET.get('model')
            status_filter = request.GET.get('status')
            
            queryset = WorkflowInstance.objects.all()
            
            if database:
                queryset = queryset.filter(database__name=database)
            
            if model_name:
                queryset = queryset.filter(odoo_model_name=model_name)
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            instances = []
            for instance in queryset[:50]:  # Limit to 50 instances
                instances.append({
                    'id': str(instance.id),
                    'workflow_name': instance.workflow_definition.name,
                    'model_name': instance.odoo_model_name,
                    'record_id': instance.odoo_record_id,
                    'database': instance.database.name,
                    'current_state': instance.current_state,
                    'status': instance.status,
                    'approval_status': instance.approval_status,
                    'started_at': instance.started_at,
                    'last_executed_at': instance.last_executed_at,
                    'initiated_by': instance.initiated_by.username if instance.initiated_by else None,
                    'current_assignee': instance.current_assignee.username if instance.current_assignee else None
                })
            
            return Response({
                'success': True,
                'data': instances
            })
            
        except Exception as e:
            logger.error(f"Error listing workflow instances: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'POST':
        try:
            data = request.data
            
            # Validate required fields
            required_fields = ['workflow_definition_id', 'record_id', 'model_name', 'database']
            for field in required_fields:
                if field not in data:
                    return Response({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get workflow definition
            workflow_definition = get_object_or_404(WorkflowDefinition, id=data['workflow_definition_id'], active=True)
            
            # Create workflow instance
            instance = workflow_engine.create_workflow_instance(
                workflow_definition=workflow_definition,
                record_id=data['record_id'],
                model_name=data['model_name'],
                database=data['database'],
                user=request.user,
                context=data.get('context', {})
            )
            
            return Response({
                'success': True,
                'data': {
                    'id': str(instance.id),
                    'workflow_name': instance.workflow_definition.name,
                    'message': 'Workflow instance created successfully'
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating workflow instance: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def workflow_instance_detail(request, instance_id):
    """Get workflow instance details and execute transitions"""
    
    try:
        instance = get_object_or_404(WorkflowInstance, id=instance_id)
        
        if request.method == 'GET':
            # Get workflow status
            status_data = workflow_engine.get_workflow_status(instance)
            
            return Response({
                'success': True,
                'data': status_data
            })
        
        elif request.method == 'POST':
            data = request.data
            action = data.get('action')
            
            if action == 'execute':
                # Execute workflow
                result = workflow_engine.execute_workflow(instance, request.user)
                return Response(result)
            
            elif action == 'transition':
                # Execute specific transition
                transition_name = data.get('transition_name')
                if not transition_name:
                    return Response({
                        'success': False,
                        'error': 'transition_name is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                result = workflow_engine.execute_transition(
                    instance, transition_name, request.user, data.get('context')
                )
                return Response(result)
            
            elif action == 'approve':
                # Approve workflow
                instance.approval_status = 'approved'
                instance.save()
                
                # Continue workflow execution
                result = workflow_engine.execute_workflow(instance, request.user)
                return Response(result)
            
            elif action == 'reject':
                # Reject workflow
                instance.approval_status = 'rejected'
                instance.status = 'cancelled'
                instance.save()
                
                return Response({
                    'success': True,
                    'message': 'Workflow rejected successfully'
                })
            
            else:
                return Response({
                    'success': False,
                    'error': f'Unknown action: {action}'
                }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error in workflow instance detail: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def workflow_transitions(request, workflow_id):
    """List and create workflow transitions"""
    
    try:
        workflow = get_object_or_404(WorkflowDefinition, id=workflow_id, active=True)
        
        if request.method == 'GET':
            transitions = WorkflowTransition.objects.filter(workflow_definition=workflow).order_by('order')
            
            transition_data = []
            for transition in transitions:
                transition_data.append({
                    'id': str(transition.id),
                    'name': transition.name,
                    'description': transition.description,
                    'from_state': transition.from_state,
                    'to_state': transition.to_state,
                    'conditions': transition.conditions,
                    'actions': transition.actions,
                    'required_roles': transition.required_roles,
                    'requires_approval': transition.requires_approval,
                    'button_text': transition.button_text,
                    'button_style': transition.button_style,
                    'order': transition.order
                })
            
            return Response({
                'success': True,
                'data': transition_data
            })
        
        elif request.method == 'POST':
            data = request.data
            
            # Validate required fields
            required_fields = ['name', 'from_state', 'to_state']
            for field in required_fields:
                if field not in data:
                    return Response({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create transition
            transition = WorkflowTransition.objects.create(
                workflow_definition=workflow,
                name=data['name'],
                description=data.get('description', ''),
                from_state=data['from_state'],
                to_state=data['to_state'],
                conditions=data.get('conditions', {}),
                actions=data.get('actions', []),
                required_roles=data.get('required_roles', []),
                requires_approval=data.get('requires_approval', False),
                button_text=data.get('button_text', ''),
                button_style=data.get('button_style', 'primary'),
                order=data.get('order', 0)
            )
            
            return Response({
                'success': True,
                'data': {
                    'id': str(transition.id),
                    'name': transition.name,
                    'message': 'Workflow transition created successfully'
                }
            }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error in workflow transitions: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def workflow_actions(request):
    """List available workflow actions"""
    
    try:
        from ..workflows.workflow_actions import WorkflowActionRegistry
        
        actions = WorkflowActionRegistry.list_actions()
        
        return Response({
            'success': True,
            'data': {
                'available_actions': actions,
                'action_count': len(actions)
            }
        })
    
    except Exception as e:
        logger.error(f"Error listing workflow actions: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 