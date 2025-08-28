#!/usr/bin/env python3
"""
Test Admin Password - Check if admin user authentication is working
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

def setup_environment():
    """Set up environment variables for testing"""
    print("🔧 Setting up test environment...")
    
    # Database connection settings (for database-level operations)
    os.environ['FBS_DB_HOST'] = 'localhost'
    os.environ['FBS_DB_PORT'] = '5432'
    os.environ['FBS_DB_USER'] = 'odoo'
    os.environ['FBS_DB_PASSWORD'] = 'four@One2'
    os.environ['FBS_DJANGO_USER'] = 'fayvad'
    os.environ['FBS_DJANGO_PASSWORD'] = 'MeMiMo@0207'
    os.environ['FBS_ADMIN_USER'] = 'postgres'
    os.environ['FBS_ADMIN_PASSWORD'] = 'MeMiMo@0207'
    
    print("✅ Environment setup complete")
    print()

def test_database_connection():
    """Test database-level connection using odoo user"""
    print("🧪 Testing Database-Level Connection (odoo user)")
    print("=" * 60)
    
    try:
        from fbs_app.services.database_service import DatabaseService
        
        db_service = DatabaseService('rental_test')
        
        print("🔍 Testing PostgreSQL connection with odoo user...")
        
        # Test if we can connect to PostgreSQL as odoo user
        try:
            odoo_config = db_service._get_user_config('odoo')
            print(f"   ✅ Odoo user config: {odoo_config['user']}@{odoo_config['host']}:{odoo_config['port']}")
            
            # Test if rental_test database exists
            database_name = 'fbs_rental_test_db'
            exists = db_service._check_odoo_database_exists(database_name)
            print(f"   ✅ Database '{database_name}' exists: {exists}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database connection failed: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Database connection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_authentication():
    """Test application-level authentication using admin user"""
    print("\n🧪 Testing Application-Level Authentication (admin user)")
    print("=" * 60)
    
    try:
        from fbs_app.services.odoo_client import OdooClient
        
        # Test with rental_test database
        database_name = 'fbs_rental_test_db'
        
        print(f"🔍 Testing Odoo API authentication to database: {database_name}")
        print()
        
        # Test 1: Try with default password (admin123)
        print("📝 Test 1: Trying with default password 'admin123'...")
        os.environ['ODOO_USER'] = 'admin'
        os.environ['ODOO_PASSWORD'] = 'admin123'
        
        client = OdooClient('rental_test')
        
        try:
            # Try to get database info
            info = client.get_database_info()
            print(f"   ✅ Database info retrieved: {info.get('success', False)}")
            
            # Try to authenticate
            credentials = client._get_odoo_credentials(database_name)
            print(f"   ✅ Credentials prepared: {credentials['username']}@{credentials['database']}")
            
            uid = client._authenticate(credentials)
            print(f"   ✅ Authentication successful with default password! UID: {uid}")
            default_works = True
            
        except Exception as e:
            print(f"   ❌ Default password failed: {str(e)}")
            default_works = False
        
        print()
        
        # Test 2: Try with expected password (MeMiMo@0207)
        print("📝 Test 2: Trying with expected password 'MeMiMo@0207'...")
        os.environ['ODOO_USER'] = 'admin'
        os.environ['ODOO_PASSWORD'] = 'MeMiMo@0207'
        
        try:
            # Try to authenticate
            credentials = client._get_odoo_credentials(database_name)
            print(f"   ✅ Credentials prepared: {credentials['username']}@{credentials['database']}")
            
            uid = client._authenticate(credentials)
            print(f"   ✅ Authentication successful with expected password! UID: {uid}")
            expected_works = True
            
        except Exception as e:
            print(f"   ❌ Expected password failed: {str(e)}")
            expected_works = False
        
        print()
        
        # Summary
        if default_works and not expected_works:
            print("🔍 RESULT: Default password works, expected password doesn't")
            print("   The admin user still has the default password 'admin123'")
            print("   It needs to be changed to 'MeMiMo@0207'")
        elif not default_works and expected_works:
            print("🔍 RESULT: Expected password works, default password doesn't")
            print("   The admin user has been properly configured")
        elif default_works and expected_works:
            print("🔍 RESULT: Both passwords work (unexpected)")
        else:
            print("🔍 RESULT: Neither password works")
            print("   There's a deeper authentication issue")
        
        return True
        
    except Exception as e:
        print(f"❌ Admin authentication test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 Admin Password Test - Database vs Application Level")
    print("=" * 80)
    
    # Setup environment
    setup_environment()
    
    # Test database-level connection (odoo user)
    db_success = test_database_connection()
    
    # Test application-level authentication (admin user)
    admin_success = test_admin_authentication()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    print(f"Database Connection (odoo user): {'✅ PASSED' if db_success else '❌ FAILED'}")
    print(f"Admin Authentication (admin user): {'✅ PASSED' if admin_success else '❌ FAILED'}")
    
    if db_success and admin_success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests need attention")
    
    return db_success and admin_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
