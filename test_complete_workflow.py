#!/usr/bin/env python3
"""
Test Complete Workflow - All modules installed in one step
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
    
    # Database connection settings
    os.environ['FBS_DB_HOST'] = 'localhost'
    os.environ['FBS_DB_PORT'] = '5432'
    os.environ['FBS_DB_USER'] = 'odoo'
    os.environ['FBS_DB_PASSWORD'] = 'four@One2'
    os.environ['FBS_DJANGO_USER'] = 'fayvad'
    os.environ['FBS_DJANGO_PASSWORD'] = 'MeMiMo@0207'
    os.environ['FBS_ADMIN_USER'] = 'postgres'
    os.environ['FBS_ADMIN_PASSWORD'] = 'MeMiMo@0207'
    
    # Odoo authentication settings
    os.environ['ODOO_USER'] = 'admin'
    os.environ['ODOO_PASSWORD'] = 'MeMiMo@0207'
    
    print("✅ Environment setup complete")
    print()

def test_complete_database_creation():
    """Test complete database creation with all modules in one step"""
    print("🧪 Testing Complete Database Creation")
    print("=" * 60)
    
    try:
        from fbs_app.interfaces import FBSInterface
        
        # Initialize FBS for rental_test solution
        fbs = FBSInterface('rental_test')
        print(f"✅ FBS initialized for solution: 'rental_test'")
        
        # Show expected database names
        print("📊 Expected database names:")
        print(f"   Django DB: {fbs.django_db_name}")
        print(f"   Odoo DB: {fbs.odoo_db_name}")
        print()
        
        # Define ALL modules for rental business (installed in one step)
        core_modules = ['base', 'web', 'mail', 'contacts']
        rental_modules = ['sale', 'stock', 'account', 'project', 'purchase', 'mrp']
        
        print("🔧 Creating solution databases with ALL modules in one step...")
        print(f"   Core modules: {', '.join(core_modules)}")
        print(f"   Rental modules: {', '.join(rental_modules)}")
        print(f"   Total modules: {len(core_modules) + len(rental_modules)}")
        print()
        
        result = fbs.odoo.create_solution_databases_with_modules(
            core_modules=core_modules,
            additional_modules=rental_modules
        )
        
        if result['success']:
            print("✅ Solution databases are ready!")
            print(f"   Django DB: {result['django_db_name']}")
            print(f"   Odoo DB: {result['odoo_db_name']}")
            print(f"   All modules installed: {', '.join(result['all_modules_installed'])}")
            print(f"   Password changed: {result.get('password_changed', 'Unknown')}")
            
            # Show if databases already existed
            if result.get('django_exists') or result.get('odoo_exists'):
                print("   ℹ️  Some databases already existed (this is fine)")
            
            return True
        else:
            print(f"❌ Database creation failed: {result.get('error', 'Unknown error')}")
            if 'results' in result:
                for db_type, db_result in result['results'].items():
                    if not db_result.get('success', False):
                        error_msg = db_result.get('error', 'Unknown error')
                        if 'already exists' in error_msg:
                            print(f"   ✅ {db_type}: Database already exists (this is fine)")
                        else:
                            print(f"   ❌ {db_type}: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Database creation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_odoo_authentication():
    """Test Odoo authentication after database creation"""
    print("\n🧪 Testing Odoo Authentication")
    print("=" * 60)
    
    try:
        from fbs_app.services.odoo_client import OdooClient
        
        # Test with rental_test database
        database_name = 'fbs_rental_test_db'
        
        print(f"🔍 Testing Odoo API authentication to database: {database_name}")
        print()
        
        # Test with expected password (MeMiMo@0207)
        print("📝 Testing with expected password 'MeMiMo@0207'...")
        os.environ['ODOO_USER'] = 'admin'
        os.environ['ODOO_PASSWORD'] = 'MeMiMo@0207'
        
        client = OdooClient('rental_test')
        
        try:
            # Try to get database info
            info = client.get_database_info()
            print(f"   ✅ Database info retrieved: {info.get('success', False)}")
            
            # Try to authenticate
            credentials = client._get_odoo_credentials(database_name)
            print(f"   ✅ Credentials prepared: {credentials['username']}@{credentials['database']}")
            
            uid = client._authenticate(credentials)
            print(f"   ✅ Authentication successful! UID: {uid}")
            return True
            
        except Exception as e:
            print(f"   ❌ Authentication failed: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Odoo authentication test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_odoo_operations():
    """Test basic Odoo operations after successful authentication"""
    print("\n🧪 Testing Basic Odoo Operations")
    print("=" * 60)
    
    try:
        from fbs_app.interfaces import FBSInterface
        
        fbs = FBSInterface('rental_test')
        print(f"✅ FBS initialized for solution: 'rental_test'")
        
        # Test model discovery
        print("🔍 Testing Odoo model discovery...")
        models_result = fbs.odoo.discover_models()
        
        if models_result['success']:
            print("✅ Models discovered successfully")
            
            # Handle the data structure properly
            models_data = models_result['data']
            if isinstance(models_data, dict) and 'models' in models_data:
                models = models_data['models']
            elif isinstance(models_data, list):
                models = models_data
            else:
                models = []
            
            if models:
                model_names = [model.get('name', 'unknown') for model in models[:5]]
                print(f"   Sample models: {', '.join(model_names)}...")
                
                            # Check if res.users is available
            if 'res.users' in model_names:
                print("   ✅ res.users model is available (authentication should work)")
            else:
                print("   ⚠️  res.users model not found in first 5 models")
        else:
            print("   ⚠️  No models found in response")
        
        # Direct check for res.users model
        print("\n🔍 Direct check for res.users model...")
        try:
            users_result = fbs.odoo.get_records('res.users', limit=1)
            if users_result.get('success', False):
                print("   ✅ res.users model is directly accessible (authentication will work)")
                if 'data' in users_result and users_result['data']:
                    print(f"   📊 Found {len(users_result['data'])} user records")
                return True
            else:
                print(f"   ❌ res.users model access failed: {users_result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"   ❌ Error accessing res.users model: {str(e)}")
            return False
        else:
            print(f"❌ Model discovery failed: {models_result['error']}")
            return False
        
    except Exception as e:
        print(f"❌ Basic Odoo operations test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 Complete Workflow Test - All Modules in One Step")
    print("=" * 80)
    
    # Setup environment
    setup_environment()
    
    # Run all tests
    test_results = []
    
    test_results.append(("Complete Database Creation", test_complete_database_creation()))
    test_results.append(("Odoo Authentication", test_odoo_authentication()))
    test_results.append(("Basic Odoo Operations", test_basic_odoo_operations()))
    
    # Print results summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{len(test_results)} steps passed")
    
    if passed == len(test_results):
        print("🎉 ALL TESTS PASSED! Complete workflow is working!")
        print("   - Database created with all modules in one step")
        print("   - Admin password changed to MeMiMo@0207")
        print("   - Odoo authentication working")
        print("   - Basic operations functional")
    else:
        failed = len(test_results) - passed
        print(f"⚠️  {failed} step(s) need attention")
    
    return passed == len(test_results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
