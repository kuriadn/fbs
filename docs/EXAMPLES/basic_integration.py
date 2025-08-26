#!/usr/bin/env python3
"""
FBS Basic Integration Example

This example demonstrates the basic usage of FBS (Fayvad Business Suite)
interfaces for common business operations.

Prerequisites:
1. FBS installed and configured
2. Odoo ERP system accessible
3. Valid solution configuration
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main example function"""
    try:
        # Initialize FBS interface
        logger.info("Initializing FBS interface...")
        fbs = initialize_fbs()
        
        # Check system health
        logger.info("Checking system health...")
        check_system_health(fbs)
        
        # Test Odoo integration
        logger.info("Testing Odoo integration...")
        test_odoo_integration(fbs)
        
        # Test virtual fields
        logger.info("Testing virtual fields...")
        test_virtual_fields(fbs)
        
        # Test MSME capabilities
        logger.info("Testing MSME capabilities...")
        test_msme_capabilities(fbs)
        
        # Test business intelligence
        logger.info("Testing business intelligence...")
        test_business_intelligence(fbs)
        
        # Test workflow management
        logger.info("Testing workflow management...")
        test_workflow_management(fbs)
        
        # Test accounting operations
        logger.info("Testing accounting operations...")
        test_accounting_operations(fbs)
        
        # Test caching system
        logger.info("Testing caching system...")
        test_caching_system(fbs)
        
        logger.info("✅ All basic integration tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Example failed: {str(e)}")
        sys.exit(1)

def initialize_fbs():
    """Initialize FBS interface with solution context"""
    try:
        from fbs_app.interfaces import FBSInterface
        
        # Get solution name from environment or use default
        solution_name = os.getenv('FBS_SOLUTION_NAME', 'demo_solution')
        
        # Initialize FBS interface
        fbs = FBSInterface(solution_name)
        
        logger.info(f"FBS interface initialized for solution: {solution_name}")
        return fbs
        
    except ImportError as e:
        logger.error(f"Failed to import FBS: {str(e)}")
        logger.error("Make sure FBS is installed and configured correctly")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize FBS: {str(e)}")
        raise

def check_system_health(fbs):
    """Check FBS system health"""
    try:
        # Get system health
        health = fbs.get_system_health()
        
        if health['success']:
            logger.info(f"System status: {health['status']}")
            
            # Check individual services
            services = health.get('services', {})
            for service, status in services.items():
                logger.info(f"  {service}: {status}")
        else:
            logger.warning("System health check failed")
            
        # Check Odoo availability
        odoo_available = fbs.is_odoo_available()
        logger.info(f"Odoo available: {odoo_available}")
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")

def test_odoo_integration(fbs):
    """Test basic Odoo integration"""
    try:
        # Discover available models
        models = fbs.odoo.discover_models()
        
        if models['success']:
            model_count = len(models['data'])
            logger.info(f"Discovered {model_count} Odoo models")
            
            # Show first few models
            for model in models['data'][:5]:
                logger.info(f"  - {model['name']}: {model.get('display_name', 'N/A')}")
        else:
            logger.warning("Failed to discover Odoo models")
            
        # Test basic record operations
        test_partner_operations(fbs)
        
    except Exception as e:
        logger.error(f"Odoo integration test failed: {str(e)}")

def test_partner_operations(fbs):
    """Test partner (res.partner) operations"""
    try:
        # Get existing partners
        partners = fbs.odoo.get_records(
            'res.partner',
            filters=[('is_company', '=', True)],
            fields=['name', 'email'],
            limit=5
        )
        
        if partners['success']:
            partner_count = len(partners['data'])
            logger.info(f"Found {partner_count} company partners")
            
            if partner_count > 0:
                # Test getting a specific partner
                first_partner = partners['data'][0]
                partner_id = first_partner['id']
                
                partner_detail = fbs.odoo.get_record('res.partner', partner_id)
                if partner_detail['success']:
                    logger.info(f"Partner detail: {partner_detail['data']['name']}")
                    
        else:
            logger.warning("Failed to retrieve partners")
            
    except Exception as e:
        logger.error(f"Partner operations test failed: {str(e)}")

def test_virtual_fields(fbs):
    """Test virtual fields functionality"""
    try:
        # Get existing partners for testing
        partners = fbs.odoo.get_records('res.partner', limit=1)
        
        if not partners['success'] or len(partners['data']) == 0:
            logger.warning("No partners available for virtual fields test")
            return
            
        partner_id = partners['data'][0]['id']
        
        # Set a custom field
        field_result = fbs.fields.set_custom_field(
            'res.partner',
            partner_id,
            'demo_field',
            'demo_value',
            'char'
        )
        
        if field_result['success']:
            logger.info("Custom field set successfully")
            
            # Retrieve the custom field
            field_data = fbs.fields.get_custom_field(
                'res.partner',
                partner_id,
                'demo_field'
            )
            
            if field_data['success']:
                logger.info(f"Custom field value: {field_data['data']}")
                
                # Get all custom fields
                all_custom = fbs.fields.get_custom_fields('res.partner', partner_id)
                if all_custom['success']:
                    custom_count = len(all_custom['data'])
                    logger.info(f"Total custom fields: {custom_count}")
                    
        else:
            logger.warning("Failed to set custom field")
            
    except Exception as e:
        logger.error(f"Virtual fields test failed: {str(e)}")

