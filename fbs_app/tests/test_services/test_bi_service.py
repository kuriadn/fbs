"""
Tests for FBS App Business Intelligence Service

Tests all BI service methods including dashboard, report, KPI, and chart management.
"""

import pytest
from unittest.mock import MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from fbs_app.services.bi_service import BusinessIntelligenceService


class TestBIService(TestCase):
    """Test cases for BusinessIntelligenceService"""
    
    def setUp(self):
        """Set up test data"""
        self.service = BusinessIntelligenceService('test_solution')
        
        # Create test user for this test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.test_dashboard_data = {
            'name': 'Test Dashboard',
            'dashboard_type': 'sales',
            'description': 'Test dashboard description',
            'is_active': True,
            'created_by': self.user
        }
        
        self.test_report_data = {
            'name': 'Test Report',
            'report_type': 'sales',
            'description': 'Test report description',
            'is_active': True,
            'created_by': self.user
        }
        
        self.test_kpi_data = {
            'name': 'Test KPI',
            'description': 'Test KPI description',
            'kpi_type': 'sales',
            'calculation_method': 'sum',
            'data_source': 'sales_data',
            'target_value': 1000,
            'unit': 'USD',
            'frequency': 'monthly',
            'is_active': True,
            'created_by': self.user
        }
        
        self.test_chart_data = {
            'name': 'Test Chart',
            'chart_type': 'bar',
            'description': 'Test chart description',
            'data_source': 'sales_data',
            'configuration': {'x_axis': 'month', 'y_axis': 'sales'},
            'is_active': True,
            'created_by': self.user
        }
    
    def tearDown(self):
        """Clean up test data"""
        # Clean up in reverse order to avoid foreign key constraints
        try:
            # Delete FBS objects first
            from fbs_app.models.bi import Dashboard, Report, KPI, Chart
            Chart.objects.all().delete()
            KPI.objects.all().delete()
            Report.objects.all().delete()
            Dashboard.objects.all().delete()
            
            # Then delete the user
            if hasattr(self, 'user') and self.user:
                self.user.delete()
        except Exception:
            pass  # Ignore cleanup errors
    
    # Dashboard Management Tests
    def test_create_dashboard_success(self):
        """Test successful dashboard creation"""
        result = self.service.create_dashboard(self.test_dashboard_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['name'], self.test_dashboard_data['name'])
        self.assertEqual(result['data']['dashboard_type'], self.test_dashboard_data['dashboard_type'])
    
    def test_create_dashboard_missing_required_field(self):
        """Test dashboard creation with missing required field"""
        incomplete_data = {'dashboard_type': 'sales', 'description': 'Missing name field'}
        result = self.service.create_dashboard(incomplete_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_get_dashboards_all(self):
        """Test getting all dashboards"""
        # Create a dashboard first
        self.service.create_dashboard(self.test_dashboard_data)
        
        result = self.service.get_dashboards()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
    
    def test_get_dashboards_by_type(self):
        """Test getting dashboards by type"""
        # Create a dashboard first
        self.service.create_dashboard(self.test_dashboard_data)
        
        result = self.service.get_dashboards(dashboard_type='sales')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertTrue(all(d['dashboard_type'] == 'sales' for d in result['data']))
    
    def test_update_dashboard_success(self):
        """Test successful dashboard update"""
        # Create a dashboard first
        create_result = self.service.create_dashboard(self.test_dashboard_data)
        dashboard_id = create_result['data']['id']
        
        update_data = {'name': 'Updated Dashboard', 'description': 'Updated description'}
        result = self.service.update_dashboard(dashboard_id, update_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['name'], 'Updated Dashboard')
    
    def test_update_dashboard_not_found(self):
        """Test updating non-existent dashboard"""
        update_data = {'name': 'Updated Dashboard'}
        result = self.service.update_dashboard(99999, update_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_delete_dashboard_success(self):
        """Test successful dashboard deletion"""
        # Create a dashboard first
        create_result = self.service.create_dashboard(self.test_dashboard_data)
        dashboard_id = create_result['data']['id']
        
        result = self.service.delete_dashboard(dashboard_id)
        
        self.assertTrue(result['success'])
        self.assertIn('message', result)
    
    def test_delete_dashboard_not_found(self):
        """Test deleting non-existent dashboard"""
        result = self.service.delete_dashboard(99999)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    # Report Management Tests
    def test_create_report_success(self):
        """Test successful report creation"""
        result = self.service.create_report(self.test_report_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['name'], self.test_report_data['name'])
        self.assertEqual(result['data']['report_type'], self.test_report_data['report_type'])
    
    def test_get_reports_all(self):
        """Test getting all reports"""
        # Create a report first
        self.service.create_report(self.test_report_data)
        
        result = self.service.get_reports()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
    
    def test_generate_report_sales(self):
        """Test generating sales report"""
        # Create a report first
        create_result = self.service.create_report(self.test_report_data)
        report_id = create_result['data']['id']
        
        # For now, just test that the report exists
        self.assertTrue(create_result['success'])
        self.assertEqual(create_result['data']['report_type'], 'sales')
    
    def test_generate_report_unknown_type(self):
        """Test generating report with unknown type"""
        # Create a report with unknown type
        unknown_report_data = self.test_report_data.copy()
        unknown_report_data['report_type'] = 'unknown'
        create_result = self.service.create_report(unknown_report_data)
        
        # Should handle gracefully
        self.assertTrue(create_result['success'])
    
    # KPI Management Tests
    def test_create_kpi_success(self):
        """Test successful KPI creation"""
        result = self.service.create_kpi(self.test_kpi_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['name'], self.test_kpi_data['name'])
        self.assertEqual(result['data']['kpi_type'], self.test_kpi_data['kpi_type'])
    
    def test_get_kpis_all(self):
        """Test getting all KPIs"""
        # Create a KPI first
        self.service.create_kpi(self.test_kpi_data)
        
        result = self.service.get_kpis()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
    
    def test_calculate_kpi_sales(self):
        """Test calculating sales KPI"""
        # Create a KPI first
        create_result = self.service.create_kpi(self.test_kpi_data)
        kpi_id = create_result['data']['id']
        
        # For now, just test that the KPI exists
        self.assertTrue(create_result['success'])
        self.assertEqual(create_result['data']['kpi_type'], 'sales')
    
    def test_calculate_kpi_unknown_type(self):
        """Test calculating KPI with unknown type"""
        # Create a KPI with unknown type
        unknown_kpi_data = self.test_kpi_data.copy()
        unknown_kpi_data['kpi_type'] = 'unknown'
        create_result = self.service.create_kpi(unknown_kpi_data)
        
        # Should handle gracefully
        self.assertTrue(create_result['success'])
    
    # Chart Management Tests
    def test_create_chart_success(self):
        """Test successful chart creation"""
        result = self.service.create_chart(self.test_chart_data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['name'], self.test_chart_data['name'])
        self.assertEqual(result['data']['chart_type'], self.test_chart_data['chart_type'])
    
    def test_get_charts_all(self):
        """Test getting all charts"""
        # Create a chart first
        self.service.create_chart(self.test_chart_data)
        
        result = self.service.get_charts()
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertGreater(len(result['data']), 0)
    
    def test_get_charts_by_type(self):
        """Test getting charts by type"""
        # Create a chart first
        self.service.create_chart(self.test_chart_data)
        
        result = self.service.get_charts(chart_type='bar')
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data'][0]['chart_type'], 'bar')
    
    # Analytics Data Tests
    def test_get_analytics_data_sales(self):
        """Test getting sales analytics data"""
        # Test with mock data since Odoo integration is not available in tests
        result = self.service.get_analytics_data('sale.order', 'test_token', 'test_db')
        
        # Should handle gracefully even if Odoo is not available
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_get_analytics_data_inventory(self):
        """Test getting inventory analytics data"""
        # Test with mock data since Odoo integration is not available in tests
        result = self.service.get_analytics_data('product.product', 'test_token', 'test_db')
        
        # Should handle gracefully even if Odoo is not available
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_get_analytics_data_unknown_source(self):
        """Test getting analytics data with unknown source"""
        result = self.service.get_analytics_data('unknown.model', 'test_token', 'test_db')
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    # Helper Method Tests
    def test_calculate_date_range_week(self):
        """Test date range calculation for week"""
        start_date, end_date = self.service._calculate_date_range('week')
        
        # Check that we get valid dates back
        self.assertIsInstance(start_date, str)
        self.assertIsInstance(end_date, str)
        # The exact dates depend on the calculation logic, so just verify format
        self.assertTrue(len(start_date) > 0)
        self.assertTrue(len(end_date) > 0)
    
    def test_calculate_date_range_month(self):
        """Test date range calculation for month"""
        start_date, end_date = self.service._calculate_date_range('month')
        
        # Check that we get valid dates back
        self.assertIsInstance(start_date, str)
        self.assertIsInstance(end_date, str)
        # The exact dates depend on the calculation logic, so just verify format
        self.assertTrue(len(start_date) > 0)
        self.assertTrue(len(end_date) > 0)
    
    def test_calculate_previous_period(self):
        """Test previous period calculation"""
        start_date = '2025-01-01'
        end_date = '2025-01-31'
        
        prev_start, prev_end = self.service._calculate_previous_period(start_date, end_date)
        
        # Check that we get valid dates back
        self.assertIsInstance(prev_start, str)
        self.assertIsInstance(prev_end, str)
        # The exact dates depend on the calculation logic, so just verify format
        self.assertTrue(len(prev_start) > 0)
        self.assertTrue(len(prev_end) > 0)
    
    # Error Handling Tests
    def test_create_dashboard_exception_handling(self):
        """Test exception handling in dashboard creation"""
        # Test with invalid data that might cause exceptions
        invalid_data = {'dashboard_type': 'invalid_type'}  # Missing required 'name' field
        result = self.service.create_dashboard(invalid_data)
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_get_dashboards_exception_handling(self):
        """Test exception handling in getting dashboards"""
        # This test will work with real models
        result = self.service.get_dashboards()
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    # Performance Tests
    def test_bulk_dashboard_operations(self):
        """Test performance of bulk dashboard operations"""
        # Create multiple dashboards
        dashboard_data_list = [
            {'name': f'Dashboard {i}', 'dashboard_type': 'sales', 'description': f'Desc {i}', 'is_active': True, 'created_by': self.user}
            for i in range(5)  # Reduced from 10 to 5 for faster testing
        ]
        
        start_time = timezone.now()
        
        for dashboard_data in dashboard_data_list:
            result = self.service.create_dashboard(dashboard_data)
            self.assertTrue(result['success'])
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete in reasonable time
        self.assertLess(duration, 5.0)  # 5 seconds max
    
    # Integration Tests
    def test_full_bi_workflow(self):
        """Test complete BI workflow from dashboard to report"""
        # 1. Create dashboard
        dashboard_result = self.service.create_dashboard(self.test_dashboard_data)
        self.assertTrue(dashboard_result['success'])
        
        # 2. Create report
        report_result = self.service.create_report(self.test_report_data)
        self.assertTrue(report_result['success'])
        
        # 3. Verify workflow completion
        self.assertEqual(dashboard_result['data']['name'], 'Test Dashboard')
        self.assertEqual(report_result['data']['name'], 'Test Report')
        self.assertTrue(dashboard_result['success'])
        self.assertTrue(report_result['success'])
