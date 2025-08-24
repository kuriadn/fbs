"""
FBS App Business Intelligence Service

Service for comprehensive BI capabilities including analytics, KPI calculations,
report generation, dashboard data aggregation, and performance metrics.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.getLogger('fbs_app')


class BusinessIntelligenceService:
    """Business Intelligence Service"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        self.fbs_config = getattr(settings, 'FBS_APP', {})
    
    # Dashboard Management Methods
    def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dashboard"""
        try:
            from ..models.bi import Dashboard
            
            dashboard = Dashboard.objects.create(
                name=dashboard_data['name'],
                dashboard_type=dashboard_data.get('dashboard_type', 'general'),
                description=dashboard_data.get('description', ''),
                is_active=dashboard_data.get('is_active', True),
                created_by=dashboard_data.get('created_by')
            )
            
            return {
                'success': True,
                'data': {
                    'id': dashboard.id,
                    'name': dashboard.name,
                    'dashboard_type': dashboard.dashboard_type,
                    'description': dashboard.description,
                    'is_active': dashboard.is_active
                }
            }
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_dashboards(self, dashboard_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all dashboards or by type"""
        try:
            from ..models.bi import Dashboard
            
            query = {'is_active': True}
            if dashboard_type:
                query['dashboard_type'] = dashboard_type
            
            dashboards = Dashboard.objects.filter(**query)
            dashboard_list = []
            
            for dashboard in dashboards:
                dashboard_list.append({
                    'id': dashboard.id,
                    'name': dashboard.name,
                    'dashboard_type': dashboard.dashboard_type,
                    'description': dashboard.description,
                    'is_active': dashboard.is_active,
                    'created_at': dashboard.created_at.isoformat()
                })
            
            return {
                'success': True,
                'data': dashboard_list,
                'count': len(dashboard_list)
            }
        except Exception as e:
            logger.error(f"Error getting dashboards: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_dashboard(self, dashboard_id: int, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update dashboard"""
        try:
            from ..models.bi import Dashboard
            
            dashboard = Dashboard.objects.get(id=dashboard_id)
            
            # Update only provided fields
            for field, value in dashboard_data.items():
                if hasattr(dashboard, field) and field not in ['id', 'created_at']:
                    setattr(dashboard, field, value)
            
            dashboard.save()
            
            return {
                'success': True,
                'data': {
                    'id': dashboard.id,
                    'name': dashboard.name,
                    'dashboard_type': dashboard.dashboard_type,
                    'description': dashboard.description,
                    'is_active': dashboard.is_active
                }
            }
        except Dashboard.DoesNotExist:
            return {'success': False, 'error': 'Dashboard not found'}
        except Exception as e:
            logger.error(f"Error updating dashboard: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        """Delete dashboard"""
        try:
            from ..models.bi import Dashboard
            
            dashboard = Dashboard.objects.get(id=dashboard_id)
            dashboard.delete()
            
            return {
                'success': True,
                'message': f'Dashboard {dashboard_id} deleted successfully'
            }
        except Dashboard.DoesNotExist:
            return {'success': False, 'error': 'Dashboard not found'}
        except Exception as e:
            logger.error(f"Error deleting dashboard: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Report Management Methods
    def create_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report"""
        try:
            from ..models.bi import Report
            
            report = Report.objects.create(
                name=report_data['name'],
                report_type=report_data.get('report_type', 'general'),
                description=report_data.get('description', ''),
                is_active=report_data.get('is_active', True),
                created_by=report_data.get('created_by', 1)
            )
            
            return {
                'success': True,
                'data': {
                    'id': report.id,
                    'name': report.name,
                    'report_type': report.report_type,
                    'description': report.description,
                    'is_active': report.is_active
                }
            }
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_reports(self, report_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all reports or by type"""
        try:
            from ..models.bi import Report
            
            query = {'is_active': True}
            if report_type:
                query['report_type'] = report_type
            
            reports = Report.objects.filter(**query)
            report_list = []
            
            for report in reports:
                report_list.append({
                    'id': report.id,
                    'name': report.name,
                    'report_type': report.report_type,
                    'description': report.description,
                    'is_active': report.is_active,
                    'created_at': report.created_at.isoformat()
                })
            
            return {
                'success': True,
                'data': report_list,
                'count': len(report_list)
            }
        except Exception as e:
            logger.error(f"Error getting reports: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_report(self, report_id: int, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate report with parameters"""
        try:
            from ..models.bi import Report
            
            report = Report.objects.get(id=report_id)
            params = parameters or {}
            
            # Route to appropriate report generator based on type
            if report.report_type == 'sales':
                return self.generate_sales_report(
                    token=params.get('token', ''),
                    database=params.get('database', ''),
                    period=params.get('period', 'month'),
                    date_from=params.get('date_from'),
                    date_to=params.get('date_to')
                )
            elif report.report_type == 'inventory':
                return self.generate_inventory_report(
                    token=params.get('token', ''),
                    database=params.get('database', '')
                )
            elif report.report_type == 'customer':
                return self.generate_customer_report(
                    token=params.get('token', ''),
                    database=params.get('database', ''),
                    period=params.get('period', 'month')
                )
            else:
                return {
                    'success': False,
                    'error': f'Unknown report type: {report.report_type}'
                }
                
        except Report.DoesNotExist:
            return {'success': False, 'error': 'Report not found'}
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # KPI Management Methods
    def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new KPI"""
        try:
            from ..models.bi import KPI
            
            kpi = KPI.objects.create(
                name=kpi_data['name'],
                kpi_type=kpi_data.get('kpi_type', 'general'),
                description=kpi_data.get('description', ''),
                calculation_method=kpi_data.get('calculation_method', 'sum'),
                data_source=kpi_data.get('data_source', 'default'),
                target_value=kpi_data.get('target_value'),
                warning_threshold=kpi_data.get('warning_threshold'),
                critical_threshold=kpi_data.get('critical_threshold'),
                unit=kpi_data.get('unit', ''),
                frequency=kpi_data.get('frequency', 'daily'),
                is_active=kpi_data.get('is_active', True),
                created_by=kpi_data.get('created_by', 1)
            )
            
            return {
                'success': True,
                'data': {
                    'id': kpi.id,
                    'name': kpi.name,
                    'kpi_type': kpi.kpi_type,
                    'description': kpi.description,
                    'is_active': kpi.is_active
                }
            }
        except Exception as e:
            logger.error(f"Error creating KPI: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_kpis(self, kpi_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all KPIs or by type"""
        try:
            from ..models.bi import KPI
            
            query = {'is_active': True}
            if kpi_type:
                query['kpi_type'] = kpi_type
            
            kpis = KPI.objects.filter(**query)
            kpi_list = []
            
            for kpi in kpis:
                kpi_list.append({
                    'id': kpi.id,
                    'name': kpi.name,
                    'kpi_type': kpi.kpi_type,
                    'description': kpi.description,
                    'is_active': kpi.is_active,
                    'created_at': kpi.created_at.isoformat()
                })
            
            return {
                'success': True,
                'data': kpi_list,
                'count': len(kpi_list)
            }
        except Exception as e:
            logger.error(f"Error getting KPIs: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def calculate_kpi(self, kpi_id: int) -> Dict[str, Any]:
        """Calculate KPI value"""
        try:
            from ..models.bi import KPI
            
            kpi = KPI.objects.get(id=kpi_id)
            
            # Route to appropriate KPI calculator based on type
            if kpi.kpi_type == 'sales':
                return self._calculate_sales_kpis(None, '', '')
            elif kpi.kpi_type == 'inventory':
                return self._calculate_inventory_kpis(None, '', '')
            elif kpi.kpi_type == 'customer':
                return self._calculate_customer_kpis(None, '', '')
            else:
                return {
                    'success': False,
                    'error': f'Unknown KPI type: {kpi.kpi_type}'
                }
                
        except KPI.DoesNotExist:
            return {'success': False, 'error': 'KPI not found'}
        except Exception as e:
            logger.error(f"Error calculating KPI: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Chart Management Methods
    def create_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chart"""
        try:
            from ..models.bi import Chart
            
            chart = Chart.objects.create(
                name=chart_data['name'],
                chart_type=chart_data.get('chart_type', 'bar'),
                data_source=chart_data.get('data_source', 'default'),
                description=chart_data.get('description', ''),
                configuration=chart_data.get('configuration', {}),
                is_active=chart_data.get('is_active', True),
                created_by=chart_data.get('created_by', 1)
            )
            
            return {
                'success': True,
                'data': {
                    'id': chart.id,
                    'name': chart.name,
                    'chart_type': chart.chart_type,
                    'data_source': chart.data_source,
                    'description': chart.description,
                    'is_active': chart.is_active
                }
            }
        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_charts(self, chart_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all charts or by type"""
        try:
            from ..models.bi import Chart
            
            query = {'is_active': True}
            if chart_type:
                query['chart_type'] = chart_type
            
            charts = Chart.objects.filter(**query)
            chart_list = []
            
            for chart in charts:
                chart_list.append({
                    'id': chart.id,
                    'name': chart.name,
                    'chart_type': chart.chart_type,
                    'data_source': chart.data_source,
                    'description': chart.description,
                    'is_active': chart.is_active,
                    'created_at': chart.created_at.isoformat()
                })
            
            return {
                'success': True,
                'data': chart_list,
                'count': len(chart_list)
            }
        except Exception as e:
            logger.error(f"Error getting charts: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Enhanced Analytics Data Method
    def get_analytics_data(self, data_source: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get analytics data from various sources"""
        try:
            # Route to appropriate data source
            if data_source == 'sales':
                return self._get_sales_analytics(filters)
            elif data_source == 'inventory':
                return self._get_inventory_analytics(filters)
            elif data_source == 'customer':
                return self._get_customer_analytics(filters)
            else:
                return {
                    'success': False,
                    'error': f'Unknown data source: {data_source}'
                }
        except Exception as e:
            logger.error(f"Error getting analytics data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Helper methods for analytics data
    def _get_sales_analytics(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get sales analytics data"""
        # Simple implementation - can be enhanced later
        return {
            'success': True,
            'data': {
                'total_sales': 0,
                'orders_count': 0,
                'average_order_value': 0
            }
        }
    
    def _get_inventory_analytics(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get inventory analytics data"""
        # Simple implementation - can be enhanced later
        return {
            'success': True,
            'data': {
                'total_products': 0,
                'total_value': 0,
                'low_stock_count': 0
            }
        }
    
    def _get_customer_analytics(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get customer analytics data"""
        # Simple implementation - can be enhanced later
        return {
            'success': True,
            'data': {
                'total_customers': 0,
                'active_customers': 0,
                'new_customers': 0
            }
        }

    # Existing methods (keeping for backward compatibility)
    def get_analytics_data(self, model_name: str, token: str, database: str,
                          report_type: str = 'summary', filters: Dict = None,
                          group_by: List = None, measures: List = None,
                          date_range: Dict = None) -> Dict[str, Any]:
        """Get analytics data for a model"""
        try:
            from .odoo_client import OdooClient
            
            odoo_client = OdooClient()
            
            # Build analytics request
            analytics_request = {
                'model': model_name,
                'report_type': report_type,
                'filters': filters or {},
                'group_by': group_by or [],
                'measures': measures or [],
                'date_range': date_range or {}
            }
            
            # Get data from Odoo
            result = odoo_client.get_analytics_data(
                model_name=model_name,
                token=token,
                database=database,
                report_type=report_type,
                filters=filters,
                group_by=group_by,
                measures=measures
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting analytics data: {str(e)}")
            return {
                'success': False,
                'error': str(e)}
    
    def generate_sales_report(self, token: str, database: str, 
                            period: str = 'month', date_from: str = None,
                            date_to: str = None) -> Dict[str, Any]:
        """Generate comprehensive sales report"""
        try:
            from .odoo_client import OdooClient
            
            odoo_client = OdooClient()
            
            # Calculate date range
            if not date_from or not date_to:
                date_from, date_to = self._calculate_date_range(period)
            
            # Get sales orders
            sales_data = odoo_client.list_records(
                model_name='sale.order',
                token=token,
                database=database,
                domain=[
                    ('date_order', '>=', date_from),
                    ('date_order', '<=', date_to),
                    ('state', 'in', ['sale', 'done'])
                ],
                fields=['id', 'name', 'partner_id', 'amount_total', 'date_order', 'state']
            )
            
            if not sales_data['success']:
                return sales_data
            
            # Calculate metrics
            total_sales = sum(order['amount_total'] for order in sales_data.get('data', []))
            orders_count = len(sales_data.get('data', []))
            average_order_value = total_sales / orders_count if orders_count > 0 else 0
            
            # Growth calculation
            previous_date_from, previous_date_to = self._calculate_previous_period(date_from, date_to)
            
            previous_sales_data = odoo_client.list_records(
                model_name='sale.order',
                token=token,
                database=database,
                domain=[
                    ('date_order', '>=', previous_date_from),
                    ('date_order', '<=', previous_date_to),
                    ('state', 'in', ['sale', 'done'])
                ],
                fields=['amount_total']
            )
            
            previous_total_sales = sum(order['amount_total'] for order in previous_sales_data.get('data', []))
            growth_rate = ((total_sales - previous_total_sales) / previous_total_sales * 100) if previous_total_sales > 0 else 0
            
            return {
                'success': True,
                'report': {
                    'period': period,
                    'date_from': date_from,
                    'date_to': date_to,
                    'total_sales': total_sales,
                    'orders_count': orders_count,
                    'average_order_value': average_order_value,
                    'growth_rate': growth_rate,
                    'previous_period_sales': previous_total_sales
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating sales report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_inventory_report(self, token: str, database: str) -> Dict[str, Any]:
        """Generate comprehensive inventory report"""
        try:
            from .odoo_client import OdooClient
            
            odoo_client = OdooClient()
            
            # Get products
            products_data = odoo_client.list_records(
                model_name='product.product',
                token=token,
                database=database,
                fields=['id', 'name', 'qty_available', 'list_price', 'default_code', 'categ_id']
            )
            
            if not products_data['success']:
                return products_data
            
            products = products_data.get('data', [])
            
            # Calculate metrics
            total_products = len(products)
            total_value = sum(product.get('list_price', 0) * product.get('qty_available', 0) for product in products)
            low_stock_count = len([p for p in products if p.get('qty_available', 0) < 10])
            out_of_stock_count = len([p for p in products if p.get('qty_available', 0) <= 0])
            
            # Category breakdown
            categories = {}
            for product in products:
                category_name = product.get('categ_id', ['', 'Uncategorized'])[1]
                if category_name not in categories:
                    categories[category_name] = {'count': 0, 'value': 0}
                categories[category_name]['count'] += 1
                categories[category_name]['value'] += product.get('list_price', 0) * product.get('qty_available', 0)
            
            return {
                'success': True,
                'report': {
                    'total_products': total_products,
                    'total_inventory_value': total_value,
                    'low_stock_count': low_stock_count,
                    'out_of_stock_count': out_of_stock_count,
                    'low_stock_percentage': (low_stock_count / total_products * 100) if total_products > 0 else 0,
                    'categories': categories
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating inventory report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_customer_report(self, token: str, database: str, 
                               period: str = 'month') -> Dict[str, Any]:
        """Generate comprehensive customer report"""
        try:
            from .odoo_client import OdooClient
            
            odoo_client = OdooClient()
            
            # Calculate date range
            date_from, date_to = self._calculate_date_range(period)
            
            # Get customers
            customers_data = odoo_client.list_records(
                model_name='res.partner',
                token=token,
                database=database,
                domain=[
                    ('customer', '=', True),
                    ('create_date', '>=', date_from),
                    ('create_date', '<=', date_to)
                ],
                fields=['id', 'name', 'email', 'phone', 'create_date', 'customer_rank']
            )
            
            if not customers_data['success']:
                return customers_data
            
            customers = customers_data.get('data', [])
            
            # Calculate customer metrics
            total_customers = len(customers)
            new_customers = len([c for c in customers if c.get('create_date', '') >= date_from])
            active_customers = len([c for c in customers if c.get('customer_rank', 0) > 0])
            
            return {
                'success': True,
                'report': {
                    'period': period,
                    'total_customers': total_customers,
                    'new_customers': new_customers,
                    'active_customers': active_customers,
                    'customer_growth_rate': (new_customers / total_customers * 100) if total_customers > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating customer report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_kpi_metrics(self, token: str, database: str, kpi_type: str = 'all') -> Dict[str, Any]:
        """Get KPI metrics for the business"""
        try:
            from .odoo_client import OdooClient
            
            odoo_client = OdooClient()
            
            kpis = {}
            
            if kpi_type in ['all', 'sales']:
                # Sales KPIs
                sales_kpis = self._calculate_sales_kpis(odoo_client, token, database)
                kpis['sales'] = sales_kpis
            
            if kpi_type in ['all', 'inventory']:
                # Inventory KPIs
                inventory_kpis = self._calculate_inventory_kpis(odoo_client, token, database)
                kpis['inventory'] = inventory_kpis
            
            if kpi_type in ['all', 'customers']:
                # Customer KPIs
                customer_kpis = self._calculate_customer_kpis(odoo_client, token, database)
                kpis['customers'] = customer_kpis
            
            return {
                'success': True,
                'kpis': kpis,
                'calculation_date': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting KPI metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_date_range(self, period: str) -> tuple:
        """Calculate date range for the specified period"""
        end_date = timezone.now().date()
        
        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'quarter':
            start_date = end_date - timedelta(days=90)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        return start_date.isoformat(), end_date.isoformat()
    
    def _calculate_previous_period(self, date_from: str, date_to: str) -> tuple:
        """Calculate previous period dates"""
        start_date = datetime.fromisoformat(date_from)
        end_date = datetime.fromisoformat(date_to)
        period_duration = end_date - start_date
        
        previous_end_date = start_date
        previous_start_date = previous_end_date - period_duration
        
        return previous_start_date.isoformat(), previous_end_date.isoformat()
    
    def _calculate_sales_kpis(self, odoo_client, token: str, database: str) -> Dict[str, Any]:
        """Calculate sales KPIs"""
        try:
            # Get current month sales
            current_month = timezone.now().replace(day=1)
            current_month_str = current_month.strftime('%Y-%m-%d')
            
            sales_data = odoo_client.list_records(
                model_name='sale.order',
                token=token,
                database=database,
                domain=[
                    ('date_order', '>=', current_month_str),
                    ('state', 'in', ['sale', 'done'])
                ],
                fields=['amount_total']
            )
            
            if not sales_data['success']:
                return {}
            
            current_month_sales = sum(order['amount_total'] for order in sales_data.get('data', []))
            
            # Get previous month sales
            previous_month = current_month - timedelta(days=1)
            previous_month = previous_month.replace(day=1)
            previous_month_str = previous_month.strftime('%Y-%m-%d')
            
            previous_sales_data = odoo_client.list_records(
                model_name='sale.order',
                token=token,
                database=database,
                domain=[
                    ('date_order', '>=', previous_month_str),
                    ('date_order', '<', current_month_str),
                    ('state', 'in', ['sale', 'done'])
                ],
                fields=['amount_total']
            )
            
            previous_month_sales = sum(order['amount_total'] for order in previous_sales_data.get('data', []))
            
            # Calculate growth
            growth_rate = ((current_month_sales - previous_month_sales) / previous_month_sales * 100) if previous_month_sales > 0 else 0
            
            return {
                'current_month_sales': current_month_sales,
                'previous_month_sales': previous_month_sales,
                'growth_rate': growth_rate
            }
            
        except Exception as e:
            logger.error(f"Error calculating sales KPIs: {str(e)}")
            return {}
    
    def _calculate_inventory_kpis(self, odoo_client, token: str, database: str) -> Dict[str, Any]:
        """Calculate inventory KPIs"""
        try:
            products_data = odoo_client.list_records(
                model_name='product.product',
                token=token,
                database=database,
                fields=['qty_available', 'list_price']
            )
            
            if not products_data['success']:
                return {}
            
            products = products_data.get('data', [])
            
            total_products = len(products)
            total_value = sum(product.get('list_price', 0) * product.get('qty_available', 0) for product in products)
            low_stock_count = len([p for p in products if p.get('qty_available', 0) < 10])
            
            return {
                'total_products': total_products,
                'total_inventory_value': total_value,
                'low_stock_count': low_stock_count,
                'low_stock_percentage': (low_stock_count / total_products * 100) if total_products > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating inventory KPIs: {str(e)}")
            return {}
    
    def _calculate_customer_kpis(self, odoo_client, token: str, database: str) -> Dict[str, Any]:
        """Calculate customer KPIs"""
        try:
            customers_data = odoo_client.list_records(
                model_name='res.partner',
                token=token,
                database=database,
                domain=[('customer', '=', True)],
                fields=['create_date', 'customer_rank']
            )
            
            if not customers_data['success']:
                return {}
            
            customers = customers_data.get('data', [])
            
            total_customers = len(customers)
            active_customers = len([c for c in customers if c.get('customer_rank', 0) > 0])
            
            # Calculate new customers this month
            current_month = timezone.now().replace(day=1)
            current_month_str = current_month.strftime('%Y-%m-%d')
            
            new_customers = len([c for c in customers if c.get('create_date', '') >= current_month_str])
            
            return {
                'total_customers': total_customers,
                'active_customers': active_customers,
                'new_customers_this_month': new_customers,
                'active_customer_percentage': (active_customers / total_customers * 100) if total_customers > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating customer KPIs: {str(e)}")
            return {}