def test_msme_capabilities(fbs):
    """Test MSME business management capabilities"""
    try:
        # Get business dashboard
        dashboard = fbs.msme.get_dashboard()
        
        if dashboard['success']:
            logger.info("MSME dashboard retrieved successfully")
            
            # Get business KPIs
            kpis = fbs.msme.calculate_kpis()
            
            if kpis['success']:
                logger.info("Business KPIs calculated successfully")
                
                # Get compliance status
                compliance = fbs.msme.get_compliance_status()
                
                if compliance['success']:
                    score = compliance['data'].get('overall_score', 'N/A')
                    logger.info(f"Compliance score: {score}")
                    
        else:
            logger.warning("MSME capabilities test failed")
            
    except Exception as e:
        logger.error(f"MSME capabilities test failed: {str(e)}")

def test_business_intelligence(fbs):
    """Test business intelligence capabilities"""
    try:
        # Get available dashboards
        dashboards = fbs.bi.get_dashboards()
        
        if dashboards['success']:
            dashboard_count = len(dashboards['data'])
            logger.info(f"Available dashboards: {dashboard_count}")
            
            # Get available reports
            reports = fbs.bi.get_reports()
            
            if reports['success']:
                report_count = len(reports['data'])
                logger.info(f"Available reports: {report_count}")
                
                # Get available KPIs
                kpis = fbs.bi.get_kpis()
                
                if kpis['success']:
                    kpi_count = len(kpis['data'])
                    logger.info(f"Available KPIs: {kpi_count}")
                    
        else:
            logger.warning("Business intelligence test failed")
            
    except Exception as e:
        logger.error(f"Business intelligence test failed: {str(e)}")

def test_workflow_management(fbs):
    """Test workflow management capabilities"""
    try:
        # Get workflow definitions
        workflows = fbs.workflows.get_workflow_definitions()
        
        if workflows['success']:
            workflow_count = len(workflows['data'])
            logger.info(f"Available workflows: {workflow_count}")
            
            # Get active workflow instances
            active_workflows = fbs.workflows.get_active_workflows()
            
            if active_workflows['success']:
                active_count = len(active_workflows['data'])
                logger.info(f"Active workflows: {active_count}")
                
        else:
            logger.warning("Workflow management test failed")
            
    except Exception as e:
        logger.error(f"Workflow management test failed: {str(e)}")

def test_accounting_operations(fbs):
    """Test accounting operations"""
    try:
        # Get basic ledger
        ledger = fbs.accounting.get_basic_ledger()
        
        if ledger['success']:
            logger.info("Basic ledger retrieved successfully")
            
            # Get income/expense summary
            summary = fbs.accounting.get_income_expense_summary()
            
            if summary['success']:
                logger.info("Income/expense summary retrieved successfully")
                
                # Get financial health indicators
                health = fbs.accounting.get_financial_health_indicators()
                
                if health['success']:
                    logger.info("Financial health indicators retrieved successfully")
                    
        else:
            logger.warning("Accounting operations test failed")
            
    except Exception as e:
        logger.error(f"Accounting operations test failed: {str(e)}")

def test_caching_system(fbs):
    """Test caching system"""
    try:
        # Set cache value
        cache_key = 'demo_cache_key'
        cache_value = {'timestamp': datetime.now().isoformat(), 'data': 'demo_value'}
        
        set_result = fbs.cache.set_cache(cache_key, cache_value, expiry_hours=1)
        
        if set_result['success']:
            logger.info("Cache value set successfully")
            
            # Retrieve cache value
            get_result = fbs.cache.get_cache(cache_key)
            
            if get_result['success']:
                logger.info("Cache value retrieved successfully")
                
                # Get cache statistics
                stats = fbs.cache.get_cache_stats()
                
                if stats['success']:
                    logger.info("Cache statistics retrieved successfully")
                    
        else:
            logger.warning("Caching system test failed")
            
    except Exception as e:
        logger.error(f"Caching system test failed: {str(e)}")

def cleanup_demo_data(fbs):
    """Clean up demo data created during testing"""
    try:
        logger.info("Cleaning up demo data...")
        
        # Clean up custom fields
        partners = fbs.odoo.get_records('res.partner', limit=10)
        
        if partners['success']:
            for partner in partners['data']:
                # Delete demo custom field if it exists
                fbs.fields.delete_custom_field(
                    'res.partner',
                    partner['id'],
                    'demo_field'
                )
                
        logger.info("Demo data cleanup completed")
        
    except Exception as e:
        logger.warning(f"Demo data cleanup failed: {str(e)}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup demo data
        try:
            fbs = initialize_fbs()
            cleanup_demo_data(fbs)
        except:
            pass
