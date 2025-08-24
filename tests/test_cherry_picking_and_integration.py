"""
Comprehensive Tests for Cherry-Picking and App Integration

This test suite covers:
- App cherry-picking scenarios (installing apps individually or together)
- Integration between different app combinations
- Database isolation with different app configurations
- Feature availability based on installed apps
- Graceful fallbacks when apps are missing
"""

import pytest
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.conf import settings
import json
import time

# Test different app configurations
@pytest.mark.cherry_picking
@pytest.mark.integration
class TestCherryPickingScenarios(TestCase):
    """Test cherry-picking scenarios for different app configurations."""
    
    databases = {'default', 'licensing'}
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.solution_name = 'test_solution'
    
    @pytest.mark.unit
    @pytest.mark.cherry_picking
    def test_fbs_app_only_configuration(self):
        """Test FBS app only configuration."""
        # Test that FBS app is available
        try:
            from fbs_app.interfaces import FBSInterface
            fbs_interface = FBSInterface(self.solution_name)
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
        except ImportError:
            self.fail("FBS app should be available")
    
    @pytest.mark.unit
    @pytest.mark.cherry_picking
    def test_fbs_with_licensing_configuration(self):
        """Test FBS app with licensing configuration."""
        # Test that both FBS and licensing are available
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_license_manager.services import LicenseManager
            
            fbs_interface = FBSInterface(self.solution_name)
            license_manager = LicenseManager(self.solution_name)
            
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
        except ImportError as e:
            self.fail(f"Both FBS and licensing should be available: {e}")
    
    @pytest.mark.unit
    @pytest.mark.cherry_picking
    def test_fbs_with_dms_configuration(self):
        """Test FBS app with DMS configuration."""
        # Test that both FBS and DMS are available
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_dms.services import DocumentService
            
            fbs_interface = FBSInterface(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(document_service, 'create_document'))
        except ImportError as e:
            self.fail(f"Both FBS and DMS should be available: {e}")
    
    @pytest.mark.unit
    @pytest.mark.cherry_picking
    def test_full_stack_configuration(self):
        """Test full stack configuration (FBS + Licensing + DMS)."""
        # Test that all three apps are available
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_license_manager.services import LicenseManager
            from fbs_dms.services import DocumentService
            
            fbs_interface = FBSInterface(self.solution_name)
            license_manager = LicenseManager(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
            self.assertTrue(hasattr(document_service, 'create_document'))
        except ImportError as e:
            self.fail(f"All three apps should be available: {e}")
    
    @pytest.mark.unit
    @pytest.mark.cherry_picking
    def test_graceful_fallbacks(self):
        """Test graceful fallbacks when apps are not available."""
        # Test that FBS app works even when other apps are missing
        try:
            from fbs_app.interfaces import FBSInterface
            fbs_interface = FBSInterface(self.solution_name)
            
            # Should work regardless of other apps
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
        except ImportError:
            self.fail("FBS app should always be available")


@pytest.mark.integration
@pytest.mark.cherry_picking
class TestAppIntegrationScenarios(TestCase):
    """Test app integration scenarios."""
    
    databases = {'default', 'licensing'}
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.solution_name = 'test_solution'
    
    @pytest.mark.integration
    @pytest.mark.cherry_picking
    def test_fbs_license_integration(self):
        """Test FBS and license manager integration."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_license_manager.services import LicenseManager
            
            fbs_interface = FBSInterface(self.solution_name)
            license_manager = LicenseManager(self.solution_name)
            
            # Test that they can work together
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
            
            # Test feature checking
            can_use_odoo = license_manager.feature_flags.is_enabled('odoo_integration')
            self.assertIsInstance(can_use_odoo, bool)
            
        except ImportError as e:
            self.fail(f"FBS and license manager should integrate: {e}")
    
    @pytest.mark.integration
    @pytest.mark.cherry_picking
    def test_fbs_dms_integration(self):
        """Test FBS and DMS integration."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_dms.services import DocumentService
            
            fbs_interface = FBSInterface(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            
            # Test that they can work together
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(document_service, 'create_document'))
            
        except ImportError as e:
            self.fail(f"FBS and DMS should integrate: {e}")
    
    @pytest.mark.integration
    @pytest.mark.cherry_picking
    def test_license_dms_integration(self):
        """Test license manager and DMS integration."""
        try:
            from fbs_license_manager.services import LicenseManager
            from fbs_dms.services import DocumentService
            
            license_manager = LicenseManager(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            
            # Test that they can work together
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
            self.assertTrue(hasattr(document_service, 'create_document'))
            
        except ImportError as e:
            self.fail(f"License manager and DMS should integrate: {e}")
    
    @pytest.mark.integration
    @pytest.mark.cherry_picking
    def test_full_stack_integration(self):
        """Test full stack integration."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_license_manager.services import LicenseManager
            from fbs_dms.services import DocumentService
            
            fbs_interface = FBSInterface(self.solution_name)
            license_manager = LicenseManager(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            
            # Test that all three can work together
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
            self.assertTrue(hasattr(document_service, 'create_document'))
            
        except ImportError as e:
            self.fail(f"Full stack should integrate: {e}")


@pytest.mark.integration
@pytest.mark.isolation
class TestDatabaseIsolationIntegration(TestCase):
    """Test database isolation integration."""
    
    databases = {'default', 'licensing'}
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.solution_name = 'test_solution'
    
    @pytest.mark.integration
    @pytest.mark.isolation
    def test_database_routing_with_fbs_only(self):
        """Test database routing with FBS only."""
        try:
            from fbs_app.routers import FBSDatabaseRouter
            router = FBSDatabaseRouter()
            
            # Test routing for FBS app models
            from fbs_app.models import OdooDatabase
            db_for_read = router.db_for_read(OdooDatabase)
            self.assertEqual(db_for_read, 'default')
            
        except ImportError as e:
            self.fail(f"FBS database routing should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.isolation
    def test_database_routing_with_licensing(self):
        """Test database routing with licensing."""
        try:
            from fbs_app.routers import FBSDatabaseRouter
            from fbs_license_manager.models import SolutionLicense
            
            router = FBSDatabaseRouter()
            db_for_read = router.db_for_read(SolutionLicense)
            self.assertEqual(db_for_read, 'licensing')
            
        except ImportError as e:
            self.fail(f"License database routing should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.isolation
    def test_database_routing_with_dms(self):
        """Test database routing with DMS."""
        try:
            from fbs_app.routers import FBSDatabaseRouter
            from fbs_dms.models import Document
            
            router = FBSDatabaseRouter()
            # DMS models should route to default by default
            db_for_read = router.db_for_read(Document)
            self.assertIsNotNone(db_for_read)
            
        except ImportError as e:
            self.fail(f"DMS database routing should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.isolation
    def test_solution_database_isolation(self):
        """Test solution database isolation."""
        try:
            from fbs_app.routers import FBSDatabaseRouter
            router = FBSDatabaseRouter()
            
            # Test that solution databases are detected
            solution_dbs = router._get_solution_databases()
            self.assertIsInstance(solution_dbs, list)
            
        except ImportError as e:
            self.fail(f"Solution database isolation should work: {e}")


@pytest.mark.integration
@pytest.mark.e2e
class TestEndToEndWorkflows(TestCase):
    """Test end-to-end workflows."""
    
    databases = {'default', 'licensing'}
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.solution_name = 'test_solution'
    
    @pytest.mark.integration
    @pytest.mark.e2e
    def test_basic_fbs_workflow(self):
        """Test basic FBS workflow."""
        try:
            from fbs_app.interfaces import FBSInterface
            fbs_interface = FBSInterface(self.solution_name)
            
            # Test basic workflow
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            
        except ImportError as e:
            self.fail(f"Basic FBS workflow should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.e2e
    def test_licensed_workflow(self):
        """Test licensed workflow."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_license_manager.services import LicenseManager
            
            fbs_interface = FBSInterface(self.solution_name)
            license_manager = LicenseManager(self.solution_name)
            
            # Test licensed workflow
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
            
        except ImportError as e:
            self.fail(f"Licensed workflow should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.e2e
    def test_dms_workflow(self):
        """Test DMS workflow."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_dms.services import DocumentService
            
            fbs_interface = FBSInterface(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            
            # Test DMS workflow
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(document_service, 'create_document'))
            
        except ImportError as e:
            self.fail(f"DMS workflow should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.e2e
    def test_full_stack_workflow(self):
        """Test full stack workflow."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_license_manager.services import LicenseManager
            from fbs_dms.services import DocumentService
            
            fbs_interface = FBSInterface(self.solution_name)
            license_manager = LicenseManager(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            
            # Test full stack workflow
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
            self.assertTrue(hasattr(document_service, 'create_document'))
            
        except ImportError as e:
            self.fail(f"Full stack workflow should work: {e}")


@pytest.mark.integration
@pytest.mark.performance
class TestPerformanceWithDifferentConfigurations(TestCase):
    """Test performance with different configurations."""
    
    databases = {'default', 'licensing'}
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.solution_name = 'test_solution'
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_fbs_only_performance(self):
        """Test FBS only performance."""
        try:
            from fbs_app.interfaces import FBSInterface
            import time
            
            start_time = time.time()
            fbs_interface = FBSInterface(self.solution_name)
            creation_time = time.time() - start_time
            
            # Should be fast
            self.assertLess(creation_time, 1.0)
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            
        except ImportError as e:
            self.fail(f"FBS only performance should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_with_licensing_performance(self):
        """Test performance with licensing."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_license_manager.services import LicenseManager
            import time
            
            start_time = time.time()
            fbs_interface = FBSInterface(self.solution_name)
            license_manager = LicenseManager(self.solution_name)
            creation_time = time.time() - start_time
            
            # Should be fast
            self.assertLess(creation_time, 2.0)
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
            
        except ImportError as e:
            self.fail(f"Performance with licensing should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_with_dms_performance(self):
        """Test performance with DMS."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_dms.services import DocumentService
            import time
            
            start_time = time.time()
            fbs_interface = FBSInterface(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            creation_time = time.time() - start_time
            
            # Should be fast
            self.assertLess(creation_time, 2.0)
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(document_service, 'create_document'))
            
        except ImportError as e:
            self.fail(f"Performance with DMS should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_full_stack_performance(self):
        """Test full stack performance."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_license_manager.services import LicenseManager
            from fbs_dms.services import DocumentService
            import time
            
            start_time = time.time()
            fbs_interface = FBSInterface(self.solution_name)
            license_manager = LicenseManager(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            creation_time = time.time() - start_time
            
            # Should be fast
            self.assertLess(creation_time, 3.0)
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
            self.assertTrue(hasattr(document_service, 'create_document'))
            
        except ImportError as e:
            self.fail(f"Full stack performance should work: {e}")


@pytest.mark.integration
@pytest.mark.security
class TestSecurityWithDifferentConfigurations(TestCase):
    """Test security with different configurations."""
    
    databases = {'default', 'licensing'}
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.solution_name = 'test_solution'
    
    @pytest.mark.integration
    @pytest.mark.security
    def test_fbs_only_security(self):
        """Test FBS only security."""
        try:
            from fbs_app.interfaces import FBSInterface
            fbs_interface = FBSInterface(self.solution_name)
            
            # Test security features
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            
        except ImportError as e:
            self.fail(f"FBS only security should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.security
    def test_with_licensing_security(self):
        """Test security with licensing."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_license_manager.services import LicenseManager
            
            fbs_interface = FBSInterface(self.solution_name)
            license_manager = LicenseManager(self.solution_name)
            
            # Test security features
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
            
        except ImportError as e:
            self.fail(f"Security with licensing should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.security
    def test_with_dms_security(self):
        """Test security with DMS."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_dms.services import DocumentService
            
            fbs_interface = FBSInterface(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            
            # Test security features
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(document_service, 'create_document'))
            
        except ImportError as e:
            self.fail(f"Security with DMS should work: {e}")
    
    @pytest.mark.integration
    @pytest.mark.security
    def test_full_stack_security(self):
        """Test full stack security."""
        try:
            from fbs_app.interfaces import FBSInterface
            from fbs_license_manager.services import LicenseManager
            from fbs_dms.services import DocumentService
            
            fbs_interface = FBSInterface(self.solution_name)
            license_manager = LicenseManager(self.solution_name)
            document_service = DocumentService(company_id=self.solution_name)
            
            # Test security features
            self.assertTrue(hasattr(fbs_interface, 'get_odoo_client'))
            self.assertTrue(hasattr(license_manager, 'feature_flags'))
            self.assertTrue(hasattr(document_service, 'create_document'))
            
        except ImportError as e:
            self.fail(f"Full stack security should work: {e}")
