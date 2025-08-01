from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from fayvad_core.models import OdooDatabase, ApiTokenMapping
from fayvad_core.services import AuthService
from datetime import timedelta
import secrets


class Command(BaseCommand):
    help = 'Create API token mapping for a user and database'
    
    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username')
        parser.add_argument('database', type=str, help='Database name')
        parser.add_argument('--odoo-user-id', type=int, default=1, help='Odoo user ID')
        parser.add_argument('--expires-days', type=int, default=90, help='Token expiration in days')
        parser.add_argument('--generate-token', action='store_true', help='Generate a new token')
    
    def handle(self, *args, **options):
        try:
            # Get user
            user = User.objects.get(username=options['username'])
            self.stdout.write(f'Found user: {user.username}')
            
            # Get database
            database = OdooDatabase.objects.get(name=options['database'])
            self.stdout.write(f'Found database: {database.name}')
            
            # Generate or get token
            if options['generate_token']:
                odoo_token = secrets.token_urlsafe(32)
                self.stdout.write(f'Generated new token: {odoo_token}')
            else:
                # Check if mapping already exists
                try:
                    existing = ApiTokenMapping.objects.get(user=user, database=database)
                    odoo_token = existing.odoo_token
                    self.stdout.write(f'Using existing token: {odoo_token}')
                except ApiTokenMapping.DoesNotExist:
                    odoo_token = secrets.token_urlsafe(32)
                    self.stdout.write(f'Generated new token: {odoo_token}')
            
            # Calculate expiration
            expires_at = timezone.now() + timedelta(days=options['expires_days'])
            
            # Create or update token mapping
            token_mapping = AuthService.create_token_mapping(
                user=user,
                database_name=database.name,
                odoo_token=odoo_token,
                odoo_user_id=options['odoo_user_id'],
                expires_at=expires_at
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created token mapping:\n'
                    f'  User: {user.username}\n'
                    f'  Database: {database.name}\n'
                    f'  Token: {odoo_token}\n'
                    f'  Expires: {expires_at.strftime("%Y-%m-%d %H:%M:%S")}\n'
                )
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{options["username"]}" does not exist')
            )
        except OdooDatabase.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Database "{options["database"]}" does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating token mapping: {str(e)}')
            )
