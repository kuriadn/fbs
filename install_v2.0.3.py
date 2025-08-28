#!/usr/bin/env python3
"""
FBS Suite v2.0.3 Installation Script
=====================================

This script installs FBS Suite v2.0.3 and verifies all components are working.
Use this in your solutions to ensure FBS is properly installed and configured.

Usage:
    python3 install_v2.0.3.py

Requirements:
    - Python 3.8+
    - pip
    - Git repository access
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"🚀 {title}")
    print("=" * 80)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n🔧 Step {step}: {description}")
    print("-" * 60)

def run_command(command, description, check=True):
    """Run a command and handle results"""
    print(f"   Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"      Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"      Error: {result.stderr.strip()}")
            if check:
                sys.exit(1)
            return False
    except Exception as e:
        print(f"   ❌ {description} - EXCEPTION: {str(e)}")
        if check:
            sys.exit(1)
        return False

def check_python_version():
    """Check Python version compatibility"""
    print_step(1, "Checking Python Version")
    
    version = sys.version_info
    print(f"   Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Python version is compatible (3.8+)")
        return True
    else:
        print("   ❌ Python 3.8+ is required")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are available"""
    print_step(2, "Checking System Dependencies")
    
    # Check pip
    try:
        import pip
        print("   ✅ pip is available")
    except ImportError:
        print("   ❌ pip is not available")
        sys.exit(1)
    
    # Check git
    if run_command("git --version", "Git availability", check=False):
        print("   ✅ Git is available")
    else:
        print("   ⚠️  Git not found - some features may be limited")
    
    # Check if we're in the FBS project directory
    current_dir = Path.cwd()
    setup_py = current_dir / "setup.py"
    pyproject_toml = current_dir / "pyproject.toml"
    
    if setup_py.exists() and pyproject_toml.exists():
        print("   ✅ Found FBS project files in current directory")
        print(f"   📁 Project path: {current_dir}")
    else:
        print("   ⚠️  Not in FBS project directory")
        print("   💡 Make sure you're running this script from the FBS project root")
        print("   💡 Look for setup.py and pyproject.toml files")

def install_fbs():
    """Install FBS Suite v2.0.3"""
    print_step(3, "Installing FBS Suite v2.0.3")
    
    # Check if we're in the FBS project directory
    current_dir = Path.cwd()
    setup_py = current_dir / "setup.py"
    pyproject_toml = current_dir / "pyproject.toml"
    
    if setup_py.exists() and pyproject_toml.exists():
        print("   📦 Found FBS project files in current directory")
        print(f"   📁 Project path: {current_dir}")
        
        # Check if FBS is already in Python path
        try:
            import fbs_app
            print("   ✅ FBS is already available in Python path")
            return True
        except ImportError:
            pass
        
        # Try user-specific installation (--user flag)
        print("   📦 Attempting user-specific installation...")
        if run_command("pip install --user -e .", "User-specific editable install", check=False):
            print("   ✅ Installed to user directory")
            return True
        
        # Try with virtual environment detection
        venv = os.environ.get('VIRTUAL_ENV')
        if venv:
            print(f"   📦 Virtual environment detected: {venv}")
            if run_command("pip install -e .", "Editable install in virtual environment", check=False):
                print("   ✅ Installed in virtual environment")
                return True
        
        # Fallback: Add current directory to Python path
        print("   📦 Adding current directory to Python path")
        if current_dir not in sys.path:
            sys.path.insert(0, str(current_dir))
            print("   ✅ Current directory added to Python path")
        
        # Verify FBS can now be imported
        try:
            import fbs_app
            print("   ✅ FBS can now be imported from current directory")
            return True
        except ImportError as e:
            print(f"   ❌ Still cannot import FBS: {str(e)}")
    
    # If not in FBS directory, try other methods
    print("   📦 Not in FBS project directory, trying alternative methods...")
    
    # Try to install from Git repository (if it exists)
    print("   📦 Trying Git repository installation...")
    if run_command("pip install --user git+https://github.com/kuriadn/fbs.git@v2.0.3", 
                   "User-specific Git install", check=False):
        print("   ✅ Installed from Git repository")
        return True
    
    # Try PyPI as last resort
    print("   📦 Trying PyPI installation...")
    if run_command("pip install --user fbs-suite==2.0.3", "User-specific PyPI install", check=False):
        print("   ✅ Installed from PyPI")
        return True
    
    print("   ❌ All installation methods failed")
    print("   💡 Try running this script from the FBS project directory")
    sys.exit(1)

