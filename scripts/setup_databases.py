#!/usr/bin/env python3
"""
Database Setup Script for FBS Multi-Database Architecture

This script creates and configures the required databases for FBS:
- fbs_system_db: FBS system-wide configurations
- lic_system_db: System-wide licensing management
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'user': os.environ.get('DB_USER', 'odoo'),
    'password': os.environ.get('DB_PASSWORD', 'four@One2'),
}

# Database names
SYSTEM_DB = os.environ.get('DB_NAME', 'fbs_system_db')
LICENSING_DB = os.environ.get('LIC_DB_NAME', 'lic_system_db')

def create_database(db_name):
    """Create a PostgreSQL database"""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Created database: {db_name}")
        else:
            print(f"ℹ️  Database already exists: {db_name}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database {db_name}: {e}")
        return False
    
    return True

def test_database_connection(db_name):
    """Test connection to a specific database"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=db_name
        )
        conn.close()
        print(f"✅ Connection test successful: {db_name}")
        return True
    except Exception as e:
        print(f"❌ Connection test failed for {db_name}: {e}")
        return False

def main():
    """Main setup function"""
    print("🏗️  Setting up FBS Multi-Database Architecture")
    print("=" * 50)
    
    # Create databases
    print("\n📊 Creating databases...")
    
    success = True
    success &= create_database(SYSTEM_DB)
    success &= create_database(LICENSING_DB)
    
    if not success:
        print("\n❌ Database creation failed!")
        sys.exit(1)
    
    # Test connections
    print("\n🔍 Testing database connections...")
    
    success = True
    success &= test_database_connection(SYSTEM_DB)
    success &= test_database_connection(LICENSING_DB)
    
    if not success:
        print("\n❌ Database connection tests failed!")
        sys.exit(1)
    
    print("\n✅ Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run Django migrations:")
    print(f"   python manage.py migrate --database=default")
    print(f"   python manage.py migrate --database=licensing")
    print("2. Verify database routing in Django admin")
    print("3. Test application functionality")

if __name__ == '__main__':
    main()
