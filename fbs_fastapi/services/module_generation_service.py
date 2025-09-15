"""
FBS Module Generation Service

Integrates module generator functionality into FBS FastAPI architecture.
Provides secure, licensed, and tenant-aware module generation capabilities.
"""

import logging
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from core.config import config
from core.dependencies import get_db_session_for_request
from services.odoo_service import OdooService
from services.license_service import LicenseService
from services.dms_service import DMSService
from models.models import ModuleGenerationHistory, GeneratedModule, ModuleTemplate

# Template system imports
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ModuleSpec:
    """Module specification data structure"""
    name: str
    description: str
    author: str
    version: str = "1.0.0"
    category: str = "Custom"
    depends: Optional[List[str]] = None
    models: Optional[List[Dict[str, Any]]] = None
    workflows: Optional[List[Dict[str, Any]]] = None
    views: Optional[List[Dict[str, Any]]] = None
    security: Optional[Dict[str, Any]] = None
    tenant_id: Optional[str] = None
    # RESTORED: Inheritance support from original mod_gen
    inherit_from: Optional[str] = None  # e.g., "res.partner", "sale.order"

    def __post_init__(self):
        if self.depends is None:
            self.depends = ["base"]
        if self.models is None:
            self.models = []
        if self.workflows is None:
            self.workflows = []
        if self.views is None:
            self.views = []
        if self.security is None:
            self.security = {}


