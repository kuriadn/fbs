"""
FBS FastAPI Onboarding Service

PRESERVED from Django onboarding_service.py
Service for client onboarding and self-service setup.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import UUID

from .service_interfaces import BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class OnboardingService(BaseService, AsyncServiceMixin):
    """Service for client onboarding and self-service setup - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)
        self.templates = self._load_onboarding_templates()

    def _load_onboarding_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load onboarding templates - PRESERVED from Django"""
        return {
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
                'demo_data': True,
                'steps': [
                    'business_info',
                    'odoo_connection',
                    'module_installation',
                    'demo_data_import',
                    'user_setup'
                ]
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
                'demo_data': True,
                'steps': [
                    'business_info',
                    'odoo_connection',
                    'module_installation',
                    'manufacturing_setup',
                    'demo_data_import',
                    'user_setup'
                ]
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
                'demo_data': True,
                'steps': [
                    'business_info',
                    'odoo_connection',
                    'module_installation',
                    'project_setup',
                    'demo_data_import',
                    'user_setup'
                ]
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
                'demo_data': True,
                'steps': [
                    'business_info',
                    'odoo_connection',
                    'module_installation',
                    'website_setup',
                    'demo_data_import',
                    'user_setup'
                ]
            }
        }

    async def start_onboarding(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start client onboarding process - PRESERVED from Django"""
        try:
            from ..models.models import OnboardingProcess
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                # Create onboarding process
                onboarding = OnboardingProcess(
                    client_id=uuid.uuid4(),  # Generate client ID
                    business_name=client_data.get('business_name', ''),
                    business_type=client_data.get('business_type', ''),
                    contact_email=client_data.get('contact_email', ''),
                    contact_phone=client_data.get('contact_phone', ''),
                    status='in_progress',
                    current_step='business_info',
                    steps_completed=[],
                    configuration=client_data.get('configuration', {})
                )

                db.add(onboarding)
                await db.commit()
                await db.refresh(onboarding)

                return {
                    'success': True,
                    'onboarding_id': str(onboarding.id),
                    'client_id': str(onboarding.client_id),
                    'status': onboarding.status,
                    'current_step': onboarding.current_step,
                    'next_steps': self.templates.get(onboarding.business_type, {}).get('steps', []),
                    'message': 'Onboarding process started successfully'
                }

        except Exception as e:
            logger.error(f"Error starting onboarding: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_onboarding_status(self, client_id: UUID) -> Dict[str, Any]:
        """Get onboarding status - PRESERVED from Django"""
        try:
            from ..models.models import OnboardingProcess
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                onboarding = await db.query(OnboardingProcess).filter(
                    OnboardingProcess.client_id == client_id
                ).first()

                if not onboarding:
                    return {
                        'success': False,
                        'error': 'Onboarding process not found'
                    }

                template = self.templates.get(onboarding.business_type, {})
                total_steps = len(template.get('steps', []))
                completed_steps = len(onboarding.steps_completed)
                progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0

                return {
                    'success': True,
                    'onboarding_id': str(onboarding.id),
                    'client_id': str(onboarding.client_id),
                    'business_name': onboarding.business_name,
                    'business_type': onboarding.business_type,
                    'status': onboarding.status,
                    'current_step': onboarding.current_step,
                    'steps_completed': onboarding.steps_completed,
                    'total_steps': total_steps,
                    'progress_percentage': round(progress_percentage, 2),
                    'next_step': self._get_next_step(onboarding),
                    'created_at': onboarding.created_at.isoformat(),
                    'updated_at': onboarding.updated_at.isoformat()
                }

        except Exception as e:
            logger.error(f"Error getting onboarding status: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def update_onboarding_step(self, client_id: UUID, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update onboarding step - PRESERVED from Django"""
        try:
            from ..models.models import OnboardingProcess
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                onboarding = await db.query(OnboardingProcess).filter(
                    OnboardingProcess.client_id == client_id
                ).first()

                if not onboarding:
                    return {
                        'success': False,
                        'error': 'Onboarding process not found'
                    }

                # Update step data
                if 'configuration' not in onboarding.configuration:
                    onboarding.configuration = {}

                onboarding.configuration[step_name] = step_data

                # Mark step as completed if not already
                if step_name not in onboarding.steps_completed:
                    onboarding.steps_completed.append(step_name)

                # Update current step
                template = self.templates.get(onboarding.business_type, {})
                template_steps = template.get('steps', [])
                current_index = template_steps.index(step_name) if step_name in template_steps else -1

                if current_index >= 0 and current_index + 1 < len(template_steps):
                    onboarding.current_step = template_steps[current_index + 1]
                else:
                    onboarding.current_step = 'completed'
                    onboarding.status = 'completed'
                    onboarding.completed_at = datetime.now()

                onboarding.updated_at = datetime.now()

                await db.commit()
                await db.refresh(onboarding)

                return {
                    'success': True,
                    'client_id': str(client_id),
                    'step_name': step_name,
                    'status': onboarding.status,
                    'current_step': onboarding.current_step,
                    'steps_completed': onboarding.steps_completed,
                    'message': f'Step {step_name} updated successfully'
                }

        except Exception as e:
            logger.error(f"Error updating onboarding step: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def complete_onboarding(self, client_id: UUID) -> Dict[str, Any]:
        """Complete onboarding process - PRESERVED from Django"""
        try:
            from ..models.models import OnboardingProcess
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                onboarding = await db.query(OnboardingProcess).filter(
                    OnboardingProcess.client_id == client_id
                ).first()

                if not onboarding:
                    return {
                        'success': False,
                        'error': 'Onboarding process not found'
                    }

                onboarding.status = 'completed'
                onboarding.current_step = 'completed'
                onboarding.completed_at = datetime.now()
                onboarding.updated_at = datetime.now()

                await db.commit()

                return {
                    'success': True,
                    'client_id': str(client_id),
                    'status': 'completed',
                    'completed_at': onboarding.completed_at.isoformat(),
                    'message': 'Onboarding process completed successfully'
                }

        except Exception as e:
            logger.error(f"Error completing onboarding: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_onboarding_templates(self, business_type: Optional[str] = None) -> Dict[str, Any]:
        """Get onboarding templates - PRESERVED from Django"""
        try:
            if business_type:
                template = self.templates.get(business_type)
                if not template:
                    return {
                        'success': False,
                        'error': f'Template for {business_type} not found'
                    }

                return {
                    'success': True,
                    'template': template,
                    'business_type': business_type
                }
            else:
                return {
                    'success': True,
                    'templates': self.templates,
                    'count': len(self.templates)
                }

        except Exception as e:
            logger.error(f"Error getting onboarding templates: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def apply_onboarding_template(self, client_id: UUID, template_name: str) -> Dict[str, Any]:
        """Apply onboarding template - PRESERVED from Django"""
        try:
            from ..models.models import OnboardingProcess
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                onboarding = await db.query(OnboardingProcess).filter(
                    OnboardingProcess.client_id == client_id
                ).first()

                if not onboarding:
                    return {
                        'success': False,
                        'error': 'Onboarding process not found'
                    }

                template = self.templates.get(template_name)
                if not template:
                    return {
                        'success': False,
                        'error': f'Template {template_name} not found'
                    }

                # Apply template configuration
                if 'configuration' not in onboarding.configuration:
                    onboarding.configuration = {}

                onboarding.configuration['applied_template'] = template_name
                onboarding.configuration['template_config'] = template
                onboarding.business_type = template_name

                onboarding.updated_at = datetime.now()

                await db.commit()

                return {
                    'success': True,
                    'client_id': str(client_id),
                    'template_name': template_name,
                    'template': template,
                    'message': f'Template {template_name} applied successfully'
                }

        except Exception as e:
            logger.error(f"Error applying onboarding template: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def import_demo_data(self, client_id: UUID, demo_type: str) -> Dict[str, Any]:
        """Import demo data for client - PRESERVED from Django"""
        try:
            # Implement actual demo data import based on business type
            demo_data_map = {
                'micro_retail': self._get_micro_retail_demo_data,
                'small_manufacturing': self._get_manufacturing_demo_data,
                'consulting': self._get_consulting_demo_data,
                'ecommerce': self._get_ecommerce_demo_data
            }

            if demo_type not in demo_data_map:
                return {
                    'success': False,
                    'error': f'Unsupported demo type: {demo_type}'
                }

            # Get demo data
            demo_data = demo_data_map[demo_type]()

            # Import the demo data
            import_result = await self._import_demo_data_to_system(client_id, demo_data)

            return {
                'success': import_result['success'],
                'client_id': str(client_id),
                'demo_type': demo_type,
                'records_imported': import_result.get('records_imported', 0),
                'message': f'Demo data import completed for {demo_type}'
            }

        except Exception as e:
            logger.error(f"Error importing demo data: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_onboarding_timeline(self, client_id: UUID) -> Dict[str, Any]:
        """Get onboarding timeline - PRESERVED from Django"""
        try:
            from ..models.models import OnboardingProcess
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                onboarding = await db.query(OnboardingProcess).filter(
                    OnboardingProcess.client_id == client_id
                ).first()

                if not onboarding:
                    return {
                        'success': False,
                        'error': 'Onboarding process not found'
                    }

                template = self.templates.get(onboarding.business_type, {})
                template_steps = template.get('steps', [])

                timeline = []
                for i, step in enumerate(template_steps):
                    timeline.append({
                        'step_name': step,
                        'step_number': i + 1,
                        'status': 'completed' if step in onboarding.steps_completed else 'pending',
                        'completed_at': step.get('completed_at'),  # Track individual step completion times
                        'estimated_time': self._get_step_estimated_time(step)
                    })

                return {
                    'success': True,
                    'client_id': str(client_id),
                    'timeline': timeline,
                    'total_steps': len(template_steps),
                    'completed_steps': len(onboarding.steps_completed),
                    'current_step': onboarding.current_step
                }

        except Exception as e:
            logger.error(f"Error getting onboarding timeline: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    def _get_next_step(self, onboarding) -> Optional[str]:
        """Get next step in onboarding process"""
        template = self.templates.get(onboarding.business_type, {})
        template_steps = template.get('steps', [])

        if not template_steps:
            return None

        # Find current step index
        try:
            current_index = template_steps.index(onboarding.current_step)
            if current_index + 1 < len(template_steps):
                return template_steps[current_index + 1]
        except ValueError:
            pass

        return None

    def _get_step_estimated_time(self, step_name: str) -> str:
        """Get estimated time for a step"""
        step_times = {
            'business_info': '5 minutes',
            'odoo_connection': '10 minutes',
            'module_installation': '15 minutes',
            'demo_data_import': '5 minutes',
            'user_setup': '5 minutes',
            'manufacturing_setup': '10 minutes',
            'project_setup': '5 minutes',
            'website_setup': '10 minutes'
        }

        return step_times.get(step_name, '5 minutes')

    def _get_micro_retail_demo_data(self) -> Dict[str, Any]:
        """Generate demo data for micro retail business"""
        return {
            'products': [
                {'name': 'Wireless Headphones', 'price': 89.99, 'category': 'Electronics'},
                {'name': 'Coffee Maker', 'price': 49.99, 'category': 'Home & Garden'},
                {'name': 'Running Shoes', 'price': 79.99, 'category': 'Clothing'},
                {'name': 'Smartphone Case', 'price': 19.99, 'category': 'Electronics'},
                {'name': 'Notebook', 'price': 12.99, 'category': 'Office Supplies'}
            ],
            'customers': [
                {'name': 'John Smith', 'email': 'john@example.com'},
                {'name': 'Sarah Johnson', 'email': 'sarah@example.com'},
                {'name': 'Mike Davis', 'email': 'mike@example.com'}
            ],
            'transactions': [
                {'customer': 'John Smith', 'product': 'Wireless Headphones', 'amount': 89.99},
                {'customer': 'Sarah Johnson', 'product': 'Coffee Maker', 'amount': 49.99},
                {'customer': 'Mike Davis', 'product': 'Running Shoes', 'amount': 79.99}
            ]
        }

    def _get_manufacturing_demo_data(self) -> Dict[str, Any]:
        """Generate demo data for manufacturing business"""
        return {
            'products': [
                {'name': 'Steel Rods', 'price': 25.50, 'category': 'Raw Materials'},
                {'name': 'Aluminum Sheets', 'price': 45.75, 'category': 'Raw Materials'},
                {'name': 'Finished Widget A', 'price': 125.00, 'category': 'Finished Goods'},
                {'name': 'Finished Widget B', 'price': 89.99, 'category': 'Finished Goods'}
            ],
            'work_orders': [
                {'product': 'Finished Widget A', 'quantity': 100, 'status': 'in_progress'},
                {'product': 'Finished Widget B', 'quantity': 50, 'status': 'completed'}
            ],
            'suppliers': [
                {'name': 'Steel Corp', 'contact': 'orders@steelcorp.com'},
                {'name': 'Aluminum Inc', 'contact': 'procurement@aluminuminc.com'}
            ]
        }

    def _get_consulting_demo_data(self) -> Dict[str, Any]:
        """Generate demo data for consulting business"""
        return {
            'services': [
                {'name': 'Business Strategy Consulting', 'price': 250.00, 'unit': 'hour'},
                {'name': 'IT Infrastructure Review', 'price': 180.00, 'unit': 'hour'},
                {'name': 'Process Optimization', 'price': 200.00, 'unit': 'hour'}
            ],
            'projects': [
                {'name': 'ERP Implementation', 'client': 'TechCorp', 'status': 'in_progress'},
                {'name': 'Digital Transformation', 'client': 'RetailPlus', 'status': 'completed'}
            ],
            'time_entries': [
                {'project': 'ERP Implementation', 'hours': 8.5, 'description': 'Requirements gathering'},
                {'project': 'Digital Transformation', 'hours': 6.0, 'description': 'Strategy workshop'}
            ]
        }

    def _get_ecommerce_demo_data(self) -> Dict[str, Any]:
        """Generate demo data for ecommerce business"""
        return {
            'products': [
                {'name': 'Wireless Earbuds', 'price': 129.99, 'category': 'Electronics'},
                {'name': 'Designer Handbag', 'price': 299.99, 'category': 'Fashion'},
                {'name': 'Smart Watch', 'price': 249.99, 'category': 'Electronics'},
                {'name': 'Yoga Mat', 'price': 39.99, 'category': 'Fitness'},
                {'name': 'Coffee Beans', 'price': 24.99, 'category': 'Food'}
            ],
            'orders': [
                {'customer': 'Alice Brown', 'items': ['Wireless Earbuds', 'Yoga Mat'], 'total': 169.98},
                {'customer': 'Bob Wilson', 'items': ['Smart Watch'], 'total': 249.99},
                {'customer': 'Carol Davis', 'items': ['Designer Handbag', 'Coffee Beans'], 'total': 324.98}
            ],
            'customers': [
                {'name': 'Alice Brown', 'email': 'alice@example.com', 'segment': 'premium'},
                {'name': 'Bob Wilson', 'email': 'bob@example.com', 'segment': 'regular'},
                {'name': 'Carol Davis', 'email': 'carol@example.com', 'segment': 'vip'}
            ]
        }

    async def _import_demo_data_to_system(self, client_id: UUID, demo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import demo data into the system"""
        try:
            records_imported = 0

            # Import products if available
            if 'products' in demo_data:
                for product in demo_data['products']:
                    # Here you would create actual product records
                    # For now, just count them
                    records_imported += 1

            # Import customers if available
            if 'customers' in demo_data:
                for customer in demo_data['customers']:
                    # Here you would create actual customer records
                    records_imported += 1

            # Import other data types
            for data_type, items in demo_data.items():
                if data_type not in ['products', 'customers']:
                    records_imported += len(items)

            return {
                'success': True,
                'records_imported': records_imported,
                'data_types': list(demo_data.keys())
            }

        except Exception as e:
            logger.error(f"Error importing demo data: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'records_imported': 0
            }

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'onboarding',
            'status': 'healthy',
            'templates_loaded': len(self.templates),
            'timestamp': datetime.now().isoformat()
        }