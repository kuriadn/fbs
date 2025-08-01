from django.core.management.base import BaseCommand, CommandError
from fayvad_core.generation.api_generator import FBSAPIGenerator
import json

class Command(BaseCommand):
    help = 'Generate FBS APIs for a solution based on discovered capabilities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--solution-name',
            type=str,
            required=True,
            help='Name of the solution to generate APIs for'
        )
        
        parser.add_argument(
            '--domain',
            type=str,
            help='Specific domain to generate APIs for (optional)'
        )
        
        parser.add_argument(
            '--models',
            type=str,
            help='Comma-separated list of specific models to generate APIs for'
        )
        
        parser.add_argument(
            '--output-format',
            type=str,
            choices=['json', 'table', 'simple'],
            default='json',
            help='Output format for results'
        )

    def handle(self, *args, **options):
        solution_name = options['solution_name']
        domain = options.get('domain')
        models_str = options.get('models')
        output_format = options['output_format']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Generating APIs for solution: {solution_name}')
        )
        
        try:
            # Initialize API generator
            api_generator = FBSAPIGenerator(solution_name, domain)
            
            if models_str:
                # Generate APIs for specific models
                models = [model.strip() for model in models_str.split(',')]
                self.stdout.write(f'   Generating APIs for models: {", ".join(models)}')
                
                if not domain:
                    raise CommandError('Domain is required when specifying models')
                
                result = api_generator.generate_domain_apis(domain, models)
            else:
                # Try FBS discovery approach first, fallback to direct Odoo connection
                self.stdout.write('   Generating APIs from FBS discovery...')
                result = api_generator.generate_apis_from_fbs_discovery()
                
                if result['status'] != 'success':
                    self.stdout.write('   FBS discovery failed, trying direct Odoo connection...')
                    result = api_generator.generate_all_apis()
            
            # Display results
            if result['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {result["message"]}')
                )
                
                if 'generated_apis' in result:
                    generated_apis = result['generated_apis']
                    self.stdout.write(f'   Domains generated: {len(generated_apis)}')
                    
                    for api_domain, api_data in generated_apis.items():
                        self.stdout.write(f'   📦 {api_domain}:')
                        self.stdout.write(f'      Service file: {api_data.get("service_file", "N/A")}')
                        self.stdout.write(f'      Viewset file: {api_data.get("viewset_file", "N/A")}')
                        self.stdout.write(f'      Endpoints: {len(api_data.get("endpoints", []))}')
                        self.stdout.write(f'      Models: {len(api_data.get("models", []))}')
                
                if 'models_discovered' in result:
                    self.stdout.write(f'   Models discovered: {result["models_discovered"]}')
                
                if 'domains_generated' in result:
                    self.stdout.write(f'   Domains generated: {result["domains_generated"]}')
                
                # Get API endpoints
                endpoints = api_generator.get_api_endpoints(domain)
                if endpoints:
                    self.stdout.write(f'   📋 Total endpoints: {len(endpoints)}')
                    
                    # Show sample endpoints
                    sample_endpoints = endpoints[:5]
                    for endpoint in sample_endpoints:
                        self.stdout.write(f'      {endpoint.get("method", "GET")} {endpoint.get("url", "")}')
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ {result["message"]}')
                )
                if 'errors' in result:
                    for error in result['errors']:
                        self.stdout.write(f'   - {error}')
            
            # Display detailed results
            self._display_results(result, output_format)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error generating APIs: {str(e)}')
            )
            raise CommandError(f'API generation failed: {str(e)}')

    def _display_results(self, results, output_format):
        """Display results in specified format"""
        if output_format == 'json':
            self.stdout.write('\n📄 Detailed Results (JSON):')
            self.stdout.write(json.dumps(results, indent=2, default=str))
        elif output_format == 'table':
            self.stdout.write('\n📊 Results Table:')
            # Simple table format for key-value pairs
            if isinstance(results, dict):
                for key, value in results.items():
                    if isinstance(value, (str, int, float, bool)):
                        self.stdout.write(f'{key:<20} | {value}')
        elif output_format == 'simple':
            # Already displayed in handle method
            pass 