class FBSModuleGeneratorEngine:
    """
    FBS-adapted module generation engine

    Integrates with FBS services while maintaining module generation capabilities.
    Now supports Discovery-informed generation for hybrid workflows.
    """

    def __init__(self, odoo_service: OdooService, license_service: LicenseService, dms_service: DMSService, discovery_service=None):
        self.odoo_service = odoo_service
        self.license_service = license_service
        self.dms_service = dms_service
        self.discovery_service = discovery_service  # NEW: Integration with Discovery
        self.templates_dir = Path(config.module_generator_template_dir)

    async def generate_module(self, spec: ModuleSpec, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """
        Generate module with FBS integration

        Args:
            spec: Module specification
            user_id: User requesting generation
            tenant_id: Tenant context

        Returns:
            Generation result with metadata
        """
        # License check
        license_valid = await self.license_service.check_feature_access(
            tenant_id, 'module_generation'
        )
        if not license_valid:
            raise HTTPException(403, "Module generation not licensed for this tenant")

        # Generate files
        files = await self._generate_files(spec)

        # Create ZIP package
        zip_content = self._create_zip_package(files)

        # Store in DMS
        dms_result = await self.dms_service.store_generated_module(
            module_name=spec.name,
            zip_content=zip_content,
            tenant_id=tenant_id,
            user_id=user_id,
            spec=spec.__dict__
        )

        # Log generation
        await self._log_generation(spec, user_id, tenant_id, dms_result)

        return {
            'module_name': spec.name,
            'files_count': len(files),
            'zip_size': len(zip_content),
            'dms_reference': dms_result['reference'],
            'generation_time': datetime.now().isoformat(),
            'tenant_id': tenant_id
        }

    async def generate_and_install(self, spec: ModuleSpec, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """
        Generate and install module directly

        Args:
            spec: Module specification
            user_id: User requesting generation
            tenant_id: Tenant context

        Returns:
            Installation result
        """
        # Generate module first
        generation_result = await self.generate_module(spec, user_id, tenant_id)

        # Install in tenant's Odoo instance
        install_result = await self.odoo_service.install_generated_module(
            module_name=spec.name,
            tenant_db=f"fbs_{tenant_id}",
            zip_content=generation_result['zip_content']
        )

        return {
            **generation_result,
            'installation': install_result
        }

    async def generate_from_discovery(self, discovery_findings: Dict[str, Any], user_id: str, tenant_id: str) -> Dict[str, Any]:
        """
        Generate modules based on Discovery Service findings
        This creates the integration between Discovery and Module Generation

        Args:
            discovery_findings: Results from Discovery Service
            user_id: User requesting generation
            tenant_id: Tenant context

        Returns:
            Generation result based on discovered structures
        """
        if not self.discovery_service:
            raise ValueError("Discovery service not available for integration")

        # Convert discovery findings to module specifications
        module_specs = await self._convert_discovery_to_specs(discovery_findings, tenant_id)

        results = []
        for spec in module_specs:
            result = await self.generate_module(spec, user_id, tenant_id)
            results.append(result)

        return {
            'success': True,
            'message': f'Generated {len(results)} modules from discovery findings',
            'modules': results,
            'integration_type': 'discovery_to_generation'
        }

    async def _convert_discovery_to_specs(self, discovery_findings: Dict[str, Any], tenant_id: str) -> List[ModuleSpec]:
        """
        Convert Discovery findings into ModuleSpec objects for generation
        """
        specs = []

        # Process discovered models
        if 'models' in discovery_findings.get('data', {}):
            for model in discovery_findings['data']['models']:
                model_name = model.get('model', '')
                if model_name:
                    # Create extension module for discovered model
                    spec = ModuleSpec(
                        name=f"{model_name.replace('.', '_')}_extension",
                        description=f"Extension for discovered model {model_name}",
                        author="FBS Discovery Integration",
                        models=[{
                            'name': f"{model_name}.extension",
                            'inherit_from': model_name,  # Inherit from discovered model
                            'description': f"Extension of {model_name}",
                            'fields': [
                                {'name': 'custom_notes', 'type': 'text', 'string': 'Custom Notes'},
                                {'name': 'extension_data', 'type': 'json', 'string': 'Extension Data'}
                            ]
                        }],
                        security={
                            'rules': [{
                                'name': f'{model_name} Extension Access',
                                'model': f"{model_name}.extension",
                                'permissions': ['read', 'write', 'create']
                            }]
                        },
                        tenant_id=tenant_id
                    )
                    specs.append(spec)

        return specs

    async def _generate_files(self, spec: ModuleSpec) -> Dict[str, str]:
        """Generate all module files"""
        files = {}

        # Generate manifest
        files["__manifest__.py"] = self._generate_manifest(spec)

        # Generate models
        if spec.models:
            files.update(self._generate_models(spec))

        # Generate workflows
        if spec.workflows:
            files.update(self._generate_workflows(spec))

        # Generate views
        if spec.views:
            files.update(self._generate_views(spec))

        # Generate security
        if spec.security:
            files.update(self._generate_security(spec))

        # Generate __init__.py files
        files.update(self._generate_init_files(spec))

        return files

    def _generate_manifest(self, spec: ModuleSpec) -> str:
        """Generate __manifest__.py with conditional data files"""
        data_files = []

        # Only include security if it exists
        if spec.security:
            data_files.append('security/ir.model.access.csv')

        # Only include views if they're being generated
        if spec.views:
            data_files.append('views/views.xml')

        # Only include workflows if they exist
        if spec.workflows:
            data_files.append('workflows/workflow.xml')

        return f'''{{
    'name': '{spec.name.replace("_", " ").title()}',
    'version': '{spec.version}',
    'description': """{spec.description}""",
    'author': '{spec.author}',
    'category': '{spec.category}',
    'depends': {spec.depends},
    'data': {data_files},
    'installable': True,
    'auto_install': False,
    'application': False,
}}'''

    def _generate_models(self, spec: ModuleSpec) -> Dict[str, str]:
        """Generate model files"""
        files = {}
        files["models/__init__.py"] = self._generate_models_init(spec)

        for model_spec in spec.models:
            model_name = model_spec['name']
            model_filename = model_name.replace('.', '_')
            model_file = f"models/{model_filename}.py"
            files[model_file] = self._generate_model_class(model_spec)

        return files

    def _generate_model_class(self, model_spec: Dict[str, Any]) -> str:
        """Generate a single model class with inheritance support"""
        model_name = model_spec['name']
        class_name = ''.join(word.capitalize() for word in model_name.split('.'))

        fields_code = self._generate_fields(model_spec.get('fields', []))
        methods_code = self._generate_methods(model_spec.get('methods', []))

        # RESTORED: Inheritance support from original mod_gen
        inherit_code = ""
        if model_spec.get('inherit_from'):
            inherit_code = f"    _inherit = '{model_spec['inherit_from']}'"

        return f'''from odoo import models, fields, api
from odoo.exceptions import ValidationError


class {class_name}(models.Model):
    _name = '{model_name}'{inherit_code}
    _description = '{model_spec.get("description", model_name)}'

    {fields_code}

    {methods_code}
'''

    def _generate_fields(self, fields_spec: List[Dict[str, Any]]) -> str:
        """Generate field definitions"""
        field_lines = []

        for field in fields_spec:
            field_type = field['type']
            field_name = field['name']

            field_def = f"{field_name} = fields.{field_type.title()}("
            params = []

            if field.get('string'):
                params.append(f"string='{field['string']}'")
            if field.get('required'):
                params.append("required=True")
            if field.get('help'):
                params.append(f"help='{field['help']}'")

            field_def += ', '.join(params) + ")"
            field_lines.append(field_def)

        return '\n    '.join(field_lines)

    def _generate_methods(self, methods_spec: List[Dict[str, Any]]) -> str:
        """Generate method definitions"""
        method_lines = []

        for method in methods_spec:
            method_code = f'''
    @api.multi
    def {method['name']}(self):
        """{method.get('description', '')}"""
        {method.get('body', 'pass')}
'''
            method_lines.append(method_code)

        return '\n'.join(method_lines)

    def _generate_workflows(self, spec: ModuleSpec) -> Dict[str, str]:
        """Generate workflow files"""
        files = {}

        if not spec.workflows:
            return files

        for workflow_spec in spec.workflows:
            model_name = workflow_spec.get('model', '')
            if not model_name:
                continue

            # Generate workflow XML file
            workflow_filename = f"{model_name.replace('.', '_')}_workflow.xml"
            files[f"workflows/{workflow_filename}"] = self._generate_workflow_xml(workflow_spec)

        return files

    def _generate_workflow_xml(self, workflow_spec: Dict[str, Any]) -> str:
        """Generate workflow XML from specification"""
        model_name = workflow_spec.get('model', '')
        states = workflow_spec.get('states', [])
        transitions = workflow_spec.get('transitions', [])
        actions = workflow_spec.get('actions', [])

        if not model_name:
            return ""

        workflow_xml = '<?xml version="1.0" encoding="utf-8"?>\n<odoo>\n    <data>\n'

        # Generate state records
        for state in states:
            state_record = self._generate_state_record(model_name, state)
            workflow_xml += state_record

        # Generate transition records
        for transition in transitions:
            transition_record = self._generate_transition_record(model_name, transition)
            workflow_xml += transition_record

        # Generate activity records
        for action in actions:
            activity_record = self._generate_activity_record(model_name, action)
            workflow_xml += activity_record

        workflow_xml += '    </data>\n</odoo>'

        return workflow_xml

    def _generate_state_record(self, model_name: str, state: Dict[str, Any]) -> str:
        """Generate workflow state record"""
        state_name = state.get('name', '')
        state_string = state.get('string', state_name.title())
        state_type = state.get('type', 'normal')

        state_record = f'''
        <record id="state_{model_name.replace('.', '_')}_{state_name}" model="workflow.state">
            <field name="workflow_id" ref="wkf_{model_name.replace('.', '_')}"/>
            <field name="name">{state_name}</field>
            <field name="action">{state_string}</field>
            <field name="kind">{state_type}</field>
        </record>'''

        return state_record

    def _generate_transition_record(self, model_name: str, transition: Dict[str, Any]) -> str:
        """Generate workflow transition record"""
        from_state = transition.get('from', '')
        to_state = transition.get('to', '')
        condition = transition.get('condition', '')
        signal = transition.get('signal', transition.get('action', ''))

        transition_record = f'''
        <record id="trans_{model_name.replace('.', '_')}_{from_state}_to_{to_state}" model="workflow.transition">
            <field name="workflow_id" ref="wkf_{model_name.replace('.', '_')}"/>
            <field name="act_from" ref="state_{model_name.replace('.', '_')}_{from_state}"/>
            <field name="act_to" ref="state_{model_name.replace('.', '_')}_{to_state}"/>
            <field name="condition">{condition}</field>
            <field name="signal">{signal}</field>
        </record>'''

        return transition_record

    def _generate_activity_record(self, model_name: str, action: Dict[str, Any]) -> str:
        """Generate workflow activity record"""
        action_name = action.get('name', '')
        state_name = action.get('state', '')
        action_type = action.get('type', 'function')
        function_name = action.get('function', action_name)

        activity_record = f'''
        <record id="act_{model_name.replace('.', '_')}_{action_name}" model="workflow.activity">
            <field name="workflow_id" ref="wkf_{model_name.replace('.', '_')}"/>
            <field name="name">{action_name}</field>
            <field name="kind">{action_type}</field>
            <field name="action">{function_name}</field>
            <field name="state" ref="state_{model_name.replace('.', '_')}_{state_name}"/>
        </record>'''

        return activity_record

    def _generate_views(self, spec: ModuleSpec) -> Dict[str, str]:
        """Generate view files only if views are specified"""
        files = {}

        # Only generate views if explicitly requested
        if spec.views and spec.models:
            for model in spec.models:
                model_name = model['name']
                files[f"views/{model_name.replace('.', '_')}_views.xml"] = self._generate_model_views(model)

        return files

    def _generate_model_views(self, model_spec: Dict[str, Any]) -> str:
        """Generate basic views for a model"""
        model_name = model_spec['name']
        fields = model_spec.get('fields', [])

        # Generate form view
        form_view = self._generate_form_view(model_name, fields)

        # Generate tree view
        tree_view = self._generate_tree_view(model_name, fields)

        # Generate action
        action = self._generate_action(model_name, model_spec.get('description', model_name))

        # Generate menu (optional)
        menu = self._generate_menu(model_name, model_spec.get('description', model_name))

        return form_view + tree_view + action + menu

    def _generate_form_view(self, model_name: str, fields: List[Dict[str, Any]]) -> str:
        """Generate form view XML"""
        field_elements = []

        # Group fields into logical groups (basic info, details, etc.)
        basic_fields = []
        detail_fields = []

        for field in fields:
            field_name = field['name']
            field_type = field.get('type', 'char')
            required = field.get('required', False)
            readonly = field.get('readonly', False)

            # Skip computed fields from form view
            if field_type in ['one2many', 'many2many']:
                continue

            attrs = []
            if required:
                attrs.append('required="1"')
            if readonly:
                attrs.append('readonly="1"')

            attr_str = ' ' + ' '.join(attrs) if attrs else ''

            field_element = f'<field name="{field_name}"{attr_str}/>'
            basic_fields.append(field_element)

        # Create form view
        form_view = f'''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{model_name.replace('.', '_')}_form_view" model="ir.ui.view">
        <field name="name">{model_name}.form</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <div class="oe_title">
                        <h1><field name="name" placeholder="Name..." required="1"/></h1>
                    </div>
                    <group>
                        {"".join(basic_fields)}
                    </group>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>
</odoo>
'''
        return form_view

    def _generate_tree_view(self, model_name: str, fields: List[Dict[str, Any]]) -> str:
        """Generate tree view XML"""
        # Select appropriate fields for tree view (limit to 6-8 fields)
        tree_fields = []
        field_count = 0
        max_fields = 6

        for field in fields:
            if field_count >= max_fields:
                break

            field_type = field.get('type', 'char')
            # Skip complex fields in tree view
            if field_type not in ['one2many', 'many2many', 'text', 'html']:
                tree_fields.append(f'<field name="{field["name"]}"/>')
                field_count += 1

        # Always include name field first if available
        if any(f['name'] == 'name' for f in fields) and 'name' not in [f.split('"')[1] for f in tree_fields if 'name=' in f]:
            tree_fields.insert(0, '<field name="name"/>')

        tree_view = f'''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{model_name.replace('.', '_')}_tree_view" model="ir.ui.view">
        <field name="name">{model_name}.tree</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <tree>
                {"".join(tree_fields)}
            </tree>
        </field>
    </record>
</odoo>
'''
        return tree_view

    def _generate_action(self, model_name: str, description: str) -> str:
        """Generate window action"""
        action_name = f"{model_name.replace('.', '_')}_action"
        display_name = description.split()[0] if description else model_name.replace('.', ' ').title()

        action = f'''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{action_name}" model="ir.actions.act_window">
        <field name="name">{display_name}</field>
        <field name="res_model">{model_name}</field>
        <field name="view_mode">tree,form</field>
        <field name="help">Manage {display_name.lower()} records</field>
    </record>
</odoo>
'''
        return action

    def _generate_menu(self, model_name: str, description: str) -> str:
        """Generate menu item"""
        menu_id = f"{model_name.replace('.', '_')}_menu"
        action_id = f"{model_name.replace('.', '_')}_action"
        display_name = description.split()[0] if description else model_name.replace('.', ' ').title()

        menu = f'''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem id="{menu_id}"
              name="{display_name}"
              action="{action_id}"
              sequence="10"/>
</odoo>
'''
        return menu

    def _generate_security(self, spec: ModuleSpec) -> Dict[str, str]:
        """Generate security files"""
        files = {}

        # Generate access control CSV
        files["security/ir.model.access.csv"] = self._generate_access_csv(spec)

        # Generate security XML if needed
        security_xml = self._generate_security_xml(spec)
        if security_xml:
            files["security/security.xml"] = security_xml

        return files

    def _generate_access_csv(self, spec: ModuleSpec) -> str:
        """Generate comprehensive access CSV"""
        lines = ["id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"]

        for model in spec.models:
            model_name = model['name']
            model_ref = f"model_{model_name.replace('.', '_')}"

            # User access (read/write/create/delete)
            user_line = f"access_{model_name.replace('.', '_')}_user,{model_name} user,{model_ref},base.group_user,1,1,1,1"
            lines.append(user_line)

            # Manager access (full access)
            manager_line = f"access_{model_name.replace('.', '_')}_manager,{model_name} manager,{model_ref},base.group_system,1,1,1,1"
            lines.append(manager_line)

            # Portal user access (read only, limited)
            portal_line = f"access_{model_name.replace('.', '_')}_portal,{model_name} portal,{model_ref},base.group_portal,1,0,0,0"
            lines.append(portal_line)

        return '\n'.join(lines)

    def _generate_security_xml(self, spec: ModuleSpec) -> Optional[str]:
        """Generate security XML with groups and rules"""
        groups_xml = self._generate_groups_xml(spec)
        rules_xml = self._generate_rules_xml(spec)

        if not groups_xml and not rules_xml:
            return None

        security_xml = '<?xml version="1.0" encoding="utf-8"?>\n<odoo>\n    <data>\n'

        if groups_xml:
            security_xml += groups_xml

        if rules_xml:
            security_xml += rules_xml

        security_xml += '    </data>\n</odoo>'

        return security_xml

    def _generate_groups_xml(self, spec: ModuleSpec) -> Optional[str]:
        """Generate groups XML"""
        if not hasattr(spec, 'security') or not spec.security:
            return None

        groups = spec.security.get('groups', [])
        if not groups:
            return None

        group_records = []

        for group in groups:
            group_id = group.get('id', f"group_{group.get('name', 'unknown').lower().replace(' ', '_')}")
            group_name = group.get('name', 'Unknown Group')
            category = group.get('category', 'Custom')

            group_record = f'''
        <record id="{group_id}" model="res.groups">
            <field name="name">{group_name}</field>
            <field name="category_id" ref="base.module_category_{category.lower()}"/>
        </record>'''

            group_records.append(group_record)

        return '\n'.join(group_records)

    def _generate_rules_xml(self, spec: ModuleSpec) -> Optional[str]:
        """Generate record rules XML"""
        if not hasattr(spec, 'security') or not spec.security:
            return None

        rules = spec.security.get('rules', [])
        if not rules:
            return None

        rule_records = []

        for rule in rules:
            rule_id = rule.get('id', f"rule_{rule.get('name', 'unknown').lower().replace(' ', '_')}")
            rule_name = rule.get('name', 'Unknown Rule')
            model = rule.get('model', '')
            domain = rule.get('domain', '[]')
            groups = rule.get('groups', [])
            permissions = rule.get('permissions', [])

            if not model:
                continue

            # Convert permissions list to boolean fields
            perm_read = '1' if 'read' in permissions else '0'
            perm_write = '1' if 'write' in permissions else '0'
            perm_create = '1' if 'create' in permissions else '0'
            perm_unlink = '1' if 'unlink' in permissions else '0'

            rule_record = f'''
        <record id="{rule_id}" model="ir.rule">
            <field name="name">{rule_name}</field>
            <field name="model_id" ref="model_{model.replace('.', '_')}"/>
            <field name="domain_force">{domain}</field>
            <field name="perm_read">{perm_read}</field>
            <field name="perm_write">{perm_write}</field>
            <field name="perm_create">{perm_create}</field>
            <field name="perm_unlink">{perm_unlink}</field>
        </record>'''

            rule_records.append(rule_record)

            # Add group relations if specified
            for group in groups:
                group_rel_record = f'''
        <record id="{rule_id}_{group}_rel" model="ir.rule.groups.rel">
            <field name="rule_id" ref="{rule_id}"/>
            <field name="group_id" ref="{group}"/>
        </record>'''

                rule_records.append(group_rel_record)

        return '\n'.join(rule_records)

    def _generate_init_files(self, spec: ModuleSpec) -> Dict[str, str]:
        """Generate __init__.py files"""
        files = {
            "__init__.py": self._generate_main_init(spec),
            "models/__init__.py": self._generate_models_init(spec)
        }

        return files

    def _generate_main_init(self, spec: ModuleSpec) -> str:
        """Generate main __init__.py"""
        imports = []

        for model in spec.models:
            model_filename = model['name'].replace('.', '_')
            imports.append(f"from . import models")

        return f'''# -*- coding: utf-8 -*-
from . import models
'''

    def _generate_models_init(self, spec: ModuleSpec) -> str:
        """Generate models/__init__.py"""
        imports = []

        for model in spec.models:
            model_filename = model['name'].replace('.', '_')
            imports.append(f"from . import {model_filename}")

        return '\n'.join(imports)

    def _create_zip_package(self, files: Dict[str, str]) -> bytes:
        """Create ZIP package from files"""
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path, content in files.items():
                zip_file.writestr(file_path, content)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    async def _log_generation(self, spec: ModuleSpec, user_id: str, tenant_id: str, dms_result: Dict[str, Any]):
        """Log module generation activity"""
        async for db in get_db_session_for_request(None):
            log_entry = ModuleGenerationHistory(
                module_name=spec.name,
                user_id=user_id,
                tenant_id=tenant_id,
                generation_time=datetime.now(),
                dms_reference=dms_result['reference'],
                spec_summary=f"Generated {len(spec.models)} models, {len(spec.workflows)} workflows"
            )
            db.add(log_entry)
            await db.commit()


class ModuleGenerationService:
    """
    Main service for module generation within FBS

    Provides high-level interface for module generation with FBS integration.
    """

    def __init__(self):
        self.odoo_service = None  # Will be injected
        self.license_service = None  # Will be injected
        self.dms_service = None  # Will be injected
        self.generator = None

    def initialize_services(self, odoo_service: OdooService, license_service: LicenseService, dms_service: DMSService):
        """Initialize with FBS services"""
        self.odoo_service = odoo_service
        self.license_service = license_service
        self.dms_service = dms_service
        self.generator = FBSModuleGeneratorEngine(odoo_service, license_service, dms_service)

    async def generate_module(self, spec: Dict[str, Any], user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Generate module from specification"""
        if not self.generator:
            raise HTTPException(500, "Module generator not initialized")

        module_spec = ModuleSpec(**spec, tenant_id=tenant_id)
        return await self.generator.generate_module(module_spec, user_id, tenant_id)

    async def generate_and_install(self, spec: Dict[str, Any], user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Generate and install module"""
        if not self.generator:
            raise HTTPException(500, "Module generator not initialized")

        module_spec = ModuleSpec(**spec, tenant_id=tenant_id)
        return await self.generator.generate_and_install(module_spec, user_id, tenant_id)

    async def list_templates(self, tenant_id: str) -> List[Dict[str, Any]]:
        """List available module templates"""
        # This would query the database for available templates
        # For now, return basic templates
        return [
            {
                'name': 'basic_crud',
                'description': 'Basic CRUD module with form and list views',
                'category': 'Basic',
                'models_count': 1,
                'has_workflow': False
            },
            {
                'name': 'workflow_module',
                'description': 'Module with approval workflow',
                'category': 'Workflow',
                'models_count': 1,
                'has_workflow': True
            },
            {
                'name': 'inventory_management',
                'description': 'Inventory tracking module',
                'category': 'Inventory',
                'models_count': 3,
                'has_workflow': True
            }
        ]

    async def validate_specification(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate module specification"""
        errors = []
        warnings = []

        # Basic validation
        required_fields = ['name', 'description', 'author']
        for field in required_fields:
            if field not in spec:
                errors.append(f"Missing required field: {field}")

        if 'models' in spec:
            for i, model in enumerate(spec['models']):
                if 'name' not in model:
                    errors.append(f"Model {i}: missing 'name' field")
                if 'fields' not in model:
                    warnings.append(f"Model {i}: no fields defined")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# Template Management System
class TemplateManager:
    """
    Jinja2 template management for code generation

    Provides template loading, caching, and rendering functionality.
    """

    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = Path(template_dir or config.module_generator_template_dir)
        self._env: Optional[Environment] = None
        self._template_cache: Dict[str, Template] = {}

        self._initialize_environment()

    def _initialize_environment(self):
        """Initialize Jinja2 environment"""
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True, exist_ok=True)

        self._env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

        # Add custom filters
        self._add_custom_filters()
        self._add_custom_functions()

    def _add_custom_filters(self):
        """Add custom Jinja2 filters"""
        if not self._env:
            return

        def snake_to_camel(value: str) -> str:
            parts = value.split('_')
            return ''.join(word.capitalize() for word in parts)

        def snake_to_title(value: str) -> str:
            parts = value.replace('_', ' ').split()
            return ' '.join(word.capitalize() for word in parts)

        def model_to_class(value: str) -> str:
            parts = value.split('.')
            return ''.join(word.capitalize() for word in parts)

        def field_to_string(value: str) -> str:
            return snake_to_title(value)

        self._env.filters['snake_to_camel'] = snake_to_camel
        self._env.filters['snake_to_title'] = snake_to_title
        self._env.filters['model_to_class'] = model_to_class
        self._env.filters['field_to_string'] = field_to_string

    def _add_custom_functions(self):
        """Add custom Jinja2 functions"""
        if not self._env:
            return

        self._env.globals['now'] = datetime.now

        def format_docstring(text: str, indent: int = 4) -> str:
            """Format text as a Python docstring"""
            if not text:
                return ""
            return f'{" " * indent}"""{text}"""'

        self._env.globals['format_docstring'] = format_docstring

    def get_template(self, template_name: str) -> Template:
        """Get a template by name"""
        if template_name in self._template_cache:
            return self._template_cache[template_name]

        if not self._env:
            raise RuntimeError("Template environment not initialized")

        template = self._env.get_template(template_name)
        self._template_cache[template_name] = template
        return template

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with context"""
        template = self.get_template(template_name)
        return template.render(**context)

    def list_templates(self) -> List[str]:
        """List available templates"""
        if not self.template_dir.exists():
            return []

        templates = []
        for file_path in self.template_dir.rglob('*.j2'):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.template_dir)
                templates.append(str(rel_path))

        return templates


# Auto Installer Integration
class AutoInstaller:
    """
    Auto-installer for generated Odoo modules

    Integrates with FBS OdooService for seamless module deployment.
    """

    def __init__(self, odoo_service: OdooService):
        self.odoo_service = odoo_service

    async def install_module(self, module_name: str, zip_content: bytes, tenant_db: str) -> Dict[str, Any]:
        """
        Install generated module in tenant database

        Args:
            module_name: Name of the module to install
            zip_content: ZIP file content
            tenant_db: Target tenant database

        Returns:
            Installation result
        """
        try:
            # Use FBS OdooService to install the module
            result = await self.odoo_service.install_generated_module(
                module_name=module_name,
                tenant_db=tenant_db,
                zip_content=zip_content
            )

            return {
                'success': result.get('success', False),
                'module_name': module_name,
                'installed': result.get('installed', False),
                'module_id': result.get('module_id'),
                'message': result.get('message', 'Installation completed')
            }

        except Exception as e:
            logger.error(f"Module installation failed: {e}")
            return {
                'success': False,
                'module_name': module_name,
                'installed': False,
                'error': str(e),
                'message': 'Installation failed'
            }


# Global service instance
module_generation_service = ModuleGenerationService()