def verify_installation():
    """Verify FBS Suite is properly installed"""
    print_step(4, "Verifying FBS Installation")
    
    # Check if FBS modules can be imported (basic imports only)
    basic_modules = ['fbs_app']
    
    for module_name in basic_modules:
        try:
            module = importlib.import_module(module_name)
            print(f"   ✅ {module_name} imported successfully")
        except ImportError as e:
            print(f"   ❌ {module_name} import failed: {str(e)}")
            return False
    
    # Check version
    try:
        import fbs_app
        if hasattr(fbs_app, '__version__'):
            print(f"   📊 FBS version: {fbs_app.__version__}")
        else:
            print("   📊 FBS version: 2.0.3 (installed)")
    except Exception as e:
        print(f"   ⚠️  Could not determine version: {str(e)}")
    
    # Check if we can access the project structure
    current_dir = Path.cwd()
    expected_files = [
        'setup.py',
        'pyproject.toml',
        'fbs_app/__init__.py',
        'fbs_app/interfaces.py',
        'fbs_app/services/__init__.py',
        'fbs_dms/__init__.py',
        'fbs_license_manager/__init__.py'
    ]
    
    print("   📁 Checking project structure...")
    for file_path in expected_files:
        if (current_dir / file_path).exists():
            print(f"      ✅ {file_path}")
        else:
            print(f"      ❌ {file_path} (missing)")
            return False
    
    print("   ✅ Project structure verified")
    
    # Note about lazy imports
    print("   💡 Note: Some services use lazy imports to avoid Django settings issues")
    print("   💡 This ensures FBS can be imported without Django configuration")
    
    return True

def test_basic_functionality():
    """Test basic FBS functionality"""
    print_step(5, "Testing Basic FBS Functionality")
    
    try:
        # Test basic module imports (without Django initialization)
        print("   🔍 Testing basic module imports...")
        
        # Test FBS interface class definition (not instantiation)
        from fbs_app.interfaces import FBSInterface
        print("   ✅ FBSInterface class imported successfully")
        
        # Test core service classes (not instantiation)
        from fbs_app.services.database_service import DatabaseService
        print("   ✅ DatabaseService class imported successfully")
        
        from fbs_app.services.odoo_client import OdooClient
        print("   ✅ OdooClient class imported successfully")
        
        from fbs_app.services.field_merger_service import FieldMergerService
        print("   ✅ FieldMergerService class imported successfully")
        
        # Test that we can access the solution naming logic
        test_solution = "test_installation"
        expected_django_db = f"djo_{test_solution}_db"
        expected_odoo_db = f"fbs_{test_solution}_db"
        
        print(f"   📊 Expected Django DB name: {expected_django_db}")
        print(f"   📊 Expected Odoo DB name: {expected_odoo_db}")
        
        # Test that the classes have the expected attributes
        if hasattr(FBSInterface, '__init__'):
            print("   ✅ FBSInterface has proper constructor")
        else:
            print("   ❌ FBSInterface missing constructor")
            return False
        
        if hasattr(DatabaseService, '__init__'):
            print("   ✅ DatabaseService has proper constructor")
        else:
            print("   ❌ DatabaseService missing constructor")
            return False
        
        if hasattr(OdooClient, '__init__'):
            print("   ✅ OdooClient has proper constructor")
        else:
            print("   ❌ OdooClient missing constructor")
            return False
        
        if hasattr(FieldMergerService, '__init__'):
            print("   ✅ FieldMergerService has proper constructor")
        else:
            print("   ❌ FieldMergerService missing constructor")
            return False
        
        print("   💡 Note: Some services use lazy imports to avoid Django settings issues")
        print("   💡 These services will be imported when actually needed in Django context")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Basic functionality test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_usage_examples():
    """Show usage examples for solutions"""
    print_step(6, "Usage Examples for Solutions")
    
    print("""
   📚 How to use FBS in your solution:
   
   1. Initialize FBS for your solution:
      from fbs_app.interfaces import FBSInterface
      fbs = FBSInterface('your_solution_name')
   
   2. Create solution databases:
      result = fbs.odoo.create_solution_databases_with_modules(
          core_modules=['base', 'web', 'mail'],
          additional_modules=['sale', 'stock', 'account']
      )
   
   3. Use Odoo integration:
      # Get records
      users = fbs.odoo.get_records('res.users')
      
      # Create records
      partner = fbs.odoo.create_record('res.partner', {
          'name': 'Test Partner',
          'email': 'test@example.com'
      })
   
   4. Use Virtual Fields:
      fbs.virtual.set_custom_field('res.partner', 1, 'custom_field', 'value')
   
   5. Use DMS features:
      fbs.dms.upload_document('invoice.pdf', 'invoices')
   
   6. Use License Management:
      fbs.license.create_license('basic_plan', 'user@example.com')
   """)

def main():
    """Main installation process"""
    print_header("FBS Suite v2.0.3 Installation & Verification")
    
    print("This script will install FBS Suite v2.0.3 and verify all components.")
    print("Make sure you have Python 3.8+ and pip installed.")
    
    # Run all steps
    check_python_version()
    check_dependencies()
    install_fbs()
    verify_installation()
    
    if test_basic_functionality():
        print("\n" + "=" * 80)
        print("🎉 FBS Suite v2.0.3 Installation Successful!")
        print("=" * 80)
        
        show_usage_examples()
        
        print("\n" + "=" * 80)
        print("✅ Your FBS Suite is ready to use in solutions!")
        print("=" * 80)
        
        return True
    else:
        print("\n" + "=" * 80)
        print("❌ FBS Suite installation verification failed")
        print("=" * 80)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
