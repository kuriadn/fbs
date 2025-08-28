#!/usr/bin/env python3
"""
Rental Test Solution - Complete Odoo Workflow Test
Updated to use the new Odoo database creation methods
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

def test_database_creation():
    """Test 1: Database creation using new methods"""
    print("🧪 STEP 1: Testing Database Creation with New Methods")
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
        
        # Check initial database status
        print("🔍 Checking initial database status...")
        status = fbs.get_database_status()
        print(f"✅ Database status: {status['message']}")
        print()
        
        # Check if databases already exist
        print("🔍 Checking if databases already exist...")
        from fbs_app.services.database_service import DatabaseService
        db_service = DatabaseService('rental_test')
        
        django_exists = db_service._check_database_exists('django', 'rental_test')
        odoo_exists = db_service._check_odoo_database_exists(fbs.odoo_db_name)
        
        print(f"   Django DB exists: {django_exists}")
        print(f"   Odoo DB exists: {odoo_exists}")
        print()
        
        if django_exists and odoo_exists:
            print("✅ Both databases already exist - skipping creation")
            return True
        
        # Create databases using NEW method with specific modules
        print("🔧 Creating solution databases with rental-specific modules...")
        
        # Define modules for rental business
        core_modules = ['base', 'web', 'mail', 'contacts']
        rental_modules = ['sale', 'stock', 'account', 'project']
        
        print(f"   Core modules: {', '.join(core_modules)}")
        print(f"   Rental modules: {', '.join(rental_modules)}")
        
        result = fbs.odoo.create_solution_databases_with_modules(
            core_modules=core_modules,
            additional_modules=rental_modules
        )
        
        if result['success']:
            print("✅ Solution databases created successfully!")
            print(f"   Django DB: {result['django_db_name']}")
            print(f"   Odoo DB: {result['odoo_db_name']}")
            print(f"   Core modules installed: {', '.join(result['core_modules'])}")
            print(f"   Additional modules installed: {', '.join(result['additional_modules'])}")
            return True
        else:
            print(f"⚠️  Database creation result: {result.get('message', 'Unknown status')}")
            if 'results' in result:
                for db_type, db_result in result['results'].items():
                    if not db_result.get('success', False):
                        if 'already exists' in db_result.get('error', ''):
                            print(f"   ✅ {db_type}: Database already exists (this is fine)")
                        else:
                            print(f"   ❌ {db_type}: {db_result.get('error', 'Unknown error')}")
                    else:
                        print(f"   ✅ {db_type}: {db_result.get('message', 'Success')}")
            
            # If databases exist, that's fine - we can continue
            if django_exists and odoo_exists:
                print("✅ Both databases are available - continuing with tests")
                return True
            else:
                return False
            
    except Exception as e:
        print(f"❌ Database creation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_module_management():
    """Test 2: Module management and discovery"""
    print("\n🧪 STEP 2: Testing Module Management")
    print("=" * 60)
    
    try:
        from fbs_app.interfaces import FBSInterface
        
        fbs = FBSInterface('rental_test')
        print(f"✅ FBS initialized for solution: 'rental_test'")
        
        # Test module discovery
        print("🔍 Testing module discovery...")
        available_modules = fbs.odoo.get_available_modules()
        
        if available_modules['success']:
            print("✅ Available modules retrieved successfully")
            for category, modules in available_modules['available_modules'].items():
                print(f"   {category}: {', '.join(modules[:3])}{'...' if len(modules) > 3 else ''}")
        else:
            print(f"❌ Failed to get available modules: {available_modules['error']}")
            return False
        
        # Test installing additional modules
        print("\n📦 Testing additional module installation...")
        new_modules = ['purchase', 'mrp']
        print(f"   Installing: {', '.join(new_modules)}")
        
        install_result = fbs.odoo.install_modules(new_modules)
        
        if install_result['success']:
            print("✅ Additional modules installed successfully")
            print(f"   Modules installed: {', '.join(install_result['modules_installed'])}")
            return True
        else:
            print(f"❌ Module installation failed: {install_result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Module management test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_odoo_integration():
    """Test 3: Odoo integration and model discovery"""
    print("\n🧪 STEP 3: Testing Odoo Integration")
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
            model_names = [model['name'] for model in models_result['data'][:5]]
            print(f"   Sample models: {', '.join(model_names)}...")
        else:
            print(f"❌ Model discovery failed: {models_result['error']}")
            return False
        
        # Test field discovery
        print("\n🔍 Testing field discovery for res.partner...")
        fields_result = fbs.odoo.discover_fields('res.partner')
        
        if fields_result['success']:
            print("✅ Fields discovered successfully")
            field_names = [field['name'] for field in fields_result['data'][:5]]
            print(f"   Sample fields: {', '.join(field_names)}...")
        else:
            print(f"❌ Field discovery failed: {fields_result['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Odoo integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_crud_operations():
    """Test 4: CRUD operations on Odoo models"""
    print("\n🧪 STEP 4: Testing CRUD Operations")
    print("=" * 60)
    
    try:
        from fbs_app.interfaces import FBSInterface
        
        fbs = FBSInterface('rental_test')
        print(f"✅ FBS initialized for solution: 'rental_test'")
        
        # Test CREATE operation
        print("📝 Testing CREATE operation on res.partner...")
        partner_data = {
            'name': 'Test Rental Company',
            'is_company': True,
            'customer_rank': 1,
            'supplier_rank': 0
        }
        
        create_result = fbs.odoo.create_record('res.partner', partner_data)
        
        if create_result['success']:
            partner_id = create_result['data']['id']
            print(f"✅ Partner created successfully with ID: {partner_id}")
        else:
            print(f"❌ Partner creation failed: {create_result['error']}")
            return False
        
        # Test READ operation
        print("\n📖 Testing READ operation...")
        read_result = fbs.odoo.get_record('res.partner', partner_id)
        
        if read_result['success']:
            print("✅ Record read successfully")
            print(f"   Partner name: {read_result['data']['name']}")
        else:
            print(f"❌ Record read failed: {read_result['error']}")
            return False
        
        # Test UPDATE operation
        print("\n✏️  Testing UPDATE operation...")
        update_data = {'customer_rank': 2}
        update_result = fbs.odoo.update_record('res.partner', partner_id, update_data)
        
        if update_result['success']:
            print("✅ Record updated successfully")
        else:
            print(f"❌ Record update failed: {update_result['error']}")
            return False
        
        # Test DELETE operation
        print("\n🗑️  Testing DELETE operation...")
        delete_result = fbs.odoo.delete_record('res.partner', partner_id)
        
        if delete_result['success']:
            print("✅ Record deleted successfully")
        else:
            print(f"❌ Record deletion failed: {delete_result['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CRUD operations test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_business_workflow():
    """Test 5: Complete business workflow"""
    print("\n🧪 STEP 5: Testing Complete Business Workflow")
    print("=" * 60)
    
    try:
        from fbs_app.interfaces import FBSInterface
        
        fbs = FBSInterface('rental_test')
        print(f"✅ FBS initialized for solution: 'rental_test'")
        
        print("🔍 Testing complete rental business workflow...")
        
        # 1. Create a rental company
        print("   1️⃣  Creating rental company...")
        company_data = {
            'name': 'Rental Test Company',
            'is_company': True,
            'customer_rank': 1
        }
        company_result = fbs.odoo.create_record('res.partner', company_data)
        
        if not company_result['success']:
            print(f"   ❌ Company creation failed: {company_result['error']}")
            return False
        
        company_id = company_result['data']['id']
        print(f"   ✅ Company created with ID: {company_id}")
        
        # 2. Create a rental product
        print("   2️⃣  Creating rental product...")
        product_data = {
            'name': 'Test Rental Product',
            'type': 'product',
            'categ_id': 1,  # Default category
            'list_price': 100.0
        }
        product_result = fbs.odoo.create_record('product.product', product_data)
        
        if not product_result['success']:
            print(f"   ❌ Product creation failed: {product_result['error']}")
            return False
        
        product_id = product_result['data']['id']
        print(f"   ✅ Product created with ID: {product_id}")
        
        # 3. Create a rental order
        print("   3️⃣  Creating rental order...")
        order_data = {
            'partner_id': company_id,
            'date_order': '2024-08-26',
            'order_line': [(0, 0, {
                'product_id': product_id,
                'product_uom_qty': 1,
                'price_unit': 100.0
            })]
        }
        order_result = fbs.odoo.create_record('sale.order', order_data)
        
        if not order_result['success']:
            print(f"   ❌ Order creation failed: {order_result['error']}")
            return False
        
        order_id = order_result['data']['id']
        print(f"   ✅ Order created with ID: {order_id}")
        
        print("   🎉 Complete rental workflow executed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Business workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 Rental Test Solution - Complete Odoo Workflow Test")
    print("Updated to use new Odoo database creation methods")
    print("=" * 80)
    
    # Setup environment
    setup_environment()
    
    # Run all tests
    test_results = []
    
    test_results.append(("Database Creation", test_database_creation()))
    test_results.append(("Module Management", test_module_management()))
    test_results.append(("Odoo Integration", test_odoo_integration()))
    test_results.append(("CRUD Operations", test_crud_operations()))
    test_results.append(("Business Workflow", test_business_workflow()))
    
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
        print("🎉 ALL TESTS PASSED! Workflows are working correctly!")
    else:
        failed = len(test_results) - passed
        print(f"⚠️  {failed} step(s) need attention")
    
    return passed == len(test_results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
