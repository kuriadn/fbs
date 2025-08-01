#!/usr/bin/env python3
"""
Schema Generator for FBS Database Mirror Creation
Extracts critical information from Odoo discoveries for PostgreSQL schema generation
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class FBSSchemaGenerator:
    """Generate comprehensive database schemas from Odoo discoveries"""
    
    def __init__(self):
        self.odoo_to_postgres_type_mapping = {
            'char': 'VARCHAR',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'float': 'NUMERIC',
            'boolean': 'BOOLEAN',
            'date': 'DATE',
            'datetime': 'TIMESTAMP',
            'binary': 'BYTEA',
            'many2one': 'INTEGER',  # Foreign key
            'one2many': 'INTEGER',  # Foreign key in related table
            'many2many': 'INTEGER',  # Junction table
            'selection': 'VARCHAR',
            'json': 'JSONB',
            'monetary': 'NUMERIC'
        }
    
    def generate_comprehensive_schema(self, discoveries: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """
        Generate comprehensive schema definition for database mirror creation
        
        Args:
            discoveries: Complete discovery results from Odoo
            domain: Business domain (e.g., 'rental', 'ecommerce')
            
        Returns:
            Comprehensive schema definition with all critical information
        """
        try:
            schema_definition = {
                'domain': domain,
                'metadata': {
                    'total_models': 0,
                    'total_tables': 0,
                    'total_relationships': 0,
                    'total_workflows': 0,
                    'total_bi_features': 0
                },
                'tables': {},
                'relationships': {},
                'workflows': {},
                'bi_features': {},
                'constraints': {},
                'indexes': {}
            }
            
            # Process models into tables
            if 'models' in discoveries and discoveries['models'].get('status') == 'success':
                models_data = discoveries['models'].get('discovered_models', {})
                schema_definition['metadata']['total_models'] = len(models_data)
                
                for model_name, model_data in models_data.items():
                    table_schema = self._generate_table_schema(model_name, model_data)
                    if table_schema:
                        table_name = self._get_table_name(model_name)
                        schema_definition['tables'][table_name] = table_schema
                        schema_definition['metadata']['total_tables'] += 1
            
            # Process workflows
            if 'workflows' in discoveries and discoveries['workflows'].get('status') == 'success':
                workflows_data = discoveries['workflows'].get('discovered_workflows', {})
                schema_definition['metadata']['total_workflows'] = len(workflows_data)
                
                for model_name, workflow_data in workflows_data.items():
                    workflow_schema = self._generate_workflow_schema(model_name, workflow_data)
                    if workflow_schema:
                        schema_definition['workflows'][model_name] = workflow_schema
            
            # Process BI features
            if 'bi_features' in discoveries and discoveries['bi_features'].get('status') == 'success':
                bi_data = discoveries['bi_features'].get('discovered_bi_features', {})
                schema_definition['metadata']['total_bi_features'] = len(bi_data)
                
                for model_name, bi_data_item in bi_data.items():
                    bi_schema = self._generate_bi_schema(model_name, bi_data_item)
                    if bi_schema:
                        schema_definition['bi_features'][model_name] = bi_schema
            
            # Generate relationships and constraints
            schema_definition['relationships'] = self._extract_relationships(schema_definition['tables'])
            schema_definition['metadata']['total_relationships'] = len(schema_definition['relationships'])
            
            # Generate constraints and indexes
            schema_definition['constraints'] = self._generate_constraints(schema_definition['tables'])
            schema_definition['indexes'] = self._generate_indexes(schema_definition['tables'])
            
            return schema_definition
            
        except Exception as e:
            logger.error(f"Error generating comprehensive schema: {str(e)}")
            return {'error': str(e)}
    
    def _generate_table_schema(self, model_name: str, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate table schema from model data"""
        try:
            table_name = self._get_table_name(model_name)
            fields = model_data.get('fields', {})
            
            table_schema = {
                'table_name': table_name,
                'model_name': model_name,
                'description': model_data.get('model_info', {}).get('name', model_name),
                'columns': {},
                'primary_key': 'id',
                'foreign_keys': [],
                'unique_constraints': [],
                'check_constraints': [],
                'defaults': {}
            }
            
            # Add standard Odoo fields
            table_schema['columns']['id'] = {
                'type': 'INTEGER',
                'constraints': ['PRIMARY KEY', 'NOT NULL'],
                'description': 'Primary key'
            }
            
            table_schema['columns']['create_date'] = {
                'type': 'TIMESTAMP',
                'constraints': ['NOT NULL'],
                'default': 'CURRENT_TIMESTAMP',
                'description': 'Creation timestamp'
            }
            
            table_schema['columns']['write_date'] = {
                'type': 'TIMESTAMP',
                'constraints': ['NOT NULL'],
                'default': 'CURRENT_TIMESTAMP',
                'description': 'Last update timestamp'
            }
            
            table_schema['columns']['create_uid'] = {
                'type': 'INTEGER',
                'constraints': ['NOT NULL'],
                'description': 'User who created the record'
            }
            
            table_schema['columns']['write_uid'] = {
                'type': 'INTEGER',
                'constraints': ['NOT NULL'],
                'description': 'User who last updated the record'
            }
            
            # Process model fields
            for field_name, field_data in fields.items():
                column_schema = self._generate_column_schema(field_name, field_data)
                if column_schema:
                    table_schema['columns'][field_name] = column_schema
                    
                    # Track foreign keys
                    if field_data.get('type') == 'many2one' and field_data.get('relation'):
                        table_schema['foreign_keys'].append({
                            'column': field_name,
                            'references': self._get_table_name(field_data['relation']),
                            'on_delete': field_data.get('on_delete', 'RESTRICT')
                        })
            
            return table_schema
            
        except Exception as e:
            logger.error(f"Error generating table schema for {model_name}: {str(e)}")
            return None
    
    def _generate_column_schema(self, field_name: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate column schema from field data"""
        try:
            odoo_type = field_data.get('type', 'char')
            postgres_type = self.odoo_to_postgres_type_mapping.get(odoo_type, 'VARCHAR')
            
            column_schema = {
                'type': postgres_type,
                'constraints': [],
                'description': field_data.get('description', field_name)
            }
            
            # Add size for VARCHAR fields
            if postgres_type == 'VARCHAR' and field_data.get('size'):
                column_schema['type'] = f"VARCHAR({field_data['size']})"
            elif postgres_type == 'VARCHAR' and odoo_type == 'char':
                column_schema['type'] = 'VARCHAR(255)'  # Default size
            
            # Add constraints
            if field_data.get('required', False):
                column_schema['constraints'].append('NOT NULL')
            
            if field_data.get('readonly', False):
                column_schema['constraints'].append('READONLY')  # Custom constraint
            
            # Handle selection fields
            if odoo_type == 'selection' and field_data.get('selection'):
                selection_values = self._parse_selection_values(field_data['selection'])
                if selection_values:
                    column_schema['check_constraint'] = f"CHECK ({field_name} IN {selection_values})"
            
            return column_schema
            
        except Exception as e:
            logger.error(f"Error generating column schema for {field_name}: {str(e)}")
            return None
    
    def _generate_workflow_schema(self, model_name: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow schema from workflow data"""
        try:
            workflow_schema = {
                'model_name': model_name,
                'table_name': self._get_table_name(model_name),
                'states': workflow_data.get('states', []),
                'transitions': workflow_data.get('transitions', []),
                'triggers': workflow_data.get('triggers', []),
                'approval_process': workflow_data.get('approval_process', {}),
                'workflow_actions': workflow_data.get('workflow_actions', []),
                'validation_rules': workflow_data.get('validation_rules', [])
            }
            
            return workflow_schema
            
        except Exception as e:
            logger.error(f"Error generating workflow schema for {model_name}: {str(e)}")
            return None
    
    def _generate_bi_schema(self, model_name: str, bi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate BI schema from BI data"""
        try:
            bi_schema = {
                'model_name': model_name,
                'table_name': self._get_table_name(model_name),
                'reports': bi_data.get('reports', []),
                'dashboards': bi_data.get('dashboards', []),
                'metrics': bi_data.get('metrics', [])
            }
            
            return bi_schema
            
        except Exception as e:
            logger.error(f"Error generating BI schema for {model_name}: {str(e)}")
            return None
    
    def _extract_relationships(self, tables: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all relationships from tables"""
        relationships = {}
        
        for table_name, table_schema in tables.items():
            for fk in table_schema.get('foreign_keys', []):
                relationship_key = f"{table_name}.{fk['column']}"
                relationships[relationship_key] = {
                    'from_table': table_name,
                    'from_column': fk['column'],
                    'to_table': fk['references'],
                    'to_column': 'id',  # Odoo convention
                    'type': 'many2one',
                    'on_delete': fk['on_delete']
                }
        
        return relationships
    
    def _generate_constraints(self, tables: Dict[str, Any]) -> Dict[str, Any]:
        """Generate database constraints"""
        constraints = {}
        
        for table_name, table_schema in tables.items():
            table_constraints = []
            
            # Primary key constraint
            table_constraints.append({
                'name': f"{table_name}_pkey",
                'type': 'PRIMARY KEY',
                'columns': ['id']
            })
            
            # Foreign key constraints
            for fk in table_schema.get('foreign_keys', []):
                table_constraints.append({
                    'name': f"{table_name}_{fk['column']}_fkey",
                    'type': 'FOREIGN KEY',
                    'columns': [fk['column']],
                    'references': f"{fk['references']}(id)",
                    'on_delete': fk['on_delete']
                })
            
            # Unique constraints (for name fields)
            for col_name, col_data in table_schema.get('columns', {}).items():
                if 'name' in col_name.lower() and col_name != 'name':
                    table_constraints.append({
                        'name': f"{table_name}_{col_name}_key",
                        'type': 'UNIQUE',
                        'columns': [col_name]
                    })
            
            if table_constraints:
                constraints[table_name] = table_constraints
        
        return constraints
    
    def _generate_indexes(self, tables: Dict[str, Any]) -> Dict[str, Any]:
        """Generate database indexes"""
        indexes = {}
        
        for table_name, table_schema in tables.items():
            table_indexes = []
            
            # Index on create_date for performance
            table_indexes.append({
                'name': f"{table_name}_create_date_idx",
                'columns': ['create_date'],
                'type': 'BTREE'
            })
            
            # Index on state fields for workflow queries
            for col_name, col_data in table_schema.get('columns', {}).items():
                if col_name == 'state':
                    table_indexes.append({
                        'name': f"{table_name}_state_idx",
                        'columns': ['state'],
                        'type': 'BTREE'
                    })
            
            # Index on partner_id for relationship queries
            for col_name, col_data in table_schema.get('columns', {}).items():
                if 'partner_id' in col_name:
                    table_indexes.append({
                        'name': f"{table_name}_partner_id_idx",
                        'columns': [col_name],
                        'type': 'BTREE'
                    })
            
            if table_indexes:
                indexes[table_name] = table_indexes
        
        return indexes
    
    def _get_table_name(self, model_name: str) -> str:
        """Convert Odoo model name to PostgreSQL table name"""
        return model_name.replace('.', '_')
    
    def _parse_selection_values(self, selection_str: str) -> List[str]:
        """Parse Odoo selection field values"""
        try:
            import re
            # Parse selection string like "('draft', 'Draft'), ('sent', 'Sent')"
            matches = re.findall(r"\('([^']+)',\s*'([^']+)'\)", selection_str)
            return [match[0] for match in matches]
        except:
            return []
    
    def generate_sql_creation_script(self, schema_definition: Dict[str, Any]) -> str:
        """Generate PostgreSQL CREATE TABLE scripts"""
        sql_script = []
        
        # Create tables
        for table_name, table_schema in schema_definition.get('tables', {}).items():
            sql_script.append(self._generate_create_table_sql(table_name, table_schema))
        
        # Add constraints
        for table_name, constraints in schema_definition.get('constraints', {}).items():
            for constraint in constraints:
                if constraint['type'] != 'PRIMARY KEY':  # Already in CREATE TABLE
                    sql_script.append(self._generate_constraint_sql(table_name, constraint))
        
        # Add indexes
        for table_name, indexes in schema_definition.get('indexes', {}).items():
            for index in indexes:
                sql_script.append(self._generate_index_sql(table_name, index))
        
        return '\n\n'.join(sql_script)
    
    def _generate_create_table_sql(self, table_name: str, table_schema: Dict[str, Any]) -> str:
        """Generate CREATE TABLE SQL"""
        columns = []
        
        for col_name, col_data in table_schema.get('columns', {}).items():
            col_def = f"{col_name} {col_data['type']}"
            
            # Add constraints
            for constraint in col_data.get('constraints', []):
                col_def += f" {constraint}"
            
            # Add default
            if 'default' in col_data:
                col_def += f" DEFAULT {col_data['default']}"
            
            columns.append(col_def)
        
        # Add primary key
        columns.append(f"PRIMARY KEY ({table_schema['primary_key']})")
        
        # Add foreign keys
        for fk in table_schema.get('foreign_keys', []):
            columns.append(
                f"CONSTRAINT {table_name}_{fk['column']}_fkey "
                f"FOREIGN KEY ({fk['column']}) "
                f"REFERENCES {fk['references']}(id) "
                f"ON DELETE {fk['on_delete']}"
            )
        
        sql = f"CREATE TABLE {table_name} (\n"
        sql += ",\n".join(f"    {col}" for col in columns)
        sql += "\n);"
        
        return sql
    
    def _generate_constraint_sql(self, table_name: str, constraint: Dict[str, Any]) -> str:
        """Generate constraint SQL"""
        if constraint['type'] == 'FOREIGN KEY':
            return (
                f"ALTER TABLE {table_name} "
                f"ADD CONSTRAINT {constraint['name']} "
                f"FOREIGN KEY ({', '.join(constraint['columns'])}) "
                f"REFERENCES {constraint['references']} "
                f"ON DELETE {constraint['on_delete']};"
            )
        elif constraint['type'] == 'UNIQUE':
            return (
                f"ALTER TABLE {table_name} "
                f"ADD CONSTRAINT {constraint['name']} "
                f"UNIQUE ({', '.join(constraint['columns'])});"
            )
        return ""
    
    def _generate_index_sql(self, table_name: str, index: Dict[str, Any]) -> str:
        """Generate index SQL"""
        return (
            f"CREATE INDEX {index['name']} "
            f"ON {table_name} "
            f"USING {index['type']} "
            f"({', '.join(index['columns'])});"
        ) 