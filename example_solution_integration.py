#!/usr/bin/env python3
"""
Example Solution Integration with FBS Suite v2.0.2
==================================================

This example demonstrates how a solution would integrate with FBS Suite v2.0.2.
It shows the complete workflow from initialization to using various FBS features.

Usage:
    python3 example_solution_integration.py

This example creates a fictional "inventory_tracker" solution.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Set up environment variables for the example"""
    print("🔧 Setting up environment variables...")
    
    # Database connection settings
    os.environ['FBS_DB_HOST'] = 'localhost'
    os.environ['FBS_DB_PORT'] = '5432'
    os.environ['FBS_DB_USER'] = 'odoo'
    os.environ['FBS_DB_PASSWORD'] = 'four@One2'
    os.environ['FBS_DJANGO_USER'] = 'fayvad'
    os.environ['FBS_DJANGO_PASSWORD'] = 'MeMiMo@0207'
    
    # Odoo authentication settings
    os.environ['ODOO_USER'] = 'admin'
    os.environ['ODOO_PASSWORD'] = 'MeMiMo@0207'
    
    print("✅ Environment setup complete")
    print()

def example_inventory_tracker_solution():
    """Example of how an inventory tracking solution would use FBS"""
    print("🏪 Inventory Tracker Solution - FBS Integration Example")
    print("=" * 80)
    
    try:
        # Step 1: Initialize FBS for our solution
        print("\n🔧 Step 1: Initializing FBS for 'inventory_tracker' solution")
        from fbs_app.interfaces import FBSInterface
        
        fbs = FBSInterface('inventory_tracker')
        print(f"✅ FBS initialized for solution: 'inventory_tracker'")
        print(f"📊 Django DB: {fbs.django_db_name}")
        print(f"📊 Odoo DB: {fbs.odoo_db_name}")
        
        # Step 2: Create solution databases with required modules
        print("\n🔧 Step 2: Creating solution databases with inventory modules")
        
        # Define modules needed for inventory tracking
        core_modules = ['base', 'web', 'mail', 'contacts']
        inventory_modules = ['stock', 'product', 'purchase', 'sale', 'account']
        
        print(f"📦 Core modules: {', '.join(core_modules)}")
        print(f"📦 Inventory modules: {', '.join(inventory_modules)}")
        
        # Create databases
        result = fbs.odoo.create_solution_databases_with_modules(
            core_modules=core_modules,
            additional_modules=inventory_modules
        )
        
        if result['success']:
            print("✅ Solution databases are ready!")
            print(f"   All modules installed: {', '.join(result['all_modules_installed'])}")
            
            if result.get('django_exists') or result.get('odoo_exists'):
                print("   ℹ️  Some databases already existed (this is fine)")
        else:
            print(f"❌ Database creation failed: {result.get('error')}")
            return False
        
        # Step 3: Test Odoo integration
        print("\n🔧 Step 3: Testing Odoo integration")
        
        # Discover available models
        models_result = fbs.odoo.discover_models()
        if models_result['success']:
            print("✅ Models discovered successfully")
            
            # Look for inventory-related models
            models_data = models_result['data']
            if isinstance(models_data, dict) and 'models' in models_data:
                models = models_data['models']
            elif isinstance(models_data, list):
                models = models_data
            else:
                models = []
            
            if models:
                # Find inventory models
                inventory_models = [m for m in models if 'stock' in m.get('name', '').lower() or 'product' in m.get('name', '').lower()]
                if inventory_models:
                    print(f"   📦 Found {len(inventory_models)} inventory-related models")
                    for model in inventory_models[:3]:  # Show first 3
                        print(f"      - {model.get('name', 'Unknown')}")
                else:
                    print("   ⚠️  No inventory models found")
        else:
            print(f"❌ Model discovery failed: {models_result.get('error')}")
        
        # Step 4: Demonstrate CRUD operations
        print("\n🔧 Step 4: Demonstrating CRUD operations")
        
        try:
            # Get some partners (customers/suppliers)
            partners_result = fbs.odoo.get_records('res.partner', limit=5)
            if partners_result['success']:
                print("✅ Partner records retrieved successfully")
                if 'data' in partners_result and partners_result['data']:
                    print(f"   📊 Found {len(partners_result['data'])} partner records")
                else:
                    print("   ℹ️  No partner records found (this is normal for new databases)")
            else:
                print(f"⚠️  Partner retrieval failed: {partners_result.get('error')}")
                
        except Exception as e:
            print(f"⚠️  CRUD test skipped due to: {str(e)}")
        
        # Step 5: Show Virtual Fields usage
        print("\n🔧 Step 5: Virtual Fields System")
        print("   💡 Virtual Fields allow you to extend Odoo models with custom data")
        print("   💡 Example: Add 'supplier_rating' to res.partner model")
        print("   💡 Example: Add 'warehouse_location' to stock.move model")
        
        # Step 6: Show DMS capabilities
        print("\n🔧 Step 6: Document Management System")
        print("   💡 Upload inventory documents (invoices, receipts, manifests)")
        print("   💡 Categorize by document type and supplier")
        print("   💡 Search and retrieve documents with metadata")
        
        # Step 7: Show License Management
        print("\n🔧 Step 7: License Management")
        print("   💡 Manage user access to different inventory features")
        print("   💡 Track subscription plans and feature limits")
        print("   💡 Handle trial periods and upgrades")
        
        print("\n" + "=" * 80)
        print("🎉 Inventory Tracker Solution Integration Complete!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Solution integration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_integration_patterns():
    """Show common integration patterns for solutions"""
    print("\n📚 Common Integration Patterns for Solutions")
    print("=" * 60)
    
    patterns = [
        {
            "name": "E-commerce Platform",
            "modules": ["sale", "stock", "product", "website_sale", "payment"],
            "features": "Product catalog, inventory, orders, payments"
        },
        {
            "name": "Manufacturing System",
            "modules": ["mrp", "stock", "product", "quality", "maintenance"],
            "features": "Production planning, quality control, maintenance"
        },
        {
            "name": "Service Business",
            "modules": ["project", "timesheet", "sale", "account"],
            "features": "Project management, time tracking, invoicing"
        },
        {
            "name": "Rental Business",
            "modules": ["sale", "stock", "product", "project", "account"],
            "features": "Equipment rental, scheduling, billing"
        }
    ]
    
    for pattern in patterns:
        print(f"\n🏢 {pattern['name']}")
        print(f"   📦 Modules: {', '.join(pattern['modules'])}")
        print(f"   ✨ Features: {pattern['features']}")

def main():
    """Main example execution"""
    print("🚀 FBS Suite v2.0.2 - Solution Integration Example")
    print("=" * 80)
    
    # Setup environment
    setup_environment()
    
    # Run the example
    if example_inventory_tracker_solution():
        print("\n✅ Example completed successfully!")
        
        # Show integration patterns
        show_integration_patterns()
        
        print("\n" + "=" * 80)
        print("🎯 Next Steps for Your Solution:")
        print("1. Replace 'inventory_tracker' with your solution name")
        print("2. Customize the module list for your business needs")
        print("3. Implement your business logic using FBS interfaces")
        print("4. Test thoroughly with test_complete_workflow.py")
        print("=" * 80)
        
        return True
    else:
        print("\n❌ Example failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
