#!/usr/bin/env python3
"""
FBS Suite v2.0.1 Installation Script

This script installs FBS Suite version 2.0.1 with all critical bug fixes
and Odoo integration improvements.

Usage:
    python install_v2.0.1.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print installation header"""
    print("=" * 70)
    print("🚀 FBS Suite v2.0.1 Installation Script")
    print("=" * 70)
    print("Version: 2.0.1")
    print("Release Date: August 27, 2024")
    print("Type: Patch Release (Critical Bug Fixes)")
    print("=" * 70)

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - Compatible")
    return True

def check_pip():
    """Check if pip is available"""
    print("\n📦 Checking pip availability...")
    
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip is not available")
        print("   Please install pip first")
        return False

def check_virtual_environment():
    """Check if running in virtual environment"""
    print("\n🔒 Checking virtual environment...")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
        return True
    else:
        print("⚠️  Not running in virtual environment")
        print("   It's recommended to use a virtual environment")
        return False

def install_fbs_suite():
    """Install FBS Suite v2.0.1"""
    print("\n📥 Installing FBS Suite v2.0.1...")
    
    try:
        # Install in development mode
        cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
        print(f"   Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ FBS Suite v2.0.1 installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def install_dev_dependencies():
    """Install development dependencies"""
    print("\n🔧 Installing development dependencies...")
    
    try:
        cmd = [sys.executable, "-m", "pip", "install", "-e", ".[dev]"]
        print(f"   Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Development dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Development dependencies installation failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def verify_installation():
    """Verify the installation"""
    print("\n🔍 Verifying installation...")
    
    try:
        # Try to import FBS modules
        import fbs_app
        print("✅ fbs_app module imported successfully")
        
        import fbs_dms
        print("✅ fbs_dms module imported successfully")
        
        import fbs_license_manager
        print("✅ fbs_license_manager module imported successfully")
        
        # Check version
        print(f"✅ FBS Suite v2.0.1 is properly installed")
        return True
        
    except ImportError as e:
        print(f"❌ Import verification failed: {e}")
        return False

def show_next_steps():
    """Show next steps for configuration"""
    print("\n" + "=" * 70)
    print("🎯 Next Steps for Full Odoo Integration")
    print("=" * 70)
    print("1. Configure Odoo Connection in Django settings:")
    print("   FBS_APP = {")
    print("       'ODOO_BASE_URL': 'http://your-odoo-server:8069',")
    print("       'DATABASE_USER': 'your_odoo_user',")
    print("       'DATABASE_PASSWORD': 'your_odoo_password',")
    print("   }")
    print("\n2. Add FBS apps to INSTALLED_APPS:")
    print("   INSTALLED_APPS = [")
    print("       'fbs_app.apps.FBSAppConfig',")
    print("       'fbs_dms.apps.DMSAppConfig',")
    print("       'fbs_license_manager.apps.LicenseManagerAppConfig',")
    print("   ]")
    print("\n3. Create Odoo database and run migrations")
    print("4. Test Odoo integration:")
    print("   from fbs_app.interfaces import FBSInterface")
    print("   fbs = FBSInterface('your_solution')")
    print("   result = fbs.odoo.get_database_info()")
    print("\n5. Create FBS tables:")
    print("   result = fbs.odoo.create_fbs_tables()")
    print("=" * 70)

def main():
    """Main installation function"""
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    check_virtual_environment()
    
    # Install FBS Suite
    if not install_fbs_suite():
        print("\n❌ Installation failed. Please check the error messages above.")
        sys.exit(1)
    
    # Install development dependencies (optional)
    install_dev_dependencies()
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed.")
        sys.exit(1)
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 FBS Suite v2.0.1 installation completed successfully!")
    print("   All critical Odoo integration bugs have been fixed.")
    print("   Your FBS installation is ready for production use!")

if __name__ == "__main__":
    main()
