#!/usr/bin/env python3
"""
FBS Metadata Discovery Service (Phase 1)
Discovers available modules from reference database for user selection
"""

import logging
import xmlrpc.client
import json
from typing import Dict, List, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class FBSMetadataService:
    """Phase 1: Discover available modules from reference database"""
    
    def __init__(self):
        self.odoo_url = settings.ODOO_CONFIG['BASE_URL']
        self.odoo_db = settings.ODOO_CONFIG['DATABASE']  # fayvad
        self.odoo_user = settings.ODOO_CONFIG['USERNAME']    # dn.kuria@gmail.com
        self.odoo_password = settings.ODOO_CONFIG['PASSWORD']  # MeMiMo@0207
        self.uid = None
        self.models = None
    
    def _connect_to_odoo(self) -> bool:
        """Connect to Odoo reference database"""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.odoo_db, self.odoo_user, self.odoo_password, {})
            
            if not self.uid:
                logger.error("Failed to authenticate with Odoo")
                return False
            
            self.models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            logger.info(f"Successfully connected to reference database: {self.odoo_db}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {str(e)}")
            return False
    
    def discover_available_modules(self) -> Dict[str, Any]:
        """Discover all available modules with metadata"""
        try:
            if not self._connect_to_odoo():
                return {}
            
            # Get all modules (installed + uninstalled)
            modules = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'ir.module.module', 'search_read',
                [[]], {'fields': ['name', 'state', 'summary', 'description', 'dependencies_id']}
            )
            
            available_modules = {}
            
            for module in modules:
                module_name = module['name']
                
                # Skip base technical modules
                if module_name.startswith(('base_', 'web_', 'auth_')):
                    continue
                    
                available_modules[module_name] = {
                    'name': module_name,
                    'display_name': module['summary'] or module_name.replace('_', ' ').title(),
                    'description': module['description'] or '',
                    'state': module['state'],
                    'dependencies': self._extract_dependencies(module.get('dependencies_id', [])),
                    'category': self._classify_module(module_name),
                    'estimated_features': self._estimate_features(module_name)
                }
            
            logger.info(f"Discovered {len(available_modules)} available modules")
            return available_modules
            
        except Exception as e:
            logger.error(f"Error discovering modules: {str(e)}")
            return {}
    
    def _classify_module(self, module_name: str) -> str:
        """Classify module into business category"""
        
        CATEGORY_MAP = {
            'sales': ['sale', 'crm'],
            'accounting': ['account'],
            'inventory': ['stock', 'product'],
            'manufacturing': ['mrp'],
            'hr': ['hr'],
            'project': ['project'],
            'website': ['website'],
            'pos': ['point_of_sale', 'pos'],
            'marketing': ['marketing', 'utm'],
            'other': []
        }
        
        for category, module_prefixes in CATEGORY_MAP.items():
            if any(module_name.startswith(prefix) for prefix in module_prefixes):
                return category
        
        return 'other'
    
    def _estimate_features(self, module_name: str) -> List[str]:
        """Estimate features based on known module patterns"""
        
        FEATURE_PATTERNS = {
            'sale': ['quotations', 'orders', 'customers', 'invoicing'],
            'crm': ['leads', 'opportunities', 'pipeline', 'activities'],
            'stock': ['inventory', 'warehouses', 'transfers', 'adjustments'],
            'mrp': ['manufacturing', 'bom', 'work_orders', 'planning'],
            'account': ['invoicing', 'payments', 'reconciliation', 'reports'],
            'project': ['projects', 'tasks', 'timesheets', 'planning'],
            'hr': ['employees', 'departments', 'attendance', 'leaves'],
            'website': ['pages', 'blog', 'ecommerce', 'forms'],
            'point_of_sale': ['pos', 'payments', 'receipts', 'inventory']
        }
        
        return FEATURE_PATTERNS.get(module_name, ['basic_functionality'])
    
    def _extract_dependencies(self, dependencies_ids: List[int]) -> List[str]:
        """Extract dependency module names from dependency IDs"""
        try:
            if not dependencies_ids:
                return []
            
            # Get dependency module names
            dependencies = self.models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'ir.module.module', 'read',
                [dependencies_ids], {'fields': ['name']}
            )
            
            return [dep['name'] for dep in dependencies]
            
        except Exception as e:
            logger.error(f"Error extracting dependencies: {str(e)}")
            return []
    
    def save_module_catalog(self, output_file: str = 'module_catalog.json') -> Dict[str, Any]:
        """Save discovered module catalog to file"""
        try:
            available_modules = self.discover_available_modules()
            
            with open(output_file, 'w') as f:
                json.dump(available_modules, f, indent=2)
            
            logger.info(f"Module catalog saved to {output_file}")
            return available_modules
            
        except Exception as e:
            logger.error(f"Error saving module catalog: {str(e)}")
            return {} 