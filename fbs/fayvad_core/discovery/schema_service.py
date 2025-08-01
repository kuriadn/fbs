import psycopg2
import json
import logging
from typing import Dict, Any, List
from django.conf import settings
from fayvad_core.models import FBSSolutionSchema, FBSSchemaMigration

logger = logging.getLogger(__name__)

class FBSSchemaService:
    """
    Service for managing dynamic schema creation and migration in a single database.
    Creates both FBS system tables and business tables in user-specified database.
    """
    
    def __init__(self):
        self.connection = None
    
    def create_solution_schema(self, solution_config: dict) -> Dict[str, Any]:
        """
        Create both FBS system tables and business tables in single user-specified database.
        Dynamically creates the database if it doesn't exist.
        
        Args:
            solution_config: Dictionary containing solution_name, database_config, table_prefix, business_prefix
            
        Returns:
            Dict with creation status and details
        """
        try:
            solution_name = solution_config.get('solution_name', 'testing')
            db_config = solution_config['database_config']
            table_prefix = solution_config.get('table_prefix', 'fbs_')
            business_prefix = solution_config.get('business_prefix', '')
            
            # Generate database name using the pattern
            db_name = settings.FBS_CONFIG['database_naming_pattern'].format(solution_name=solution_name)
            
            # First, connect to PostgreSQL server to create database if it doesn't exist
            self.connection = psycopg2.connect(
                database='postgres',  # Connect to default postgres database
                user=db_config['user'],
                password=db_config['password'],
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', '5432')
            )
            
            # Check if database exists
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                db_exists = cursor.fetchone()
            
            self.connection.close()
            
            # Create database if it doesn't exist (outside any transaction)
            if not db_exists:
                # Create a new connection for database creation
                create_conn = psycopg2.connect(
                    database='postgres',
                    user=db_config['user'],
                    password=db_config['password'],
                    host=db_config.get('host', 'localhost'),
                    port=db_config.get('port', '5432')
                )
                create_conn.autocommit = True  # Enable autocommit for CREATE DATABASE
                
                with create_conn.cursor() as cursor:
                    cursor.execute(f'CREATE DATABASE "{db_name}"')
                    logger.info(f"Created database: {db_name}")
                
                create_conn.close()
            else:
                logger.info(f"Database {db_name} already exists")
            
            # Now connect to the target database and set up permissions
            self.connection = psycopg2.connect(
                database='postgres',
                user=db_config['user'],
                password=db_config['password'],
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', '5432')
            )
            
            with self.connection.cursor() as cursor:
                # Set up database permissions
                self._setup_database_permissions(cursor, db_name, db_config)
            
            self.connection.close()
            
            # Now connect to the newly created database
            self.connection = psycopg2.connect(
                database=db_name,
                user=db_config['user'],
                password=db_config['password'],
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', '5432')
            )
            
            with self.connection.cursor() as cursor:
                
                # 1. Setup schema permissions for solution user
                self._setup_schema_permissions(cursor, db_config['user'])
                
                # 2. Create FBS system tables (with prefix)
                fbs_tables = self._create_fbs_system_tables(cursor, table_prefix)
                
                # 3. Create business tables (with business prefix)
                business_tables = self._create_business_tables(cursor, business_prefix, solution_config.get('domain', ''))
                
                # 4. Create indexes and constraints
                self._create_indexes_and_constraints(cursor, table_prefix, business_prefix)
                
                # 5. Register solution in FBS metadata
                self._register_solution_schema(solution_config, fbs_tables, business_tables)
                
            self.connection.commit()
            
            return {
                'status': 'success',
                'database': db_name,
                'solution_name': solution_name,
                'fbs_tables_created': fbs_tables,
                'business_tables_created': business_tables,
                'total_tables': len(fbs_tables) + len(business_tables),
                'message': f'Solution schema created successfully in {db_name}'
            }
            
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"Error creating solution schema: {str(e)}")
            raise e
        finally:
            if self.connection:
                self.connection.close()
    
    def _create_fbs_system_tables(self, cursor, prefix: str) -> List[str]:
        """Create FBS system tables with prefix"""
        
        tables_created = []
        
        # FBS Discoveries table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}discoveries (
                id SERIAL PRIMARY KEY,
                discovery_type VARCHAR(50) NOT NULL,
                domain VARCHAR(100) NOT NULL,
                name VARCHAR(100) NOT NULL,
                version VARCHAR(20) DEFAULT '1.0',
                metadata JSONB DEFAULT '{{}}',
                schema_definition JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                discovered_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(discovery_type, domain, name, version)
            );
        """)
        tables_created.append(f'{prefix}discoveries')
        
        # FBS Solution Schemas table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}solution_schemas (
                id SERIAL PRIMARY KEY,
                solution_name VARCHAR(100) UNIQUE NOT NULL,
                domain VARCHAR(100) NOT NULL,
                database_name VARCHAR(100) NOT NULL,
                database_user VARCHAR(100) NOT NULL,
                database_password VARCHAR(255) NOT NULL,
                table_prefix VARCHAR(20) DEFAULT 'fbs_',
                business_prefix VARCHAR(20) DEFAULT '',
                schema_definition JSONB DEFAULT '{{}}',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}solution_schemas')
        
        # FBS Schema Migrations table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}schema_migrations (
                id SERIAL PRIMARY KEY,
                solution_name VARCHAR(100) NOT NULL,
                migration_type VARCHAR(50) NOT NULL,
                table_name VARCHAR(100) NOT NULL,
                sql_statement TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                executed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}schema_migrations')
        
        # FBS Workflow Definitions table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}workflow_definitions (
                id SERIAL PRIMARY KEY,
                workflow_name VARCHAR(100) UNIQUE NOT NULL,
                domain VARCHAR(100) NOT NULL,
                workflow_steps JSONB DEFAULT '{{}}',
                trigger_conditions JSONB DEFAULT '{{}}',
                approval_roles JSONB DEFAULT '{{}}',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}workflow_definitions')
        
        # FBS BI Dashboard Configurations table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}bi_dashboards (
                id SERIAL PRIMARY KEY,
                dashboard_name VARCHAR(100) UNIQUE NOT NULL,
                domain VARCHAR(100) NOT NULL,
                dashboard_config JSONB DEFAULT '{{}}',
                chart_definitions JSONB DEFAULT '{{}}',
                data_sources JSONB DEFAULT '{{}}',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}bi_dashboards')
        
        return tables_created
    
    def _create_business_tables(self, cursor, business_prefix: str, domain: str) -> List[str]:
        """Create business tables based on domain"""
        
        tables_created = []
        
        if domain == 'rental':
            tables_created.extend(self._create_rental_tables(cursor, business_prefix))
        elif domain == 'ecommerce':
            tables_created.extend(self._create_ecommerce_tables(cursor, business_prefix))
        elif domain == 'hr':
            tables_created.extend(self._create_hr_tables(cursor, business_prefix))
        else:
            # Generic business tables
            tables_created.extend(self._create_generic_tables(cursor, business_prefix))
        
        return tables_created
    
    def _create_rental_tables(self, cursor, prefix: str) -> List[str]:
        """Create rental business tables"""
        
        tables_created = []
        
        # Rental Property table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}property (
                id SERIAL PRIMARY KEY,
                property_name VARCHAR(255) NOT NULL,
                property_type VARCHAR(50),
                address TEXT,
                city VARCHAR(100),
                state VARCHAR(50),
                zip_code VARCHAR(20),
                rent_amount DECIMAL(10,2) NOT NULL,
                deposit_amount DECIMAL(10,2),
                square_feet INTEGER,
                bedrooms INTEGER,
                bathrooms INTEGER,
                is_available BOOLEAN DEFAULT TRUE,
                amenities JSONB DEFAULT '{{}}',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}property')
        
        # Rental Tenant table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}tenant (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                date_of_birth DATE,
                credit_score INTEGER,
                employment_status VARCHAR(50),
                employer_name VARCHAR(255),
                annual_income DECIMAL(12,2),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}tenant')
        
        # Rental Lease table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}lease (
                id SERIAL PRIMARY KEY,
                property_id INTEGER REFERENCES {prefix}property(id),
                tenant_id INTEGER REFERENCES {prefix}tenant(id),
                lease_start_date DATE NOT NULL,
                lease_end_date DATE NOT NULL,
                monthly_rent DECIMAL(10,2) NOT NULL,
                security_deposit DECIMAL(10,2),
                lease_status VARCHAR(20) DEFAULT 'active',
                lease_terms JSONB DEFAULT '{{}}',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}lease')
        
        # Rental Payment table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}payment (
                id SERIAL PRIMARY KEY,
                lease_id INTEGER REFERENCES {prefix}lease(id),
                tenant_id INTEGER REFERENCES {prefix}tenant(id),
                payment_date DATE NOT NULL,
                payment_amount DECIMAL(10,2) NOT NULL,
                payment_type VARCHAR(50),
                payment_status VARCHAR(20) DEFAULT 'pending',
                transaction_id VARCHAR(255),
                notes TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}payment')
        
        # Rental Maintenance table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}maintenance (
                id SERIAL PRIMARY KEY,
                property_id INTEGER REFERENCES {prefix}property(id),
                tenant_id INTEGER REFERENCES {prefix}tenant(id),
                issue_type VARCHAR(100),
                description TEXT,
                priority VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(20) DEFAULT 'open',
                assigned_to VARCHAR(255),
                estimated_cost DECIMAL(10,2),
                actual_cost DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}maintenance')
        
        return tables_created
    
    def _create_ecommerce_tables(self, cursor, prefix: str) -> List[str]:
        """Create ecommerce business tables"""
        
        tables_created = []
        
        # Product table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}product (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(100),
                sku VARCHAR(100) UNIQUE,
                stock_quantity INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}product')
        
        # Customer table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}customer (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                address TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}customer')
        
        # Order table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}order (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES {prefix}customer(id),
                order_date TIMESTAMP DEFAULT NOW(),
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                shipping_address TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}order')
        
        return tables_created
    
    def _create_hr_tables(self, cursor, prefix: str) -> List[str]:
        """Create HR business tables"""
        
        tables_created = []
        
        # Employee table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}employee (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                department VARCHAR(100),
                position VARCHAR(100),
                hire_date DATE,
                salary DECIMAL(10,2),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}employee')
        
        # Department table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}department (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                manager_id INTEGER REFERENCES {prefix}employee(id),
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}department')
        
        return tables_created
    
    def _create_generic_tables(self, cursor, prefix: str) -> List[str]:
        """Create generic business tables"""
        
        tables_created = []
        
        # Generic Entity table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}entity (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(100),
                attributes JSONB DEFAULT '{{}}',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}entity')
        
        # Generic Transaction table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {prefix}transaction (
                id SERIAL PRIMARY KEY,
                entity_id INTEGER REFERENCES {prefix}entity(id),
                transaction_type VARCHAR(100),
                amount DECIMAL(10,2),
                description TEXT,
                transaction_date TIMESTAMP DEFAULT NOW(),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append(f'{prefix}transaction')
        
        return tables_created
    
    def _create_indexes_and_constraints(self, cursor, fbs_prefix: str, business_prefix: str):
        """Create indexes and constraints for better performance"""
        
        # Indexes for FBS tables
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{fbs_prefix}discoveries_domain 
            ON {fbs_prefix}discoveries(domain);
        """)
        
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{fbs_prefix}discoveries_type 
            ON {fbs_prefix}discoveries(discovery_type);
        """)
        
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{fbs_prefix}solution_schemas_name 
            ON {fbs_prefix}solution_schemas(solution_name);
        """)
        
        # Indexes for business tables (if rental domain)
        if business_prefix == 'rental_':
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{business_prefix}property_available 
                ON {business_prefix}property(is_available);
            """)
            
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{business_prefix}lease_status 
                ON {business_prefix}lease(lease_status);
            """)
            
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{business_prefix}payment_status 
                ON {business_prefix}payment(payment_status);
            """)
    
    def _register_solution_schema(self, solution_config: dict, fbs_tables: List[str], business_tables: List[str]):
        """Register solution schema in Django model"""
        
        # Generate the actual database name that was created
        solution_name = solution_config.get('solution_name', 'testing')
        db_name = settings.FBS_CONFIG['database_naming_pattern'].format(solution_name=solution_name)
        
        schema_definition = {
            'fbs_tables': fbs_tables,
            'business_tables': business_tables,
            'total_tables': len(fbs_tables) + len(business_tables),
            'table_prefix': solution_config.get('table_prefix', 'fbs_'),
            'business_prefix': solution_config.get('business_prefix', '')
        }
        
        FBSSolutionSchema.objects.update_or_create(
            solution_name=solution_config['solution_name'],
            defaults={
                'domain': solution_config['domain'],
                'database_name': db_name,  # Use the generated database name
                'database_user': solution_config['database_config']['user'],
                'database_password': solution_config['database_config']['password'],
                'table_prefix': solution_config.get('table_prefix', 'fbs_'),
                'business_prefix': solution_config.get('business_prefix', ''),
                'schema_definition': schema_definition,
                'is_active': True
            }
        )
    
    def get_solution_status(self, solution_name: str) -> Dict[str, Any]:
        """Get status of a solution including database and table information"""
        
        try:
            solution = FBSSolutionSchema.objects.get(solution_name=solution_name)
            
            # Connect to the solution's database to get real-time status
            connection = psycopg2.connect(
                database=solution.database_name,
                user=solution.database_user,
                password=solution.database_password,
                host='localhost',
                port='5432'
            )
            
            with connection.cursor() as cursor:
                # Get database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size;
                """)
                db_size = cursor.fetchone()[0]
                
                # Get table count
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
                table_count = cursor.fetchone()[0]
                
                # Get FBS tables
                cursor.execute(f"""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE '{solution.table_prefix}%';
                """)
                fbs_tables = [row[0] for row in cursor.fetchall()]
                
                # Get business tables
                cursor.execute(f"""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE '{solution.business_prefix}%';
                """)
                business_tables = [row[0] for row in cursor.fetchall()]
            
            connection.close()
            
            return {
                'status': 'active' if solution.is_active else 'inactive',
                'database': solution.database_name,
                'tables': {
                    'fbs_system_tables': fbs_tables,
                    'business_tables': business_tables
                },
                'total_tables': table_count,
                'database_size': db_size,
                'table_prefix': solution.table_prefix,
                'business_prefix': solution.business_prefix,
                'created_at': solution.created_at.isoformat(),
                'updated_at': solution.updated_at.isoformat()
            }
            
        except FBSSolutionSchema.DoesNotExist:
            return {'status': 'not_found', 'message': f'Solution {solution_name} not found'}
        except Exception as e:
            logger.error(f"Error getting solution status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _setup_database_permissions(self, cursor, db_name: str, db_config: dict):
        """Setup database permissions for solution user"""
        try:
            solution_user = db_config['user']
            
            # Grant necessary permissions to existing user
            cursor.execute(f'GRANT CONNECT ON DATABASE "{db_name}" TO "{solution_user}"')
            cursor.execute(f'GRANT CREATE ON DATABASE "{db_name}" TO "{solution_user}"')
            cursor.execute(f'GRANT TEMPORARY ON DATABASE "{db_name}" TO "{solution_user}"')
            
            logger.info(f"Granted permissions to {solution_user} on {db_name}")
            
        except Exception as e:
            logger.error(f"Error setting up database permissions: {str(e)}")
            raise e
    
    def _setup_schema_permissions(self, cursor, solution_user: str):
        """Setup schema-level permissions for solution user"""
        try:
            # Grant usage on public schema
            cursor.execute(f'GRANT USAGE ON SCHEMA public TO "{solution_user}"')
            
            # Grant permissions on all existing tables
            cursor.execute(f"""
                GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{solution_user}"
            """)
            
            # Grant permissions on all sequences
            cursor.execute(f"""
                GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "{solution_user}"
            """)
            
            # Set default permissions for future tables
            cursor.execute(f"""
                ALTER DEFAULT PRIVILEGES IN SCHEMA public 
                GRANT ALL PRIVILEGES ON TABLES TO "{solution_user}"
            """)
            
            # Set default permissions for future sequences
            cursor.execute(f"""
                ALTER DEFAULT PRIVILEGES IN SCHEMA public 
                GRANT ALL PRIVILEGES ON SEQUENCES TO "{solution_user}"
            """)
            
            logger.info(f"Granted schema permissions to {solution_user}")
            
        except Exception as e:
            logger.error(f"Error setting up schema permissions: {str(e)}")
            raise e
    
    def list_solutions(self) -> List[Dict[str, Any]]:
        """List all solutions with their status"""
        
        solutions = []
        for solution in FBSSolutionSchema.objects.filter(is_active=True):
            status = self.get_solution_status(solution.solution_name)
            solutions.append({
                'solution_name': solution.solution_name,
                'domain': solution.domain,
                'database': solution.database_name,
                'status': status.get('status', 'unknown'),
                'total_tables': status.get('total_tables', 0),
                'created_at': solution.created_at.isoformat()
            })
        
        return solutions 