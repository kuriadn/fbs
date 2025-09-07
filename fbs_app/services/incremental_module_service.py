"""
FBS Incremental Module Installation Service

Provides intelligent module installation with state detection, dependency resolution,
and incremental installation capabilities. Replaces the problematic --init approach
with safe, differential module management.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from django.conf import settings
from .odoo_client import OdooClient, OdooClientError
from .discovery_service import DiscoveryService

logger = logging.getLogger('fbs_app')


class ModuleDependencyError(Exception):
    """Raised when module dependencies cannot be resolved"""
    pass


class IncrementalModuleService:
    """Service for intelligent, incremental module installation"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        self.odoo_client = OdooClient(solution_name)
        self.discovery_service = DiscoveryService(solution_name)
    
    def install_modules_incrementally(self, requested_modules: List[str], 
                                    database_name: str = None,
                                    force_reinstall: bool = False) -> Dict[str, Any]:
        """
        Install modules incrementally with state detection and dependency resolution
        
        Args:
            requested_modules: List of modules to ensure are installed
            database_name: Optional database name override
            force_reinstall: If True, reinstall existing modules (dangerous!)
            
        Returns:
            Dict: Detailed installation results
        """
        try:
            db_name = database_name or f"fbs_{self.solution_name}_db"
            
            logger.info(f"Starting incremental module installation for database: {db_name}")
            logger.info(f"Requested modules: {requested_modules}")
            
            # Step 1: Discover current state
            state_result = self._discover_current_state(db_name)
            if not state_result['success']:
                return state_result
            
            current_state = state_result['data']
            installed_modules = current_state['installed_modules']
            available_modules = current_state['available_modules']
            
            # Step 2: Calculate delta (what needs to be installed)
            delta_result = self._calculate_installation_delta(
                requested_modules, installed_modules, available_modules, force_reinstall
            )
            
            if not delta_result['success']:
                return delta_result
            
            delta_info = delta_result['data']
            modules_to_install = delta_info['modules_to_install']
            already_installed = delta_info['already_installed']
            unavailable_modules = delta_info['unavailable_modules']
            
            # Step 3: Resolve dependencies
            if modules_to_install:
                dep_result = self._resolve_dependencies(modules_to_install, installed_modules, db_name)
                if not dep_result['success']:
                    return dep_result
                
                modules_with_deps = dep_result['data']['installation_order']
            else:
                modules_with_deps = []
            
            # Step 4: Perform incremental installation
            installation_results = []
            if modules_with_deps:
                install_result = self._install_modules_safely(modules_with_deps, db_name)
                installation_results = install_result.get('data', {}).get('results', [])
            
            # Step 5: Validate installation
            validation_result = self._validate_installation(requested_modules, db_name)
            
            # Step 6: Compile comprehensive results
            return {
                'success': True,
                'data': {
                    'requested_modules': requested_modules,
                    'already_installed': already_installed,
                    'newly_installed': [r['module'] for r in installation_results if r.get('success')],
                    'failed_installations': [r['module'] for r in installation_results if not r.get('success')],
                    'unavailable_modules': unavailable_modules,
                    'installation_results': installation_results,
                    'validation_results': validation_result.get('data', {}),
                    'total_requested': len(requested_modules),
                    'total_already_installed': len(already_installed),
                    'total_newly_installed': len([r for r in installation_results if r.get('success')]),
                    'database_name': db_name
                },
                'message': f'Incremental installation completed. {len(already_installed)} already installed, {len([r for r in installation_results if r.get("success")])} newly installed.'
            }
            
        except Exception as e:
            logger.error(f"Incremental module installation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Incremental module installation failed'
            }
    
    def _discover_current_state(self, database_name: str) -> Dict[str, Any]:
        """Discover current module state in the database"""
        try:
            logger.info(f"Discovering current module state in {database_name}")
            
            # Get installed modules
            installed_result = self.discovery_service.discover_modules(database_name)
            if not installed_result['success']:
                return installed_result
            
            installed_modules_data = installed_result['data']['modules']
            installed_modules = [m['name'] for m in installed_modules_data if m.get('state') == 'installed']
            
            # Get available modules (for dependency resolution)
            available_result = self._get_available_modules(database_name)
            if not available_result['success']:
                logger.warning("Could not get available modules list, using installed only")
                available_modules = installed_modules
            else:
                available_modules = available_result['data']['modules']
            
            logger.info(f"Current state: {len(installed_modules)} installed, {len(available_modules)} available")
            
            return {
                'success': True,
                'data': {
                    'installed_modules': installed_modules,
                    'available_modules': available_modules,
                    'installed_count': len(installed_modules),
                    'available_count': len(available_modules)
                }
            }
            
        except Exception as e:
            logger.error(f"Error discovering current state: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to discover current module state'
            }
    
    def _calculate_installation_delta(self, requested_modules: List[str], 
                                    installed_modules: List[str], 
                                    available_modules: List[str],
                                    force_reinstall: bool = False) -> Dict[str, Any]:
        """Calculate what modules need to be installed"""
        try:
            logger.info("Calculating installation delta")
            
            requested_set = set(requested_modules)
            installed_set = set(installed_modules)
            available_set = set(available_modules)
            
            # Modules already installed
            already_installed = list(requested_set & installed_set)
            
            # Modules that need to be installed
            if force_reinstall:
                modules_to_install = list(requested_set & available_set)
            else:
                modules_to_install = list((requested_set - installed_set) & available_set)
            
            # Requested modules not available
            unavailable_modules = list(requested_set - available_set)
            
            logger.info(f"Delta calculation: {len(already_installed)} already installed, "
                       f"{len(modules_to_install)} to install, {len(unavailable_modules)} unavailable")
            
            return {
                'success': True,
                'data': {
                    'modules_to_install': modules_to_install,
                    'already_installed': already_installed,
                    'unavailable_modules': unavailable_modules,
                    'force_reinstall': force_reinstall
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating installation delta: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to calculate installation delta'
            }
    
    def _resolve_dependencies(self, modules_to_install: List[str], 
                            installed_modules: List[str], 
                            database_name: str) -> Dict[str, Any]:
        """Resolve module dependencies and determine installation order"""
        try:
            logger.info(f"Resolving dependencies for: {modules_to_install}")
            
            # For now, implement basic dependency resolution
            # In production, this would query Odoo's dependency graph
            
            # Get module dependency information
            dependency_map = self._get_module_dependencies(modules_to_install, database_name)
            
            # Perform topological sort to determine installation order
            installation_order = self._topological_sort(modules_to_install, dependency_map, installed_modules)
            
            logger.info(f"Installation order determined: {installation_order}")
            
            return {
                'success': True,
                'data': {
                    'installation_order': installation_order,
                    'dependency_map': dependency_map
                }
            }
            
        except Exception as e:
            logger.error(f"Error resolving dependencies: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to resolve module dependencies'
            }
    
    def _install_modules_safely(self, modules: List[str], database_name: str) -> Dict[str, Any]:
        """Install modules one by one with individual error handling"""
        try:
            logger.info(f"Installing modules safely: {modules}")
            
            results = []
            
            for module in modules:
                logger.info(f"Installing module: {module}")
                
                try:
                    # Use Odoo's XML-RPC API for individual module installation
                    install_result = self._install_single_module(module, database_name)
                    
                    results.append({
                        'module': module,
                        'success': install_result['success'],
                        'message': install_result.get('message', ''),
                        'error': install_result.get('error', '')
                    })
                    
                    if install_result['success']:
                        logger.info(f"✅ Module {module} installed successfully")
                    else:
                        logger.error(f"❌ Module {module} installation failed: {install_result.get('error')}")
                        
                except Exception as e:
                    logger.error(f"❌ Module {module} installation failed with exception: {str(e)}")
                    results.append({
                        'module': module,
                        'success': False,
                        'message': f'Installation failed with exception: {str(e)}',
                        'error': str(e)
                    })
            
            successful_installs = [r for r in results if r['success']]
            failed_installs = [r for r in results if not r['success']]
            
            return {
                'success': len(failed_installs) == 0,
                'data': {
                    'results': results,
                    'successful_count': len(successful_installs),
                    'failed_count': len(failed_installs)
                },
                'message': f'Installation completed: {len(successful_installs)} successful, {len(failed_installs)} failed'
            }
            
        except Exception as e:
            logger.error(f"Error in safe module installation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Safe module installation failed'
            }
    
    def _install_single_module(self, module_name: str, database_name: str) -> Dict[str, Any]:
        """Install a single module using Odoo XML-RPC API"""
        try:
            # Search for the module
            search_result = self.odoo_client.search_read_records(
                model_name='ir.module.module',
                domain=[('name', '=', module_name)],
                fields=['id', 'name', 'state'],
                database=database_name
            )
            
            if not search_result['success'] or not search_result['data']:
                return {
                    'success': False,
                    'error': f'Module {module_name} not found',
                    'message': f'Module {module_name} is not available in the system'
                }
            
            module_record = search_result['data'][0]
            module_id = module_record['id']
            current_state = module_record.get('state', 'uninstalled')
            
            if current_state == 'installed':
                return {
                    'success': True,
                    'message': f'Module {module_name} is already installed',
                    'already_installed': True
                }
            
            # Install the module
            install_result = self.odoo_client.execute_method(
                model_name='ir.module.module',
                method_name='button_immediate_install',
                record_ids=[module_id],
                args=[],
                kwargs={},
                database=database_name
            )
            
            if install_result['success']:
                return {
                    'success': True,
                    'message': f'Module {module_name} installed successfully',
                    'module_id': module_id
                }
            else:
                return {
                    'success': False,
                    'error': install_result.get('error', 'Unknown installation error'),
                    'message': f'Failed to install module {module_name}'
                }
                
        except Exception as e:
            logger.error(f"Error installing single module {module_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Exception during installation of {module_name}'
            }
    
    def _validate_installation(self, requested_modules: List[str], database_name: str) -> Dict[str, Any]:
        """Validate that all requested modules are properly installed"""
        try:
            logger.info("Validating module installation")
            
            # Re-discover modules to check current state
            discovery_result = self.discovery_service.discover_modules(database_name)
            if not discovery_result['success']:
                return discovery_result
            
            installed_modules_data = discovery_result['data']['modules']
            currently_installed = [m['name'] for m in installed_modules_data if m.get('state') == 'installed']
            
            validation_results = []
            for module in requested_modules:
                is_installed = module in currently_installed
                validation_results.append({
                    'module': module,
                    'installed': is_installed,
                    'status': 'OK' if is_installed else 'MISSING'
                })
            
            all_installed = all(r['installed'] for r in validation_results)
            missing_count = len([r for r in validation_results if not r['installed']])
            
            return {
                'success': all_installed,
                'data': {
                    'validation_results': validation_results,
                    'all_installed': all_installed,
                    'missing_count': missing_count,
                    'currently_installed': currently_installed
                },
                'message': f'Validation completed: {missing_count} modules missing' if missing_count > 0 else 'All modules successfully installed'
            }
            
        except Exception as e:
            logger.error(f"Error validating installation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Installation validation failed'
            }
    
    def _get_available_modules(self, database_name: str) -> Dict[str, Any]:
        """Get list of all available modules in Odoo"""
        try:
            # Query all modules (installed, uninstalled, available)
            result = self.odoo_client.search_read_records(
                model_name='ir.module.module',
                domain=[],  # Get all modules
                fields=['name', 'state', 'description'],
                database=database_name
            )
            
            if result['success']:
                modules = [m['name'] for m in result['data']]
                return {
                    'success': True,
                    'data': {
                        'modules': modules,
                        'count': len(modules)
                    }
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error getting available modules: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_module_dependencies(self, modules: List[str], database_name: str) -> Dict[str, List[str]]:
        """Get dependency information for modules"""
        # Simplified dependency map - in production, this would query Odoo
        # Common Odoo module dependencies
        dependency_map = {
            'account': ['base'],
            'sale': ['base', 'product'],
            'purchase': ['base', 'product'],
            'stock': ['base', 'product'],
            'mrp': ['base', 'product', 'stock'],
            'project': ['base'],
            'hr': ['base'],
            'website': ['base', 'web'],
            'ecommerce': ['base', 'website', 'sale'],
            'account_asset': ['base', 'account'],
            'contract': ['base', 'account', 'sale'],
        }
        
        result = {}
        for module in modules:
            result[module] = dependency_map.get(module, ['base'])
        
        return result
    
    def _topological_sort(self, modules: List[str], dependency_map: Dict[str, List[str]], 
                         installed_modules: List[str]) -> List[str]:
        """Perform topological sort to determine installation order"""
        # Simple topological sort implementation
        # In production, this would be more sophisticated
        
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(module):
            if module in temp_visited:
                raise ModuleDependencyError(f"Circular dependency detected involving {module}")
            
            if module in visited:
                return
            
            temp_visited.add(module)
            
            # Visit dependencies first
            for dep in dependency_map.get(module, []):
                if dep not in installed_modules and dep in modules:
                    visit(dep)
            
            temp_visited.remove(module)
            visited.add(module)
            result.append(module)
        
        for module in modules:
            if module not in visited:
                visit(module)
        
        return result
    
    def get_installation_status(self, database_name: str = None) -> Dict[str, Any]:
        """Get current installation status of all modules"""
        try:
            db_name = database_name or f"fbs_{self.solution_name}_db"
            
            discovery_result = self.discovery_service.discover_modules(db_name)
            if not discovery_result['success']:
                return discovery_result
            
            modules_data = discovery_result['data']['modules']
            
            status_summary = {
                'installed': [m for m in modules_data if m.get('state') == 'installed'],
                'to_install': [m for m in modules_data if m.get('state') == 'to install'],
                'to_upgrade': [m for m in modules_data if m.get('state') == 'to upgrade'],
                'uninstalled': [m for m in modules_data if m.get('state') == 'uninstalled'],
            }
            
            return {
                'success': True,
                'data': {
                    'database_name': db_name,
                    'status_summary': status_summary,
                    'total_modules': len(modules_data),
                    'installed_count': len(status_summary['installed']),
                    'modules': modules_data
                },
                'message': f'Status retrieved for {len(modules_data)} modules'
            }
            
        except Exception as e:
            logger.error(f"Error getting installation status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get installation status'
            }
