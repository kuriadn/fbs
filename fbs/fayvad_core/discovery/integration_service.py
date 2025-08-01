import logging
from typing import Dict, Any, List
from django.conf import settings
from .services import FBSDiscoveryService
from .schema_service import FBSSchemaService
from .adaptation_service import FBSAdaptationService
from .metadata_service import FBSMetadataService
from .requirements_resolver import FBSRequirementsResolver
from fayvad_core.models import FBSDiscovery, FBSSolutionSchema, FBSSchemaMigration

logger = logging.getLogger(__name__)

class FBSAPIIntegrationService:
    """
    Main integration service that orchestrates discovery and schema management
    for single database approach with table prefixes.
    """
    
    def __init__(self):
        self.discovery_service = FBSDiscoveryService()
        self.schema_service = FBSSchemaService()
        self.adaptation_service = FBSAdaptationService()
        self.metadata_service = FBSMetadataService()
    
    def phase1_metadata_discovery(self) -> Dict[str, Any]:
        """
        Phase 1: Discover available modules from reference database
        
        Returns:
            Module catalog with metadata
        """
        try:
            logger.info("Phase 1: Discovering available modules...")
            module_catalog = self.metadata_service.discover_available_modules()
            
            return {
                'status': 'success',
                'module_catalog': module_catalog,
                'total_modules': len(module_catalog),
                'message': f'Discovered {len(module_catalog)} available modules'
            }
            
        except Exception as e:
            logger.error(f"Error in phase1_metadata_discovery: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def phase2_complete_setup(self, solution_config: dict, user_requirements: dict) -> Dict[str, Any]:
        """
        Phase 2: Complete setup with user-selected modules
        
        Args:
            solution_config: Configuration for the solution
            user_requirements: User requirements (industry, features, or direct modules)
            
        Returns:
            Complete setup results
        """
        try:
            solution_name = solution_config['solution_name']
            
            logger.info(f"Phase 2: Complete setup for {solution_name}")
            
            # Step 1: Get module catalog (from reference database)
            metadata_result = self.phase1_metadata_discovery()
            if metadata_result['status'] != 'success':
                return metadata_result
            
            module_catalog = metadata_result['module_catalog']
            
            # Step 2: Resolve user requirements to modules
            logger.info("Step 2: Resolving user requirements...")
            resolver = FBSRequirementsResolver(module_catalog)
            selected_modules = resolver.resolve_requirements(user_requirements)
            
            logger.info(f"Selected modules: {selected_modules}")
            
            # Step 3: Create solution database with selected modules
            logger.info("Step 3: Creating solution database...")
            from .odoo_installer import OdooInstallerService
            installer = OdooInstallerService()
            db_result = installer.create_solution_database(solution_name, selected_modules)
            
            if db_result['status'] != 'success':
                return db_result
            
            # Step 4: Setup FBS schema in the solution database
            logger.info("Step 4: Setting up FBS schema in solution database...")
            schema_result = self.schema_service.create_solution_schema(solution_config)
            
            if schema_result['status'] != 'success':
                return schema_result
            
            # Step 5: Discover capabilities in the NEW solution database
            logger.info("Step 5: Discovering capabilities in solution database...")
            discovery_results = {}
            
            # Discover models, workflows, and BI features in the solution database
            for discovery_type in ['models', 'workflows', 'bi_features']:
                try:
                    result = self.discovery_service.discover_and_cache(
                        domain=solution_config.get('domain', 'general'),
                        discovery_type=discovery_type,
                        database=db_result['database']  # Use the NEW solution database
                    )
                    discovery_results[discovery_type] = result
                except Exception as e:
                    logger.error(f"Error discovering {discovery_type}: {str(e)}")
                    discovery_results[discovery_type] = {'status': 'error', 'message': str(e)}
            
            return {
                'status': 'success',
                'solution_name': solution_name,
                'database': db_result['database'],
                'selected_modules': selected_modules,
                'modules_installed': db_result.get('modules_installed', []),
                'discovery_results': discovery_results,
                'schema_result': schema_result,
                'message': f'Phase 2 setup completed for {solution_name}'
            }
            
        except Exception as e:
            logger.error(f"Error in phase2_complete_setup: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def solution_operations(self, solution_name: str, operation_type: str, operation_data: dict = None) -> Dict[str, Any]:
        """
        Phase 3: Operations on user's solution database
        
        Args:
            solution_name: Name of the solution
            operation_type: Type of operation (discover, adapt, migrate, etc.)
            operation_data: Additional data for the operation
            
        Returns:
            Operation results
        """
        try:
            # Get solution database name
            db_name = f"fbs_{solution_name}_db"
            
            logger.info(f"Phase 3: Performing {operation_type} on {db_name}")
            
            if operation_type == 'discover':
                # Discover capabilities in the solution database
                discovery_type = operation_data.get('discovery_type', 'models')
                domain = operation_data.get('domain', 'general')
                
                result = self.discovery_service.discover_and_cache(
                    domain=domain,
                    discovery_type=discovery_type,
                    database=db_name  # Use the solution database
                )
                
                return {
                    'status': 'success',
                    'operation': 'discover',
                    'solution_name': solution_name,
                    'database': db_name,
                    'discovery_type': discovery_type,
                    'result': result
                }
            
            elif operation_type == 'adapt':
                # Adapt discoveries for the solution
                domain = operation_data.get('domain', 'general')
                discoveries = operation_data.get('discoveries', {})
                
                adapted_discoveries = self.adaptation_service.adapt_discoveries(domain, discoveries)
                
                return {
                    'status': 'success',
                    'operation': 'adapt',
                    'solution_name': solution_name,
                    'database': db_name,
                    'adapted_discoveries': adapted_discoveries
                }
            
            elif operation_type == 'status':
                # Get solution status
                return self.get_solution_status(solution_name)
            
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown operation type: {operation_type}'
                }
            
        except Exception as e:
            logger.error(f"Error in solution_operations: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def setup_solution(self, solution_config: dict) -> Dict[str, Any]:
        """
        Setup a complete solution with discovery and schema creation in single database.
        
        Args:
            solution_config: Dictionary containing solution configuration
                {
                    'solution_name': 'fayvad_rentals',
                    'domain': 'rental',
                    'database_config': {
                        'name': 'rental_db',
                        'user': 'rental_user',
                        'password': 'rental_password',
                        'host': 'localhost',
                        'port': '5432'
                    },
                    'table_prefix': 'fbs_',
                    'business_prefix': 'rental_',
                    'refresh_discoveries': True
                }
        
        Returns:
            Dict with setup status and details
        """
        try:
            solution_name = solution_config['solution_name']
            domain = solution_config['domain']
            
            logger.info(f"Setting up solution: {solution_name} for domain: {domain}")
            
            # Step 1: Perform discovery and cache results
            discovery_results = {}
            if solution_config.get('refresh_discoveries', True):
                logger.info("Performing fresh discovery...")
                
                # Generate the database name that will be used
                from django.conf import settings
                db_name = settings.FBS_CONFIG['database_naming_pattern'].format(solution_name=solution_name)
                
                # Discover models
                models_discovery = self.discovery_service.discover_and_cache(
                    domain=domain,
                    discovery_type='models',
                    database=db_name
                )
                discovery_results['models'] = models_discovery
                
                # Discover workflows
                workflows_discovery = self.discovery_service.discover_and_cache(
                    domain=domain,
                    discovery_type='workflows',
                    database=db_name
                )
                discovery_results['workflows'] = workflows_discovery
                
                # Discover BI features
                bi_discovery = self.discovery_service.discover_and_cache(
                    domain=domain,
                    discovery_type='bi_features',
                    database=db_name
                )
                discovery_results['bi_features'] = bi_discovery
            
            # Step 2: Create schema in single database
            logger.info("Creating solution schema...")
            schema_result = self.schema_service.create_solution_schema(solution_config)
            
            # Step 3: Adapt discoveries to business domain
            if discovery_results:
                logger.info("Adapting discoveries to business domain...")
                adapted_discoveries = self.adaptation_service.adapt_discoveries(domain, discovery_results)
                
                # Generate schema definitions from adapted discoveries
                logger.info("Generating schema definitions from adapted discoveries...")
                schema_definitions = self._generate_schema_definitions(adapted_discoveries, solution_config)
                
                # Update solution schema with generated definitions
                self._update_solution_schema_definitions(solution_name, schema_definitions)
                
                # Store adapted discoveries in cache
                self._cache_adapted_discoveries(solution_name, adapted_discoveries)
            
            return {
                'status': 'success',
                'solution_name': solution_name,
                'domain': domain,
                'database': schema_result.get('database', ''),
                'discovery_results': discovery_results,
                'adapted_discoveries': adapted_discoveries if discovery_results else {},
                'schema_result': schema_result,
                'message': f'Solution {solution_name} setup completed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error setting up solution: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'solution_name': solution_config.get('solution_name', 'unknown')
            }
    
    def get_solution_status(self, solution_name: str) -> Dict[str, Any]:
        """
        Get comprehensive status of a solution including database and discovery status.
        
        Args:
            solution_name: Name of the solution to check
            
        Returns:
            Dict with solution status details
        """
        try:
            # Get schema status
            schema_status = self.schema_service.get_solution_status(solution_name)
            
            if schema_status['status'] == 'not_found':
                return schema_status
            
            # Get discovery status
            discoveries = self.get_solution_discoveries(solution_name)
            
            # Handle discovery errors gracefully
            if isinstance(discoveries, dict) and 'error' in discoveries:
                discoveries = {'error': discoveries['error']}
            
            # Combine status information
            status = {
                'solution_name': solution_name,
                'schema_status': schema_status,
                'discoveries': discoveries,
                'overall_status': 'active' if schema_status['status'] == 'active' else 'inactive'
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting solution status: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'solution_name': solution_name
            }
    
    def migrate_solution_schema(self, solution_name: str, migration_config: dict = None) -> Dict[str, Any]:
        """
        Migrate solution schema with new discoveries or configuration changes.
        
        Args:
            solution_name: Name of the solution to migrate
            migration_config: Optional migration configuration
            
        Returns:
            Dict with migration status
        """
        try:
            solution = FBSSolutionSchema.objects.get(solution_name=solution_name)
            
            # Get current discoveries
            current_discoveries = self.get_solution_discoveries(solution_name)
            
            # Perform fresh discovery
            fresh_discoveries = {}
            for discovery_type in ['models', 'workflows', 'bi_features']:
                fresh_discoveries[discovery_type] = self.discovery_service.discover_and_cache(
                    domain=solution.domain,
                    discovery_type=discovery_type,
                    database=solution.database_name
                )
            
            # Compare and generate migration SQL
            migration_sql = self._generate_migration_sql(
                current_discoveries, 
                fresh_discoveries, 
                solution
            )
            
            if migration_sql:
                # Execute migration
                migration_result = self._execute_migration_sql(solution, migration_sql)
                
                # Log migration
                self._log_migration(solution_name, migration_sql, 'completed')
                
                return {
                    'status': 'success',
                    'solution_name': solution_name,
                    'migrations_applied': len(migration_sql),
                    'migration_sql': migration_sql,
                    'message': f'Successfully migrated {solution_name}'
                }
            else:
                return {
                    'status': 'success',
                    'solution_name': solution_name,
                    'migrations_applied': 0,
                    'message': f'No migrations needed for {solution_name}'
                }
                
        except Exception as e:
            logger.error(f"Error migrating solution schema: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'solution_name': solution_name
            }
    
    def refresh_solution_discoveries(self, solution_name: str) -> Dict[str, Any]:
        """
        Refresh discoveries for a solution.
        
        Args:
            solution_name: Name of the solution to refresh
            
        Returns:
            Dict with refresh status
        """
        try:
            solution = FBSSolutionSchema.objects.get(solution_name=solution_name)
            
            discovery_results = {}
            
            # Refresh all discovery types
            for discovery_type in ['models', 'workflows', 'bi_features']:
                result = self.discovery_service.discover_and_cache(
                    domain=solution.domain,
                    discovery_type=discovery_type,
                    database=solution.database_name
                )
                discovery_results[discovery_type] = result
            
            return {
                'status': 'success',
                'solution_name': solution_name,
                'discovery_results': discovery_results,
                'message': f'Successfully refreshed discoveries for {solution_name}'
            }
            
        except Exception as e:
            logger.error(f"Error refreshing solution discoveries: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'solution_name': solution_name
            }
    
    def get_solution_discoveries(self, solution_name: str) -> Dict[str, Any]:
        """
        Get all discoveries for a solution.
        
        Args:
            solution_name: Name of the solution
            
        Returns:
            Dict with discovery information
        """
        try:
            solution = FBSSolutionSchema.objects.get(solution_name=solution_name)
            
            discoveries = FBSDiscovery.objects.filter(
                domain=solution.domain,
                is_active=True
            ).order_by('discovery_type', 'name')
            
            discovery_data = {}
            for discovery in discoveries:
                if discovery.discovery_type not in discovery_data:
                    discovery_data[discovery.discovery_type] = []
                
                discovery_data[discovery.discovery_type].append({
                    'name': discovery.name,
                    'version': discovery.version,
                    'metadata': discovery.metadata,
                    'schema_definition': discovery.schema_definition,
                    'discovered_at': discovery.discovered_at.isoformat()
                })
            
            return discovery_data
            
        except FBSSolutionSchema.DoesNotExist:
            return {'error': f'Solution {solution_name} not found'}
        except Exception as e:
            logger.error(f"Error getting solution discoveries: {str(e)}")
            return {'error': str(e)}
    
    def validate_solution_config(self, solution_config: dict) -> Dict[str, Any]:
        """
        Validate solution configuration before setup.
        
        Args:
            solution_config: Solution configuration to validate
            
        Returns:
            Dict with validation results
        """
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['solution_name', 'domain', 'database_config']
        for field in required_fields:
            if field not in solution_config:
                errors.append(f'Missing required field: {field}')
        
        # Database config validation
        if 'database_config' in solution_config:
            db_config = solution_config['database_config']
            required_db_fields = ['user', 'password']  # 'name' is generated dynamically
            for field in required_db_fields:
                if field not in db_config:
                    errors.append(f'Missing required database field: {field}')
        
        # Validate table prefixes
        if 'table_prefix' in solution_config:
            prefix = solution_config['table_prefix']
            if not prefix.endswith('_'):
                warnings.append('Table prefix should end with underscore for clarity')
        
        if 'business_prefix' in solution_config:
            prefix = solution_config['business_prefix']
            if prefix and not prefix.endswith('_'):
                warnings.append('Business prefix should end with underscore for clarity')
        
        # Check if solution already exists
        if 'solution_name' in solution_config:
            try:
                existing = FBSSolutionSchema.objects.get(solution_name=solution_config['solution_name'])
                warnings.append(f'Solution {solution_config["solution_name"]} already exists and will be updated')
            except FBSSolutionSchema.DoesNotExist:
                pass
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def list_solutions(self) -> List[Dict[str, Any]]:
        """
        List all solutions with their status.
        
        Returns:
            List of solution information
        """
        return self.schema_service.list_solutions()
    
    def _generate_schema_definitions(self, discovery_results: dict, solution_config: dict) -> dict:
        """Generate schema definitions from discovery results"""
        
        schema_definitions = {
            'models': {},
            'workflows': {},
            'bi_features': {}
        }
        
        # Process model discoveries
        if 'models' in discovery_results:
            for model_name, model_data in discovery_results['models'].get('discovered_models', {}).items():
                schema_definitions['models'][model_name] = {
                    'fields': model_data.get('fields', {}),
                    'relationships': model_data.get('relationships', {}),
                    'constraints': model_data.get('constraints', {})
                }
        
        # Process workflow discoveries
        if 'workflows' in discovery_results:
            for workflow_name, workflow_data in discovery_results['workflows'].get('discovered_workflows', {}).items():
                schema_definitions['workflows'][workflow_name] = {
                    'steps': workflow_data.get('steps', []),
                    'transitions': workflow_data.get('transitions', []),
                    'conditions': workflow_data.get('conditions', {})
                }
        
        # Process BI feature discoveries
        if 'bi_features' in discovery_results:
            for bi_name, bi_data in discovery_results['bi_features'].get('discovered_bi_features', {}).items():
                schema_definitions['bi_features'][bi_name] = {
                    'reports': bi_data.get('reports', []),
                    'dashboards': bi_data.get('dashboards', []),
                    'metrics': bi_data.get('metrics', [])
                }
        
        return schema_definitions
    
    def _update_solution_schema_definitions(self, solution_name: str, schema_definitions: dict):
        """Update solution schema with generated definitions"""
        
        try:
            solution = FBSSolutionSchema.objects.get(solution_name=solution_name)
            
            # Update schema definition
            current_definition = solution.schema_definition or {}
            current_definition.update(schema_definitions)
            
            solution.schema_definition = current_definition
            solution.save()
            
        except FBSSolutionSchema.DoesNotExist:
            logger.warning(f"Solution {solution_name} not found for schema definition update")
    
    def _generate_migration_sql(self, current_discoveries: dict, fresh_discoveries: dict, solution) -> List[str]:
        """Generate migration SQL based on discovery differences"""
        
        migration_sql = []
        
        # Compare model discoveries
        current_models = current_discoveries.get('models', {}).get('discovered_models', {})
        fresh_models = fresh_discoveries.get('models', {}).get('discovered_models', {})
        
        # Find new models
        for model_name, model_data in fresh_models.items():
            if model_name not in current_models:
                # Generate CREATE TABLE SQL for new model
                table_name = f"{solution.business_prefix}{model_name.replace('.', '_')}"
                create_sql = self._generate_create_table_sql(table_name, model_data)
                if create_sql:
                    migration_sql.append(create_sql)
        
        return migration_sql
    
    def _generate_create_table_sql(self, table_name: str, model_data: dict) -> str:
        """Generate CREATE TABLE SQL from model data"""
        
        fields = model_data.get('fields', {})
        if not fields:
            return ""
        
        field_definitions = []
        for field_name, field_info in fields.items():
            field_type = field_info.get('type', 'VARCHAR(255)')
            field_def = f"{field_name} {field_type}"
            
            if field_info.get('required', False):
                field_def += " NOT NULL"
            
            if field_info.get('unique', False):
                field_def += " UNIQUE"
            
            field_definitions.append(field_def)
        
        if field_definitions:
            return f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    {', '.join(field_definitions)},
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """
        
        return ""
    
    def _execute_migration_sql(self, solution, migration_sql: List[str]) -> Dict[str, Any]:
        """Execute migration SQL statements"""
        
        import psycopg2
        
        connection = psycopg2.connect(
            database=solution.database_name,
            user=solution.database_user,
            password=solution.database_password,
            host='localhost',
            port='5432'
        )
        
        try:
            with connection.cursor() as cursor:
                for sql in migration_sql:
                    cursor.execute(sql)
            
            connection.commit()
            
            return {
                'status': 'success',
                'migrations_executed': len(migration_sql)
            }
            
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()
    
    def _log_migration(self, solution_name: str, migration_sql: List[str], status: str):
        """Log migration in FBS schema migrations table"""
        
        for sql in migration_sql:
            FBSSchemaMigration.objects.create(
                solution_name=solution_name,
                migration_type='schema_update',
                table_name='multiple',  # Could be more specific
                sql_statement=sql,
                status=status
            )
    
    def _cache_adapted_discoveries(self, solution_name: str, adapted_discoveries: Dict[str, Any]):
        """Cache adapted discoveries for the solution"""
        try:
            # Store adapted discoveries in FBSDiscovery table
            for discovery_type, discoveries in adapted_discoveries.items():
                if discovery_type.startswith('adapted_'):
                    original_type = discovery_type.replace('adapted_', '')
                    for model_name, discovery_data in discoveries.items():
                        FBSDiscovery.objects.update_or_create(
                            discovery_type=original_type,
                            domain=adapted_discoveries['domain'],
                            name=model_name,
                            defaults={
                                'metadata': discovery_data,
                                'schema_definition': discovery_data.get('business_logic', {}),
                                'is_active': True
                            }
                        )
            logger.info(f"Cached adapted discoveries for solution: {solution_name}")
        except Exception as e:
            logger.error(f"Error caching adapted discoveries: {str(e)}") 