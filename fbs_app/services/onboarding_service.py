"""
FBS App Onboarding Service

Service for client onboarding and self-service setup.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.db import connections
from django.conf import settings

logger = logging.getLogger('fbs_app')


class OnboardingService:
    """Service for client onboarding and self-service setup"""
    
    def __init__(self):
        self.fbs_config = getattr(settings, 'FBS_APP', {})
    
    def start_onboarding(self, business_type: str, business_name: str, 
                        contact_email: str, contact_phone: str = None) -> Dict[str, Any]:
        """Start client onboarding process"""
        try:
            # Generate unique onboarding ID
            onboarding_id = str(uuid.uuid4())
            
            # Create solution name from business name
            solution_name = self._generate_solution_name(business_name)
            
            # Create onboarding wizard record
            from ..models import MSMESetupWizard
            wizard = MSMESetupWizard.objects.create(
                solution_name=solution_name,
                business_type=business_type,
                setup_status='pending',
                preconfigured_data={
                    'business_name': business_name,
                    'contact_email': contact_email,
                    'contact_phone': contact_phone,
                    'onboarding_id': onboarding_id,
                    'created_at': timezone.now().isoformat()
                }
            )
            
            # Get available templates for business type
            templates = self.get_available_templates(business_type)
            
            return {
                'success': True,
                'onboarding_id': onboarding_id,
                'solution_name': solution_name,
                'business_type': business_type,
                'available_templates': templates,
                'next_steps': [
                    'configure_business_setup',
                    'select_modules',
                    'complete_onboarding'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error starting onboarding: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_available_templates(self, business_type: str = None) -> Dict[str, Any]:
        """Get available onboarding templates"""
        try:
            templates = {
                'micro_retail': {
                    'name': 'Micro Retail',
                    'description': 'Small retail store with basic operations',
                    'modules': ['sale', 'stock', 'account', 'point_of_sale'],
                    'features': [
                        'Basic sales management',
                        'Inventory tracking',
                        'Simple accounting',
                        'Point of sale system'
                    ],
                    'setup_time': '15-30 minutes',
                    'demo_data': True
                },
                'small_manufacturing': {
                    'name': 'Small Manufacturing',
                    'description': 'Small manufacturing business',
                    'modules': ['mrp', 'sale', 'stock', 'purchase', 'account'],
                    'features': [
                        'Manufacturing planning',
                        'Sales management',
                        'Inventory control',
                        'Purchase management',
                        'Basic accounting'
                    ],
                    'setup_time': '30-45 minutes',
                    'demo_data': True
                },
                'consulting': {
                    'name': 'Consulting',
                    'description': 'Professional consulting services',
                    'modules': ['project', 'hr_timesheet', 'account', 'sale'],
                    'features': [
                        'Project management',
                        'Time tracking',
                        'Basic accounting',
                        'Sales management'
                    ],
                    'setup_time': '20-30 minutes',
                    'demo_data': True
                },
                'ecommerce': {
                    'name': 'E-commerce',
                    'description': 'Online retail business',
                    'modules': ['website_sale', 'sale', 'stock', 'account'],
                    'features': [
                        'Online store',
                        'Sales management',
                        'Inventory control',
                        'Basic accounting'
                    ],
                    'setup_time': '25-40 minutes',
                    'demo_data': True
                }
            }
            
            if business_type:
                return {
                    'success': True,
                    'template': templates.get(business_type, templates['micro_retail'])
                }
            
            return {
                'success': True,
                'templates': templates
            }
            
        except Exception as e:
            logger.error(f"Error getting templates: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def configure_business_setup(self, onboarding_id: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Configure business setup during onboarding"""
        try:
            from ..models import MSMESetupWizard
            
            # Get onboarding wizard
            try:
                wizard = MSMESetupWizard.objects.get(
                    preconfigured_data__onboarding_id=onboarding_id
                )
            except MSMESetupWizard.DoesNotExist:
                return {'success': False, 'error': 'Onboarding session not found'}
            
            # Update business configuration
            wizard.business_config = business_data
            wizard.setup_status = 'configured'
            wizard.save()
            
            return {
                'success': True,
                'wizard_id': wizard.id,
                'setup_status': wizard.setup_status,
                'next_steps': ['select_modules', 'complete_onboarding']
            }
            
        except Exception as e:
            logger.error(f"Error configuring business setup: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def select_modules(self, onboarding_id: str, selected_modules: List[str]) -> Dict[str, Any]:
        """Select modules for business setup"""
        try:
            from ..models import MSMESetupWizard
            
            # Get onboarding wizard
            try:
                wizard = MSMESetupWizard.objects.get(
                    preconfigured_data__onboarding_id=onboarding_id
                )
            except MSMESetupWizard.DoesNotExist:
                return {'success': False, 'error': 'Onboarding session not found'}
            
            # Update selected modules
            wizard.selected_modules = selected_modules
            wizard.setup_status = 'modules_selected'
            wizard.save()
            
            return {
                'success': True,
                'wizard_id': wizard.id,
                'selected_modules': selected_modules,
                'next_steps': ['complete_onboarding']
            }
            
        except Exception as e:
            logger.error(f"Error selecting modules: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def complete_onboarding(self, onboarding_id: str) -> Dict[str, Any]:
        """Complete the onboarding process"""
        try:
            from ..models import MSMESetupWizard
            
            # Get onboarding wizard
            try:
                wizard = MSMESetupWizard.objects.get(
                    preconfigured_data__onboarding_id=onboarding_id
                )
            except MSMESetupWizard.DoesNotExist:
                return {'success': False, 'error': 'Onboarding session not found'}
            
            # Mark onboarding as completed
            wizard.setup_status = 'completed'
            wizard.completed_at = timezone.now()
            wizard.save()
            
            return {
                'success': True,
                'wizard_id': wizard.id,
                'setup_status': 'completed',
                'solution_name': wizard.solution_name,
                'message': 'Onboarding completed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error completing onboarding: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_onboarding_status(self, onboarding_id: str) -> Dict[str, Any]:
        """Get current onboarding status"""
        try:
            from ..models import MSMESetupWizard
            
            # Get onboarding wizard
            try:
                wizard = MSMESetupWizard.objects.get(
                    preconfigured_data__onboarding_id=onboarding_id
                )
            except MSMESetupWizard.DoesNotExist:
                return {'success': False, 'error': 'Onboarding session not found'}
            
            return {
                'success': True,
                'onboarding_id': onboarding_id,
                'solution_name': wizard.solution_name,
                'business_type': wizard.business_type,
                'setup_status': wizard.setup_status,
                'created_at': wizard.created_at,
                'completed_at': wizard.completed_at,
                'selected_modules': getattr(wizard, 'selected_modules', []),
                'business_config': getattr(wizard, 'business_config', {})
            }
            
        except Exception as e:
            logger.error(f"Error getting onboarding status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_solution_name(self, business_name: str) -> str:
        """Generate solution name from business name"""
        # Clean business name and create solution name
        clean_name = business_name.lower().replace(' ', '_').replace('-', '_')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
        
        # Ensure uniqueness
        base_name = f"solution_{clean_name}"
        counter = 1
        
        while self._solution_name_exists(f"{base_name}_{counter}"):
            counter += 1
        
        return f"{base_name}_{counter}"
    
    def _solution_name_exists(self, solution_name: str) -> bool:
        """Check if solution name already exists"""
        try:
            from ..models import MSMESetupWizard
            return MSMESetupWizard.objects.filter(solution_name=solution_name).exists()
        except Exception:
            return False
    
    # Missing methods that the interface expects
    def start_onboarding(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start client onboarding process"""
        try:
            from ..models import MSMESetupWizard
            
            # Extract client data
            business_name = client_data.get('business_name', 'New Business')
            business_type = client_data.get('business_type', 'general')
            
            # Generate unique solution name
            solution_name = self._generate_solution_name(business_name)
            
            # Create onboarding wizard
            wizard = MSMESetupWizard.objects.create(
                solution_name=solution_name,
                business_type=business_type,
                status='not_started',
                current_step='setup',
                total_steps=5,
                progress=0.0
            )
            
            return {
                'success': True,
                'data': {
                    'onboarding_id': wizard.id,
                    'solution_name': wizard.solution_name,
                    'business_type': wizard.business_type,
                    'status': wizard.status
                }
            }
        except Exception as e:
            logger.error(f"Error starting onboarding: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_onboarding_step(self, client_id: int, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update onboarding step"""
        try:
            from ..models import MSMESetupWizard
            
            wizard = MSMESetupWizard.objects.get(id=client_id)
            
            # Update step data
            wizard.current_step = step_name
            wizard.progress = step_data.get('progress', wizard.progress)
            
            # Update configuration if provided
            if 'configuration' in step_data:
                current_config = wizard.configuration or {}
                current_config.update(step_data['configuration'])
                wizard.configuration = current_config
            
            wizard.save()
            
            return {
                'success': True,
                'data': {
                    'id': wizard.id,
                    'current_step': wizard.current_step,
                    'progress': wizard.progress
                }
            }
        except MSMESetupWizard.DoesNotExist:
            return {'success': False, 'error': 'Client not found'}
        except Exception as e:
            logger.error(f"Error updating onboarding step: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_onboarding_templates(self, business_type: Optional[str] = None) -> Dict[str, Any]:
        """Get onboarding templates"""
        try:
            # Placeholder for onboarding templates
            # In production, this would fetch actual templates from database
            templates = {
                'retail': {
                    'name': 'Retail Starter Pack',
                    'modules': ['inventory', 'sales', 'customer_management'],
                    'configuration': {'currency': 'USD', 'tax_rate': 0.1}
                },
                'manufacturing': {
                    'name': 'Manufacturing Starter Pack',
                    'modules': ['inventory', 'production', 'quality_control'],
                    'configuration': {'currency': 'USD', 'tax_rate': 0.1}
                },
                'services': {
                    'name': 'Services Starter Pack',
                    'modules': ['project_management', 'time_tracking', 'billing'],
                    'configuration': {'currency': 'USD', 'tax_rate': 0.1}
                }
            }
            
            if business_type:
                return {
                    'success': True,
                    'data': templates.get(business_type, {})
                }
            else:
                return {
                    'success': True,
                    'data': templates
                }
        except Exception as e:
            logger.error(f"Error getting onboarding templates: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def apply_onboarding_template(self, client_id: int, template_name: str) -> Dict[str, Any]:
        """Apply onboarding template"""
        try:
            from ..models import MSMESetupWizard
            
            wizard = MSMESetupWizard.objects.get(id=client_id)
            
            # Get template
            templates = self.get_onboarding_templates(wizard.business_type)
            if not templates['success']:
                return templates
            
            template = templates['data']
            
            # Apply template configuration
            current_config = wizard.configuration or {}
            current_config.update(template.get('configuration', {}))
            wizard.configuration = current_config
            
            # Update progress
            wizard.progress = 50.0  # Template applied
            wizard.current_step = 'template_applied'
            wizard.save()
            
            return {
                'success': True,
                'data': {
                    'id': wizard.id,
                    'template_applied': template_name,
                    'progress': wizard.progress,
                    'current_step': wizard.current_step
                }
            }
        except MSMESetupWizard.DoesNotExist:
            return {'success': False, 'error': 'Client not found'}
        except Exception as e:
            logger.error(f"Error applying onboarding template: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def import_demo_data(self, client_id: int, demo_type: str) -> Dict[str, Any]:
        """Import demo data for client"""
        try:
            from ..models import MSMESetupWizard
            
            wizard = MSMESetupWizard.objects.get(id=client_id)
            
            # Placeholder for demo data import
            # In production, this would import actual demo data
            demo_data = {
                'customers': 10,
                'products': 25,
                'orders': 15,
                'invoices': 12
            }
            
            # Update configuration with demo data info
            current_config = wizard.configuration or {}
            current_config['demo_data'] = {
                'type': demo_type,
                'imported': True,
                'counts': demo_data
            }
            wizard.configuration = current_config
            wizard.progress = 80.0  # Demo data imported
            wizard.current_step = 'demo_data_imported'
            wizard.save()
            
            return {
                'success': True,
                'data': {
                    'id': wizard.id,
                    'demo_type': demo_type,
                    'demo_data': demo_data,
                    'progress': wizard.progress
                }
            }
        except MSMESetupWizard.DoesNotExist:
            return {'success': False, 'error': 'Client not found'}
        except Exception as e:
            logger.error(f"Error importing demo data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_onboarding_timeline(self, client_id: int) -> Dict[str, Any]:
        """Get onboarding timeline"""
        try:
            from ..models import MSMESetupWizard
            
            wizard = MSMESetupWizard.objects.get(id=client_id)
            
            # Create timeline based on current progress
            timeline = [
                {
                    'step': 'setup',
                    'status': 'completed' if wizard.progress >= 20 else 'pending',
                    'description': 'Initial business setup',
                    'completed_at': wizard.started_at.isoformat()
                },
                {
                    'step': 'template_applied',
                    'status': 'completed' if wizard.progress >= 50 else 'pending',
                    'description': 'Business template applied',
                    'completed_at': None
                },
                {
                    'step': 'demo_data_imported',
                    'status': 'completed' if wizard.progress >= 80 else 'pending',
                    'description': 'Demo data imported',
                    'completed_at': None
                },
                {
                    'step': 'completed',
                    'status': 'completed' if wizard.progress >= 100 else 'pending',
                    'description': 'Onboarding completed',
                    'completed_at': wizard.completed_at.isoformat() if wizard.completed_at else None
                }
            ]
            
            return {
                'success': True,
                'data': {
                    'id': wizard.id,
                    'timeline': timeline,
                    'current_progress': wizard.progress,
                    'current_step': wizard.current_step,
                    'progress': wizard.progress
                }
            }
        except MSMESetupWizard.DoesNotExist:
            return {'success': False, 'error': 'Client not found'}
        except Exception as e:
            logger.error(f"Error getting onboarding timeline: {str(e)}")
            return {'success': False, 'error': str(e)}
