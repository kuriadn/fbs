#!/usr/bin/env python3
"""
FBS Installation Test Script

This script tests the installation and basic functionality of FBS
after pip install -e . has been run.
"""

import sys
import os

def test_imports():
    """Test that all FBS modules can be imported"""
    print("🔍 Testing FBS imports...")
    
    try:
        # Test core FBS app
        import fbs_app
        print("✅ fbs_app imported successfully")
        
        # Test DMS app
        import fbs_dms
        print("✅ fbs_dms imported successfully")
        
        # Test License Manager app
        import fbs_license_manager
        print("✅ fbs_license_manager imported successfully")
        
        # Test main interfaces
        from fbs_app.interfaces import FBSInterface
        print("✅ FBSInterface imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_basic_functionality():
    """Test basic FBS functionality"""
    print("\n🔍 Testing basic functionality...")
    
    try:
        from fbs_app.interfaces import FBSInterface
        
        # Initialize interface
        fbs = FBSInterface('test_solution')
        print("✅ FBS interface initialized")
        
        # Test system health
        health = fbs.get_system_health()
        print(f"✅ System health check: {health.get('status', 'unknown')}")
        
        # Test solution info
        info = fbs.get_solution_info()
        print(f"✅ Solution info retrieved: {info.get('solution_name', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {str(e)}")
        return False

def test_package_info():
    """Test package information"""
    print("\n🔍 Testing package information...")
    
    try:
        import fbs_app
        import fbs_dms
        import fbs_license_manager
        
        print(f"✅ fbs_app version: {getattr(fbs_app, '__version__', 'unknown')}")
        print(f"✅ fbs_dms version: {getattr(fbs_dms, '__version__', 'unknown')}")
        print(f"✅ fbs_license_manager version: {getattr(fbs_license_manager, '__version__', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Package info test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 FBS Installation Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Installation may be incomplete.")
        sys.exit(1)
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed. Check configuration.")
        sys.exit(1)
    
    # Test package info
    if not test_package_info():
        print("\n❌ Package info tests failed.")
        sys.exit(1)
    
    print("\n🎉 All tests passed! FBS is installed and working correctly.")
    print("\nNext steps:")
    print("1. Add FBS apps to your Django INSTALLED_APPS")
    print("2. Configure your Odoo connection")
    print("3. Run migrations")
    print("4. Start building your business application!")
    
    print("\n📚 Documentation: https://github.com/kuriadn/fbs/tree/main/docs")
    print("🔧 Examples: https://github.com/kuriadn/fbs/tree/main/docs/EXAMPLES")

if __name__ == '__main__':
    main()
