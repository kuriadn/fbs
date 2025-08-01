#!/usr/bin/env python3
"""
FBS Requirements Resolver
Maps user requirements to specific Odoo modules
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class FBSRequirementsResolver:
    """Resolve user requirements to specific modules"""
    
    INDUSTRY_MODULE_MAP = {
        'manufacturing': ['mrp', 'sale', 'stock', 'purchase', 'account'],
        'retail': ['sale', 'stock', 'account', 'point_of_sale'],
        'consulting': ['project', 'hr_timesheet', 'account', 'sale'],
        'ecommerce': ['website_sale', 'sale', 'stock', 'account'],
        'services': ['project', 'sale', 'account', 'hr_timesheet'],
        'rental': ['sale', 'product', 'account', 'project']  # Using existing modules for rental
    }
    
    FEATURE_MODULE_MAP = {
        'sales_management': ['sale', 'crm'],
        'inventory_control': ['stock', 'product'],
        'manufacturing': ['mrp', 'stock', 'product'],
        'accounting': ['account'],
        'project_management': ['project', 'hr_timesheet'],
        'hr_management': ['hr', 'hr_attendance'],
        'website': ['website'],
        'ecommerce': ['website_sale', 'sale', 'stock'],
        'point_of_sale': ['point_of_sale', 'stock']
    }
    
    def __init__(self, module_catalog: Dict[str, Any]):
        self.module_catalog = module_catalog
    
    def resolve_requirements(self, user_requirements: Dict[str, Any]) -> List[str]:
        """Resolve user requirements to module list"""
        
        if 'industry' in user_requirements:
            return self._resolve_industry_requirements(user_requirements['industry'])
        
        elif 'features' in user_requirements:
            return self._resolve_feature_requirements(user_requirements['features'])
        
        elif 'direct' in user_requirements:
            return self._validate_direct_selection(user_requirements['modules'])
        
        else:
            raise ValueError(f"Unknown requirement type. Must specify 'industry', 'features', or 'direct'")
    
    def _resolve_industry_requirements(self, industry: str) -> List[str]:
        """Resolve industry to recommended modules"""
        
        if industry not in self.INDUSTRY_MODULE_MAP:
            raise ValueError(f"Unknown industry: {industry}")
        
        recommended_modules = self.INDUSTRY_MODULE_MAP[industry]
        return self._resolve_dependencies(recommended_modules)
    
    def _resolve_feature_requirements(self, features: List[str]) -> List[str]:
        """Resolve features to required modules"""
        
        required_modules = []
        
        for feature in features:
            if feature in self.FEATURE_MODULE_MAP:
                required_modules.extend(self.FEATURE_MODULE_MAP[feature])
            else:
                logger.warning(f"Unknown feature '{feature}' ignored")
        
        # Remove duplicates and resolve dependencies
        unique_modules = list(set(required_modules))
        return self._resolve_dependencies(unique_modules)
    
    def _validate_direct_selection(self, selected_modules: List[str]) -> List[str]:
        """Validate and resolve direct module selection"""
        
        # Check all modules exist
        for module in selected_modules:
            if module not in self.module_catalog:
                raise ValueError(f"Module '{module}' not available")
        
        return self._resolve_dependencies(selected_modules)
    
    def _resolve_dependencies(self, modules: List[str]) -> List[str]:
        """Resolve module dependencies"""
        
        all_required = set(modules)
        
        # Add dependencies recursively
        def add_dependencies(module_name: str):
            if module_name in self.module_catalog:
                dependencies = self.module_catalog[module_name].get('dependencies', [])
                for dep in dependencies:
                    if dep not in all_required and dep != 'base':
                        all_required.add(dep)
                        add_dependencies(dep)
        
        for module in modules:
            add_dependencies(module)
        
        resolved_modules = list(all_required)
        logger.info(f"Resolved {len(modules)} modules to {len(resolved_modules)} with dependencies")
        return resolved_modules 