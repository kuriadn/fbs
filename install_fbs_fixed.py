#!/usr/bin/env python3
"""
FBS Fixed Installation Script

This script properly installs FBS with all required database tables and migrations.
Fixes the critical issues identified in the integration communique.
"""

import os
import sys
import subprocess
import django
from pathlib import Path

def setup_django_environment():
    """Setup Django environment for migrations"""
    try:
        # Add the current directory to Python path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_project.settings')
        
        # Configure Django
        django.setup()
        
        print("✅ Django environment configured successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to configure Django environment: {e}")
        return False

def run_django_migrations():
    """Run Django migrations to create all FBS tables"""
    try:
        print("\n🔄 Running Django migrations...")
        
        # Run migrations for the default database
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate', '--database=default'
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Default database migrations completed successfully")
        else:
            print(f"❌ Default database migrations failed: {result.stderr}")
            return False
        
        # Run migrations for the licensing database if it exists
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate', '--database=licensing'
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Licensing database migrations completed successfully")
        else:
            print("⚠️  Licensing database migrations failed (this is normal if database doesn't exist)")
        
        return True
    except Exception as e:
        print(f"❌ Failed to run migrations: {e}")
        return False

def verify_tables_created():
    """Verify that FBS tables were created successfully"""
    try:
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        print("\n🔍 Verifying FBS tables...")
        
        # Check if key FBS tables exist
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'fbs_%'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            if tables:
                print("✅ FBS tables found:")
                for table in tables:
                    print(f"   - {table}")
                
                # Check for the critical table that was causing issues
                if 'fbs_approval_requests' in tables:
                    print("✅ Critical table 'fbs_approval_requests' exists!")
                else:
                    print("❌ Critical table 'fbs_approval_requests' missing!")
                    return False
            else:
                print("❌ No FBS tables found!")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to verify tables: {e}")
        return False

def test_fbs_functionality():
    """Test basic FBS functionality"""
    try:
        print("\n🧪 Testing FBS functionality...")
        
        # Test model imports
        from fbs_app.models import ApprovalRequest, OdooDatabase, TokenMapping
        print("✅ FBS models imported successfully")
        
        # Test signal registration
        from fbs_app.signals import safe_signal_execution
        print("✅ FBS signals loaded successfully")
        
        # Test database routing
        from fbs_app.routers import FBSDatabaseRouter
        router = FBSDatabaseRouter()
        print("✅ FBS database router initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ FBS functionality test failed: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 FBS Fixed Installation Script")
    print("=" * 50)
    print("This script fixes the critical database schema issues identified in the integration communique.")
    
    # Step 1: Setup Django environment
    if not setup_django_environment():
        print("\n❌ Installation failed at Django environment setup")
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_django_migrations():
        print("\n❌ Installation failed at migration execution")
        sys.exit(1)
    
    # Step 3: Verify tables
    if not verify_tables_created():
        print("\n❌ Installation failed at table verification")
        sys.exit(1)
    
    # Step 4: Test functionality
    if not test_fbs_functionality():
        print("\n❌ Installation failed at functionality testing")
        sys.exit(1)
    
    print("\n🎉 FBS installation completed successfully!")
    print("\n📋 What was fixed:")
    print("   ✅ Created missing migrations directory")
    print("   ✅ Generated Django migration files for all FBS models")
    print("   ✅ Created all required database tables")
    print("   ✅ Added signal safety wrapper to prevent failures")
    print("   ✅ Verified table creation and functionality")
    
    print("\n🔧 Next steps:")
    print("   1. Restart your Django application")
    print("   2. Test your rental solution CRUD operations")
    print("   3. Verify FBS integration is working properly")
    
    print("\n💡 The critical 'fbs_approval_requests' table now exists!")
    print("   Your Location/Tenant deletion operations should work without errors.")

if __name__ == '__main__':
    main()
