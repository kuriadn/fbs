"""
Django management command for generating service interfaces based on discovered Odoo capabilities.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json
import logging

logger = logging.getLogger('fbs_app')


class Command(BaseCommand):
    help = 'Generate service interfaces based on discovered Odoo capabilities'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--solution',
            type=str,
            help='Solution name for service interface generation'
        )
        parser.add_argument(
            '--database',
            type=str,
            help='Database name for service interface generation'
        )
        parser.add_argument(
            '--token',
            type=str,
            help='Odoo authentication token'
        )
        parser.add_argument(
            '--models',
            type=str,
            help='Comma-separated list of model names to generate service interfaces for'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path for generated service interface configuration'
        )
        parser.add_argument(
            '--discover',
            action='store_true',
            help='Discover models automatically before generating service interfaces'
        )
    
    def handle(self, *args, **options):
        try:
            solution_name = options.get('solution')
            database_name = options.get('database')
            token = options.get('token')
            models_str = options.get('models')
            output_path = options.get('output')
            discover = options.get('discover')
            
            # Validate required parameters
            if not all([solution_name, database_name, token]):
                raise CommandError('Solution name, database, and token are required')
            
            # Import services
            from fbs_app.services import FBSServiceGenerator, DiscoveryService
            
            service_generator = FBSServiceGenerator()
            discovery_service = DiscoveryService()
            
            # Discover models if requested
            if discover:
                self.stdout.write('Discovering models...')
                discovery_result = discovery_service.discover_models(
                    token=token,
                    database=database_name
                )
                
                if not discovery_result['success']:
                    raise CommandError(f"Model discovery failed: {discovery_result.get('error')}")
                
                discovered_models = discovery_result.get('models', [])
                self.stdout.write(f"Discovered {len(discovered_models)} models")
                
                # Generate service interfaces for all discovered models
                models_data = []
                for model in discovered_models:
                    models_data.append({
                        'model_name': model['name'],
                        'fields': model.get('fields', []),
                        'database_name': database_name,
                        'token': token
                    })
                
                # Bulk generate service interfaces
                result = service_generator.generate_bulk_services(models_data)
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully generated {result['successful_generations']} service interfaces out of {result['total_models']} models"
                        )
                    )
                else:
                    raise CommandError(f"Bulk service interface generation failed: {result.get('error')}")
                
            else:
                # Generate service interfaces for specific models
                if not models_str:
                    raise CommandError('Models must be specified when not using discovery mode')
                
                model_names = [name.strip() for name in models_str.split(',')]
                
                # Get model fields for each model
                models_data = []
                for model_name in model_names:
                    fields_result = discovery_service.get_model_fields(
                        model_name=model_name,
                        token=token,
                        database=database_name
                    )
                    
                    if fields_result['success']:
                        models_data.append({
                            'model_name': model_name,
                            'fields': fields_result.get('fields', []),
                            'database_name': database_name,
                            'token': token
                        })
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Failed to get fields for model {model_name}: {fields_result.get('error')}"
                            )
                        )
                
                # Generate service interfaces for specified models
                for model_data in models_data:
                    result = service_generator.generate_model_service(
                        model_name=model_data['model_name'],
                        model_fields=model_data['fields'],
                        database_name=model_data['database_name'],
                        token=model_data['token']
                    )
                    
                    if result['success']:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully generated service interface for model {model_data['model_name']}"
                            )
                        )
                        
                        # Show capabilities
                        for capability in result.get('capabilities', []):
                            self.stdout.write(f"  - {capability}")
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed to generate service interface for model {model_data['model_name']}: {result.get('error')}"
                            )
                        )
            
            # Get generated service interfaces summary
            services_summary = service_generator.get_generated_services()
            
            if services_summary['success']:
                self.stdout.write(f"\nTotal generated service interfaces: {services_summary['total_services']}")
                self.stdout.write("Generated service interfaces:")
                for service_name in services_summary['generated_services']:
                    self.stdout.write(f"  - {service_name}")
            
            # Save configuration to file if output path specified
            if output_path:
                self._save_service_configuration(services_summary, output_path)
                self.stdout.write(f"Service interface configuration saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error in generate_services command: {str(e)}")
            raise CommandError(f"Service interface generation failed: {str(e)}")
    
    def _save_service_configuration(self, services_summary, output_path):
        """Save service interface configuration to file"""
        try:
            config_data = {
                'generated_at': str(settings.TIME_ZONE),
                'total_services': services_summary['total_services'],
                'services': services_summary['generated_services'],
                'service_details': {}
            }
            
            # Add detailed information for each service interface
            for service_name in services_summary['generated_services']:
                service_info = services_summary['service_details'].get(service_name, {})
                config_data['service_details'][service_name] = {
                    'model_fields': service_info.get('model_fields', []),
                    'database_name': service_info.get('database_name'),
                    'capabilities': [
                        f'create_{service_name}',
                        f'get_{service_name}',
                        f'update_{service_name}',
                        f'delete_{service_name}',
                        f'list_{service_name}s'
                    ]
                }
            
            # Write to file
            with open(output_path, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving service interface configuration: {str(e)}")
            raise CommandError(f"Failed to save service interface configuration: {str(e)}")
