"""
Management command for FBS license operations

Usage:
    python manage.py manage_license <action> [options]

Actions:
    - create: Create a new license for a solution
    - update: Update existing license
    - delete: Delete a license
    - status: Show license status
    - sync: Sync license data between Django and Odoo
    - usage: Show feature usage
"""

import json
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from fbs_license_manager import LicenseManager, FeatureFlags


class Command(BaseCommand):
    help = 'Manage FBS licenses for solutions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['create', 'update', 'delete', 'status', 'sync', 'usage'],
            help='Action to perform'
        )
        
        parser.add_argument(
            '--solution',
            required=True,
            help='Solution name'
        )
        
        parser.add_argument(
            '--type',
            choices=['trial', 'basic', 'professional', 'enterprise'],
            help='License type'
        )
        
        parser.add_argument(
            '--features',
            help='Comma-separated list of features'
        )
        
        parser.add_argument(
            '--limits',
            help='JSON string of feature limits'
        )
        
        parser.add_argument(
            '--expiry',
            help='Expiry date (YYYY-MM-DD)'
        )
        
        parser.add_argument(
            '--key',
            help='License key'
        )
        
        parser.add_argument(
            '--source',
            choices=['embedded', 'external', 'file', 'environment'],
            default='embedded',
            help='License source'
        )
        
        parser.add_argument(
            '--format',
            choices=['text', 'json'],
            default='text',
            help='Output format'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        solution_name = options['solution']
        
        try:
            if action == 'create':
                self.create_license(solution_name, options)
            elif action == 'update':
                self.update_license(solution_name, options)
            elif action == 'delete':
                self.delete_license(solution_name)
            elif action == 'status':
                self.show_status(solution_name, options)
            elif action == 'sync':
                self.sync_license(solution_name)
            elif action == 'usage':
                self.show_usage(solution_name, options)
        except Exception as e:
            raise CommandError(f"Failed to {action} license: {e}")
    
    def create_license(self, solution_name, options):
        """Create a new license"""
        license_data = {
            'type': options.get('type', 'trial'),
            'license_key': options.get('key'),
            'expiry_date': options.get('expiry'),
            'features': self._parse_features(options.get('features')),
            'limits': self._parse_limits(options.get('limits')),
            'source': options.get('source', 'embedded')
        }
        
        # Initialize license manager
        license_manager = LicenseManager(solution_name, options.get('key'))
        
        # Save to storage
        if hasattr(license_manager, 'storage') and license_manager.storage:
            success = license_manager.storage.save_license_data(license_data)
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"License created for {solution_name}")
                )
            else:
                raise CommandError("Failed to save license data")
        else:
            raise CommandError("No storage available for license")
    
    def update_license(self, solution_name, options):
        """Update existing license"""
        # Get current license
        license_manager = LicenseManager(solution_name, options.get('key'))
        current_data = license_manager.get_license_info()
        
        # Update fields
        if options.get('type'):
            current_data['license_type'] = options['type']
        if options.get('features'):
            current_data['features'] = self._parse_features(options['features'])
        if options.get('limits'):
            current_data['limits'] = self._parse_limits(options['limits'])
        if options.get('expiry'):
            current_data['expiry_date'] = options['expiry']
        if options.get('source'):
            current_data['source'] = options['source']
        
        # Save updated data
        if hasattr(license_manager, 'storage') and license_manager.storage:
            success = license_manager.storage.save_license_data(current_data)
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"License updated for {solution_name}")
                )
            else:
                raise CommandError("Failed to update license data")
        else:
            raise CommandError("No storage available for license")
    
    def delete_license(self, solution_name):
        """Delete a license"""
        license_manager = LicenseManager(solution_name)
        
        if hasattr(license_manager, 'storage') and license_manager.storage:
            success = license_manager.storage.delete_license_data()
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"License deleted for {solution_name}")
                )
            else:
                raise CommandError("Failed to delete license data")
        else:
            raise CommandError("No storage available for license")
    
    def show_status(self, solution_name, options):
        """Show license status"""
        license_manager = LicenseManager(solution_name)
        license_info = license_manager.get_license_info()
        
        if options['format'] == 'json':
            self.stdout.write(json.dumps(license_info, indent=2))
        else:
            self._output_text_status(license_info)
    
    def sync_license(self, solution_name):
        """Sync license data between Django and Odoo"""
        license_manager = LicenseManager(solution_name)
        
        if hasattr(license_manager, 'storage') and license_manager.storage:
            success = license_manager.storage.refresh_cache()
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"License synced for {solution_name}")
                )
            else:
                raise CommandError("Failed to sync license data")
        else:
            raise CommandError("No storage available for license")
    
    def show_usage(self, solution_name, options):
        """Show feature usage"""
        license_manager = LicenseManager(solution_name)
        
        if hasattr(license_manager, 'storage') and license_manager.storage:
            usage_summary = license_manager.storage.get_usage_summary()
            
            if options['format'] == 'json':
                self.stdout.write(json.dumps(usage_summary, indent=2))
            else:
                self._output_text_usage(usage_summary, solution_name)
        else:
            raise CommandError("No storage available for license")
    
    def _parse_features(self, features_str):
        """Parse features string into list"""
        if not features_str:
            return []
        return [f.strip() for f in features_str.split(',') if f.strip()]
    
    def _parse_limits(self, limits_str):
        """Parse limits string into dict"""
        if not limits_str:
            return {}
        try:
            return json.loads(limits_str)
        except json.JSONDecodeError:
            raise CommandError("Invalid JSON format for limits")
    
    def _output_text_status(self, license_info):
        """Output license status in text format"""
        self.stdout.write(f"\nLicense Status for {license_info['solution_name']}")
        self.stdout.write("=" * 50)
        self.stdout.write(f"Type: {license_info['license_type']}")
        self.stdout.write(f"Status: {license_info['status']}")
        self.stdout.write(f"Source: {license_info['source']}")
        self.stdout.write(f"Storage: {license_info.get('storage_type', 'unknown')}")
        self.stdout.write(f"Odoo Available: {license_info.get('odoo_available', False)}")
        
        if license_info.get('expiry_date'):
            self.stdout.write(f"Expires: {license_info['expiry_date']}")
        
        if license_info.get('trial_days_remaining'):
            self.stdout.write(f"Trial Days Remaining: {license_info['trial_days_remaining']}")
        
        self.stdout.write(f"\nFeatures: {', '.join(license_info['features']) if license_info['features'] else 'None'}")
        
        if license_info.get('limits'):
            self.stdout.write("\nLimits:")
            for feature, limit in license_info['limits'].items():
                self.stdout.write(f"  {feature}: {limit}")
    
    def _output_text_usage(self, usage_summary, solution_name):
        """Output usage summary in text format"""
        self.stdout.write(f"\nFeature Usage for {solution_name}")
        self.stdout.write("=" * 40)
        
        if not usage_summary:
            self.stdout.write("No usage data available")
            return
        
        for feature, count in usage_summary.items():
            self.stdout.write(f"{feature}: {count}")
