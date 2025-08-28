#!/usr/bin/env python3
"""
Test script for Odoo database creation using odoo-bin
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

def test_odoo_database_creation():
    """Test Odoo database creation"""
    try:
        # Set environment variables for testing
        os.environ['FBS_DB_HOST'] = 'localhost'
        os.environ['FBS_DB_PORT'] = '5432'
        os.environ['FBS_DB_USER'] = 'odoo'
        os.environ['FBS_DB_PASSWORD'] = 'four@One2'
        
        print("🧪 Testing Odoo database creation...")
        
        # Import the database service
        from fbs_app.services.database_service import DatabaseService
        
        # Create database service
        db_service = DatabaseService('test_solution')
        
        print("✅ DatabaseService initialized successfully")
        
        # Test Odoo database creation
        print("📊 Creating Odoo database for 'test_solution_2'...")
        result = db_service.create_odoo_database('test_solution_2', ['base', 'web'])
        
        if result['success']:
            print(f"✅ Odoo database created successfully: {result['database_name']}")
            print(f"📦 Modules installed: {result['modules_installed']}")
            print(f"💬 Message: {result['message']}")
        else:
            print(f"❌ Odoo database creation failed: {result['error']}")
            if 'stdout' in result:
                print(f"📤 STDOUT: {result['stdout']}")
            if 'stderr' in result:
                print(f"📥 STDERR: {result['stderr']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_odoo_database_creation()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)
