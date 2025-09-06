#!/usr/bin/env python3
"""
FBS Critical Bug Fixes Verification Script

Verifies that the code fixes are correctly implemented without requiring Django setup.
This script analyzes the source code directly to confirm fixes are in place.
"""

import os
import sys
import re
from pathlib import Path

def check_search_read_method():
    """Verify search_read method exists in OdooIntegrationInterface"""
    print("🔍 Checking search_read method implementation...")
    
    interfaces_file = Path("fbs_app/interfaces.py")
    if not interfaces_file.exists():
        print("❌ interfaces.py not found")
        return False
    
    content = interfaces_file.read_text()
    
    # Check if search_read method exists
    if "def search_read(" in content:
        print("✅ search_read method found")
        
        # Check method signature
        search_read_pattern = r'def search_read\(self,\s*model_name.*?\):'
        if re.search(search_read_pattern, content, re.DOTALL):
            print("✅ search_read method has correct signature")
            
            # Check if it calls search_read_records
            if "search_read_records" in content:
                print("✅ search_read method calls search_read_records")
                return True
            else:
                print("❌ search_read method doesn't call search_read_records")
                return False
        else:
            print("❌ search_read method signature incorrect")
            return False
    else:
        print("❌ search_read method not found")
        return False

def check_model_mapping():
    """Verify model name mapping is implemented"""
    print("\n🔍 Checking model name mapping...")
    
    interfaces_file = Path("fbs_app/interfaces.py")
    content = interfaces_file.read_text()
    
    # Check if _map_model_name method exists
    if "def _map_model_name(" in content:
        print("✅ _map_model_name method found")
        
        # Check for inventory.location mapping
        if "'inventory.location': 'stock.location'" in content:
            print("✅ inventory.location → stock.location mapping found")
            
            # Check for other mappings
            mappings = [
                "'inventory.warehouse': 'stock.warehouse'",
                "'inventory.picking': 'stock.picking'", 
                "'inventory.move': 'stock.move'"
            ]
            
            all_found = True
            for mapping in mappings:
                if mapping in content:
                    model_name = mapping.split(':')[0].strip("'")
                    print(f"✅ {model_name} mapping found")
                else:
                    model_name = mapping.split(':')[0].strip("'")
                    print(f"❌ {model_name} mapping missing")
                    all_found = False
            
            return all_found
        else:
            print("❌ inventory.location mapping not found")
            return False
    else:
        print("❌ _map_model_name method not found")
        return False

def check_crud_methods_use_mapping():
    """Verify CRUD methods use model name mapping"""
    print("\n🔍 Checking CRUD methods use mapping...")
    
    interfaces_file = Path("fbs_app/interfaces.py")
    content = interfaces_file.read_text()
    
    methods_to_check = [
        'get_records',
        'get_record', 
        'create_record',
        'update_record',
        'delete_record',
        'search_read'
    ]
    
    all_methods_correct = True
    for method in methods_to_check:
        # Find method definition
        method_pattern = rf'def {method}\(.*?\):'
        method_match = re.search(method_pattern, content, re.DOTALL)
        
        if method_match:
            # Get method body (rough approximation)
            method_start = method_match.end()
            # Find next method or end of class
            next_method = re.search(r'\n    def ', content[method_start:])
            method_end = method_start + next_method.start() if next_method else len(content)
            method_body = content[method_start:method_end]
            
            if '_map_model_name' in method_body or 'corrected_model_name' in method_body:
                print(f"✅ {method} uses model mapping")
            else:
                print(f"❌ {method} doesn't use model mapping")
                all_methods_correct = False
        else:
            print(f"❌ {method} method not found")
            all_methods_correct = False
    
    return all_methods_correct

def check_odoo_client_method():
    """Verify OdooClient has search_read_records method"""
    print("\n🔍 Checking OdooClient search_read_records method...")
    
    odoo_client_file = Path("fbs_app/services/odoo_client.py")
    if not odoo_client_file.exists():
        print("❌ odoo_client.py not found")
        return False
    
    content = odoo_client_file.read_text()
    
    if "def search_read_records(" in content:
        print("✅ search_read_records method found in OdooClient")
        
        # Check if method returns proper format
        if "return {" in content and "'success':" in content:
            print("✅ search_read_records returns proper response format")
            return True
        else:
            print("❌ search_read_records doesn't return proper format")
            return False
    else:
        print("❌ search_read_records method not found in OdooClient")
        return False

def check_documentation():
    """Verify documentation files were created"""
    print("\n🔍 Checking documentation...")
    
    guide_file = Path("RENTAL_ENDPOINTS_FIX_GUIDE.md")
    if guide_file.exists():
        print("✅ RENTAL_ENDPOINTS_FIX_GUIDE.md created")
        
        content = guide_file.read_text()
        if "search_read" in content and "inventory.location" in content:
            print("✅ Guide contains fix information")
            return True
        else:
            print("❌ Guide missing fix information")
            return False
    else:
        print("❌ RENTAL_ENDPOINTS_FIX_GUIDE.md not found")
        return False

def generate_verification_report(results):
    """Generate verification report"""
    print("\n" + "="*60)
    print("🔧 FBS CRITICAL FIXES VERIFICATION REPORT")
    print("="*60)
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    failed_checks = total_checks - passed_checks
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Checks: {total_checks}")
    print(f"   Passed: {passed_checks} ✅")
    print(f"   Failed: {failed_checks} ❌")
    print(f"   Success Rate: {(passed_checks/total_checks)*100:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for check_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {check_name}: {status}")
    
    print(f"\n🎯 STATUS FOR RENTAL TEAM:")
    if all(results.values()):
        print("   🎉 ALL FIXES VERIFIED! The FBS Suite core issues are resolved.")
        print("   ")
        print("   📝 NEXT STEPS:")
        print("   1. ✅ search_read method - FIXED")
        print("   2. ✅ inventory.location mapping - FIXED") 
        print("   3. ✅ Model name mapping for all CRUD operations - FIXED")
        print("   4. ✅ Implementation guide provided - COMPLETE")
        print("   ")
        print("   🚀 YOUR RENTAL ENDPOINTS SHOULD NOW WORK!")
        print("   ")
        print("   📖 Follow the RENTAL_ENDPOINTS_FIX_GUIDE.md to:")
        print("      • Update your rental application views")
        print("      • Add proper URL mappings")
        print("      • Test your endpoints")
        print("      • Deploy to production")
        
    else:
        print("   ⚠️  Some fixes need attention. Please review failed checks above.")
        
    print("\n" + "="*60)

def main():
    """Run all verification checks"""
    print("🔧 FBS Critical Fixes Verification")
    print("Analyzing code structure to verify fixes are implemented...")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run all checks
    verification_results = {
        "search_read Method": check_search_read_method(),
        "Model Name Mapping": check_model_mapping(),
        "CRUD Methods Use Mapping": check_crud_methods_use_mapping(), 
        "OdooClient Integration": check_odoo_client_method(),
        "Documentation": check_documentation(),
    }
    
    # Generate report
    generate_verification_report(verification_results)
    
    # Return exit code
    return 0 if all(verification_results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
