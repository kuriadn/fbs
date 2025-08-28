#!/usr/bin/env python3
"""
Test script for Odoo module management capabilities
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_project.settings')

# Configure Django
django.setup()

def test_module_management():
    """Test Odoo module management capabilities"""
    try:
        # Set environment variables for testing
        os.environ['FBS_DB_HOST'] = 'localhost'
        os.environ['FBS_DB_PORT'] = '5432'
        os.environ['FBS_DB_USER'] = 'odoo'
        os.environ['FBS_DB_PASSWORD'] = 'four@One2'
        
        print("🧪 Testing Odoo module management capabilities...")
        
        # Import the FBS interface
        from fbs_app.interfaces import FBSInterface
        
        # Create FBS interface for a test solution
        fbs = FBSInterface('module_test_solution')
        
        print("✅ FBSInterface initialized successfully")
        
        # Test 1: Get available modules
        print("\n📋 Test 1: Getting available modules...")
        available_modules = fbs.odoo.get_available_modules()
        
        if available_modules['success']:
            print("✅ Available modules retrieved successfully")
            for category, modules in available_modules['available_modules'].items():
                print(f"   {category}: {', '.join(modules[:3])}{'...' if len(modules) > 3 else ''}")
        else:
            print(f"❌ Failed to get available modules: {available_modules['error']}")
        
        # Test 2: Create solution databases with specific modules
        print("\n📊 Test 2: Creating solution databases with specific modules...")
        
        # Define modules for a rental business solution
        core_modules = ['base', 'web', 'mail', 'contacts']
        additional_modules = ['sale', 'stock', 'account']
        
        print(f"   Core modules: {', '.join(core_modules)}")
        print(f"   Additional modules: {', '.join(additional_modules)}")
        
        result = fbs.odoo.create_solution_databases_with_modules(
            core_modules=core_modules,
            additional_modules=additional_modules
        )
        
        if result['success']:
            print("✅ Solution databases created with modules successfully")
            print(f"   Django DB: {result['django_db_name']}")
            print(f"   Odoo DB: {result['odoo_db_name']}")
            print(f"   Core modules installed: {', '.join(result['core_modules'])}")
            print(f"   Additional modules installed: {', '.join(result['additional_modules'])}")
        else:
            print(f"❌ Failed to create solution databases: {result.get('error', 'Unknown error')}")
            if 'results' in result:
                for db_type, db_result in result['results'].items():
                    if not db_result.get('success', False):
                        print(f"   {db_type}: {db_result.get('error', 'Unknown error')}")
        
        # Test 3: Install additional modules
        print("\n📦 Test 3: Installing additional modules...")
        
        new_modules = ['purchase', 'mrp']
        print(f"   Installing: {', '.join(new_modules)}")
        
        install_result = fbs.odoo.install_modules(new_modules)
        
        if install_result['success']:
            print("✅ Additional modules installed successfully")
            print(f"   Modules installed: {', '.join(install_result['modules_installed'])}")
        else:
            print(f"❌ Failed to install additional modules: {install_result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_module_management()
    if success:
        print("\n🎉 Module management test completed successfully!")
    else:
        print("\n💥 Module management test failed!")
        sys.exit(1)
