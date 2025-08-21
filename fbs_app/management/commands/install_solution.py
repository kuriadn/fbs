"""
Django management command for installing and setting up new solutions.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json
import logging

logger = logging.getLogger('fbs_app')


class Command(BaseCommand):
    help = 'Install and setup new solutions with Odoo integration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'solution_name',
            type=str,
            help='Name of the solution to install'
        )
        parser.add_argument(
            '--odoo-url',
            type=str,
            help='Odoo server URL'
        )
        parser.add_argument(
            '--odoo-database',
            type=str,
            help='Odoo database name'
        )
        parser.add_argument(
            '--odoo-username',
            type=str,
            help='Odoo username'
        )
        parser.add_argument(
            '--odoo-password',
            type=str,
            help='Odoo password'
        )
        parser.add_argument(
            '--modules',
            type=str,
            help='Comma-separated list of Odoo modules to install'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            help='Admin user email'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            help='Admin user password'
        )
        parser.add_argument(
            '--config-file',
            type=str,
            help='Configuration file path'
        )
        parser.add_argument(
            '--skip-odoo-setup',
            action='store_true',
            help='Skip Odoo database setup'
        )
        parser.add_argument(
            '--skip-django-setup',
            action='store_true',
            help='Skip Django database setup'
        )
    
    def handle(self, *args, **options):
        try:
            solution_name = options['solution_name']
            odoo_url = options.get('odoo_url')
            odoo_database = options.get('odoo_database')
            odoo_username = options.get('odoo_username')
            odoo_password = options.get('odoo_password')
            modules_str = options.get('modules')
            admin_email = options.get('admin_email')
            admin_password = options.get('admin_password')
            config_file = options.get('config_file')
            skip_odoo_setup = options.get('skip_odoo_setup')
            skip_django_setup = options.get('skip_django_setup')
            
            # Load configuration from file if provided
            if config_file:
                config = self._load_config_file(config_file)
                odoo_url = odoo_url or config.get('odoo_url')
                odoo_database = odoo_database or config.get('odoo_database')
                odoo_username = odoo_username or config.get('odoo_username')
                odoo_password = odoo_password or config.get('odoo_password')
                modules_str = modules_str or config.get('modules')
                admin_email = admin_email or config.get('admin_email')
                admin_password = admin_password or config.get('admin_password')
            
            # Validate required parameters
            if not skip_odoo_setup and not all([odoo_url, odoo_database, odoo_username, odoo_password]):
                raise CommandError('Odoo URL, database, username, and password are required when not skipping Odoo setup')
            
            if not admin_email:
                admin_email = f'admin@{solution_name}.com'
            
            if not admin_password:
                # Generate a secure random password instead of hardcoded one
                import secrets
                import string
                admin_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
                self.stdout.write(
                    self.style.WARNING(
                        f'Generated secure admin password: {admin_password}\n'
                        'Please save this password securely!'
                    )
                )
            
            # Parse modules
            modules = []
            if modules_str:
                modules = [module.strip() for module in modules_str.split(',')]
            
            self.stdout.write(f"Installing solution: {solution_name}")
            
            # Import services
            from fbs_app.services import OnboardingService, DatabaseService
            
            onboarding_service = OnboardingService()
            database_service = DatabaseService(solution_name)
            
            # Step 1: Create databases
            if not skip_django_setup:
                self.stdout.write("Creating Django database...")
                django_result = database_service.create_database('django', solution_name)
                if not django_result['success']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Django database creation warning: {django_result.get('error')}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Django database created: {django_result['database_name']}"
                        )
                    )
            
            if not skip_odoo_setup:
                self.stdout.write("Creating Odoo database...")
                odoo_result = database_service.create_database('fbs', solution_name)
                if not odoo_result['success']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Odoo database creation warning: {odoo_result.get('error')}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Odoo database created: {odoo_result['database_name']}"
                        )
                    )
            
            # Step 2: Setup Odoo if not skipped
            if not skip_odoo_setup:
                self.stdout.write("Setting up Odoo...")
                
                # Test Odoo connection
                from fbs_app.services import OdooClient
                odoo_client = OdooClient()
                
                # Authenticate with Odoo
                auth_result = odoo_client.authenticate(
                    url=odoo_url,
                    database=odoo_database,
                    username=odoo_username,
                    password=odoo_password
                )
                
                if not auth_result['success']:
                    raise CommandError(f"Odoo authentication failed: {auth_result.get('error')}")
                
                token = auth_result['token']
                self.stdout.write("Odoo authentication successful")
                
                # Install base modules
                if modules:
                    self.stdout.write(f"Installing modules: {', '.join(modules)}")
                    
                    for module in modules:
                        install_result = onboarding_service.install_odoo_module(
                            module_name=module,
                            token=token,
                            database=odoo_database
                        )
                        
                        if install_result['success']:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Module {module} installed successfully"
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Module {module} installation warning: {install_result.get('error')}"
                                )
                            )
                
                # Create admin user
                self.stdout.write("Creating admin user...")
                admin_result = onboarding_service.create_odoo_admin_user(
                    admin_email=admin_email,
                    admin_password=admin_password,
                    token=token,
                    database=odoo_database
                )
                
                if admin_result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Admin user created: {admin_email}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Admin user creation warning: {admin_result.get('error')}"
                        )
                    )
            
            # Step 3: Setup Django solution
            if not skip_django_setup:
                self.stdout.write("Setting up Django solution...")
                
                # Create solution setup wizard
                setup_result = onboarding_service.create_solution_setup(
                    solution_name=solution_name,
                    admin_email=admin_email,
                    admin_password=admin_password
                )
                
                if setup_result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Solution setup created: {setup_result['setup_id']}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Solution setup warning: {setup_result.get('error')}"
                        )
                    )
            
            # Step 4: Generate solution summary
            self.stdout.write("Generating solution summary...")
            
            summary = {
                'solution_name': solution_name,
                'databases': database_service.get_database_names(solution_name),
                'admin_email': admin_email,
                'odoo_setup': not skip_odoo_setup,
                'django_setup': not skip_django_setup,
                'modules_installed': modules if not skip_odoo_setup else []
            }
            
            # Display summary
            self.stdout.write("\n" + "="*50)
            self.stdout.write("SOLUTION INSTALLATION SUMMARY")
            self.stdout.write("="*50)
            self.stdout.write(f"Solution Name: {summary['solution_name']}")
            self.stdout.write(f"Admin Email: {summary['admin_email']}")
            self.stdout.write(f"Odoo Setup: {'Yes' if summary['odoo_setup'] else 'No'}")
            self.stdout.write(f"Django Setup: {'Yes' if summary['django_setup'] else 'No'}")
            
            if summary['odoo_setup']:
                self.stdout.write(f"Odoo URL: {odoo_url}")
                self.stdout.write(f"Odoo Database: {odoo_database}")
                self.stdout.write(f"Modules Installed: {', '.join(summary['modules_installed']) if summary['modules_installed'] else 'None'}")
            
            self.stdout.write("\nDatabases:")
            for db_type, db_name in summary['databases'].items():
                self.stdout.write(f"  {db_type}: {db_name}")
            
            self.stdout.write("="*50)
            
            # Save summary to file
            summary_file = f"{solution_name}_installation_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.stdout.write(f"Installation summary saved to: {summary_file}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Solution '{solution_name}' installed successfully!"
                )
            )
            
        except Exception as e:
            logger.error(f"Error in install_solution command: {str(e)}")
            raise CommandError(f"Solution installation failed: {str(e)}")
    
    def _load_config_file(self, config_file):
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise CommandError(f"Failed to load config file: {str(e)}")
