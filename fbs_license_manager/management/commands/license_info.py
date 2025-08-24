"""
Django management command to display FBS license information
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from fbs_license_manager import LicenseManager, FeatureFlags
import json


class Command(BaseCommand):
    help = 'Display FBS license information and feature status'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--solution',
            type=str,
            default='default',
            help='Solution name to check license for'
        )
        parser.add_argument(
            '--license-key',
            type=str,
            help='License key to validate'
        )
        parser.add_argument(
            '--format',
            choices=['text', 'json'],
            default='text',
            help='Output format'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information'
        )
    
    def handle(self, *args, **options):
        solution_name = options['solution']
        license_key = options['license_key']
        output_format = options['format']
        detailed = options['detailed']
        
        try:
            # Initialize license manager
            license_manager = LicenseManager(solution_name, license_key)
            feature_flags = FeatureFlags(solution_name, license_manager)
            
            # Get license information
            license_info = license_manager.get_license_info()
            feature_matrix = feature_flags.get_feature_matrix()
            
            if output_format == 'json':
                self._output_json(license_info, feature_matrix, detailed, license_manager)
            else:
                self._output_text(license_info, feature_matrix, detailed, license_manager)
                
        except Exception as e:
            raise CommandError(f"Failed to get license info: {e}")
    
    def _output_json(self, license_info, feature_matrix, detailed, license_manager):
        """Output license information in JSON format"""
        output = {
            'license_info': license_info,
            'feature_matrix': feature_matrix
        }
        
        if detailed:
            # Create upgrade prompts with the license manager
            from fbs_license_manager import UpgradePrompts
            upgrade_prompts = UpgradePrompts(license_manager)
            output['upgrade_analysis'] = upgrade_prompts.get_comprehensive_upgrade_analysis()
        
        self.stdout.write(json.dumps(output, indent=2))
    
    def _output_text(self, license_info, feature_matrix, detailed, license_manager):
        """Output license information in text format"""
        self.stdout.write(self.style.SUCCESS(f"\n🔐 FBS License Information for '{license_info['solution_name']}'\n"))
        
        # License details
        self.stdout.write(f"License Type: {license_info['license_type'].upper()}")
        self.stdout.write(f"Status: {license_info['status']}")
        self.stdout.write(f"Source: {license_info['source']}")
        
        if license_info.get('expiry_date'):
            self.stdout.write(f"Expiry Date: {license_info['expiry_date']}")
        
        if license_info.get('trial_days_remaining') is not None:
            self.stdout.write(f"Trial Days Remaining: {license_info['trial_days_remaining']}")
        
        # Features
        self.stdout.write(f"\n📋 Available Features ({len(license_info['features'])}):")
        for feature in license_info['features']:
            self.stdout.write(f"  ✅ {feature}")
        
        # Limits
        if license_info.get('limits'):
            self.stdout.write(f"\n📊 Usage Limits:")
            for limit_name, limit_value in license_info['limits'].items():
                if limit_value == -1:
                    self.stdout.write(f"  {limit_name}: Unlimited")
                else:
                    self.stdout.write(f"  {limit_name}: {limit_value}")
        
        # Feature matrix
        self.stdout.write(f"\n🎯 Feature Matrix:")
        for feature, config in feature_matrix.items():
            status = "✅ Enabled" if config['enabled'] else "❌ Disabled"
            self.stdout.write(f"  {feature}: {status}")
            
            if detailed and config['dependencies']:
                deps = ", ".join(config['dependencies'])
                self.stdout.write(f"    Dependencies: {deps}")
        
        # Upgrade information
        if license_info.get('upgrade_available'):
            self.stdout.write(f"\n🚀 Upgrade Available!")
            if detailed:
                # Create upgrade prompts with the license manager
                from fbs_license_manager import UpgradePrompts
                upgrade_prompts = UpgradePrompts(license_manager)
                upgrade_analysis = upgrade_prompts.get_comprehensive_upgrade_analysis()
                
                for option in upgrade_analysis.get('upgrade_options', []):
                    self.stdout.write(f"  {option['tier'].upper()}: ${option['pricing']['monthly']}/month")
                    self.stdout.write(f"    New features: {len(option['new_features'])}")
        
        self.stdout.write("\n" + "="*50 + "\n")
    
    def _get_license_manager_from_info(self, license_info):
        """Extract license manager from license info"""
        # This is a workaround since license_info doesn't contain the manager
        # In practice, you'd need to pass the manager separately
        return None
