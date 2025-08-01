"""
Business Intelligence Service

Provides comprehensive BI capabilities including:
- Analytics and KPI calculations
- Report generation and scheduling
- Dashboard data aggregation
- Data visualization support
- Performance metrics
"""

from typing import Dict, Any, List, Optional, Union
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .odoo_client import odoo_client
from .cache_service import CacheService
import logging
import json

logger = logging.getLogger('fayvad_core.bi')


class BIService:
    """
    Business Intelligence Service
    """
    
    def __init__(self):
        self.odoo_client = odoo_client
        self.cache = CacheService()
    
    def get_analytics_data(self, model_name: str, token: str, database: str,
                          report_type: str = 'summary', filters: Dict = None,
                          group_by: List = None, measures: List = None,
                          date_range: Dict = None) -> Dict[str, Any]:
        """
        Get analytics data for a model
        """
        try:
            # Build analytics request
            analytics_request = {
                'model': model_name,
                'report_type': report_type,
                'filters': filters or {},
                'group_by': group_by or [],
                'measures': measures or [],
                'date_range': date_range or {}
            }
            
            # Check cache first
            cache_key = f"analytics:{database}:{model_name}:{hash(json.dumps(analytics_request, sort_keys=True))}"
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Get data from Odoo
            result = self.odoo_client.get_analytics_data(
                model_name=model_name,
                token=token,
                database=database,
                report_type=report_type,
                filters=filters,
                group_by=group_by,
                measures=measures
            )
            
            # Cache result for 5 minutes
            self.cache.set(cache_key, result, timeout=300)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting analytics data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_sales_report(self, token: str, database: str, 
                            period: str = 'month', date_from: str = None,
                            date_to: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive sales report
        """
        try:
            # Calculate date range
            if not date_from or not date_to:
                date_from, date_to = self._calculate_date_range(period)
            
            # Get sales orders
            sales_data = self.odoo_client.list_records(
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
            
            # Get order lines for product analysis
            order_ids = [order['id'] for order in sales_data.get('data', [])]
            
            if order_ids:
                order_lines = self.odoo_client.list_records(
                    model_name='sale.order.line',
                    token=token,
                    database=database,
                    domain=[('order_id', 'in', order_ids)],
                    fields=['product_id', 'product_uom_qty', 'price_subtotal', 'order_id']
                )
            else:
                order_lines = {'data': []}
            
            # Calculate metrics
            total_sales = sum(order['amount_total'] for order in sales_data.get('data', []))
            orders_count = len(sales_data.get('data', []))
            average_order_value = total_sales / orders_count if orders_count > 0 else 0
            
            # Product performance
            product_sales = {}
            for line in order_lines.get('data', []):
                product_id = line.get('product_id', [0, 'Unknown'])[1]
                if product_id not in product_sales:
                    product_sales[product_id] = 0
                product_sales[product_id] += line.get('price_subtotal', 0)
            
            top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Customer analysis
            customer_sales = {}
            for order in sales_data.get('data', []):
                customer = order.get('partner_id', [0, 'Unknown'])[1]
                if customer not in customer_sales:
                    customer_sales[customer] = 0
                customer_sales[customer] += order.get('amount_total', 0)
            
            top_customers = sorted(customer_sales.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Daily sales trend
            daily_sales = {}
            for order in sales_data.get('data', []):
                date = order.get('date_order', '')[:10]  # YYYY-MM-DD
                if date not in daily_sales:
                    daily_sales[date] = 0
                daily_sales[date] += order.get('amount_total', 0)
            
            # Growth calculation (compare with previous period)
            previous_date_from, previous_date_to = self._calculate_previous_period(date_from, date_to)
            
            previous_sales_data = self.odoo_client.list_records(
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
            
            previous_total = sum(order['amount_total'] for order in previous_sales_data.get('data', []))
            growth_rate = ((total_sales - previous_total) / previous_total * 100) if previous_total > 0 else 0
            
            return {
                'success': True,
                'report': {
                    'period': period,
                    'date_from': date_from,
                    'date_to': date_to,
                    'summary': {
                        'total_sales': total_sales,
                        'orders_count': orders_count,
                        'average_order_value': average_order_value,
                        'growth_rate': growth_rate
                    },
                    'top_products': [
                        {'name': name, 'sales': sales}
                        for name, sales in top_products
                    ],
                    'top_customers': [
                        {'name': name, 'sales': sales}
                        for name, sales in top_customers
                    ],
                    'daily_trend': [
                        {'date': date, 'sales': sales}
                        for date, sales in sorted(daily_sales.items())
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating sales report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_inventory_report(self, token: str, database: str) -> Dict[str, Any]:
        """
        Generate inventory analysis report
        """
        try:
            # Get product data
            products = self.odoo_client.list_records(
                model_name='product.product',
                token=token,
                database=database,
                domain=[('type', '=', 'product')],
                fields=['id', 'name', 'qty_available', 'virtual_available', 'standard_price', 'list_price']
            )
            
            # Get stock moves for movement analysis
            stock_moves = self.odoo_client.list_records(
                model_name='stock.move',
                token=token,
                database=database,
                domain=[
                    ('date', '>=', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')),
                    ('state', '=', 'done')
                ],
                fields=['product_id', 'product_uom_qty', 'location_id', 'location_dest_id', 'date']
            )
            
            # Calculate metrics
            total_products = len(products.get('data', []))
            total_value = sum(
                product.get('qty_available', 0) * product.get('standard_price', 0)
                for product in products.get('data', [])
            )
            
            # Low stock products (less than 10 units)
            low_stock_products = [
                product for product in products.get('data', [])
                if product.get('qty_available', 0) < 10
            ]
            
            # Out of stock products
            out_of_stock_products = [
                product for product in products.get('data', [])
                if product.get('qty_available', 0) <= 0
            ]
            
            # Most active products (by movement)
            product_movements = {}
            for move in stock_moves.get('data', []):
                product_id = move.get('product_id', [0, 'Unknown'])[1]
                if product_id not in product_movements:
                    product_movements[product_id] = 0
                product_movements[product_id] += abs(move.get('product_uom_qty', 0))
            
            most_active_products = sorted(product_movements.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'success': True,
                'report': {
                    'summary': {
                        'total_products': total_products,
                        'total_inventory_value': total_value,
                        'low_stock_count': len(low_stock_products),
                        'out_of_stock_count': len(out_of_stock_products)
                    },
                    'low_stock_products': [
                        {
                            'name': product.get('name', 'Unknown'),
                            'quantity': product.get('qty_available', 0),
                            'value': product.get('qty_available', 0) * product.get('standard_price', 0)
                        }
                        for product in low_stock_products[:20]
                    ],
                    'out_of_stock_products': [
                        {
                            'name': product.get('name', 'Unknown'),
                            'list_price': product.get('list_price', 0)
                        }
                        for product in out_of_stock_products[:20]
                    ],
                    'most_active_products': [
                        {'name': name, 'movements': movements}
                        for name, movements in most_active_products
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating inventory report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_dashboard_data(self, dashboard_type: str, token: str, database: str,
                          user: User = None) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data
        """
        try:
            if dashboard_type == 'sales':
                return self._get_sales_dashboard(token, database)
            elif dashboard_type == 'inventory':
                return self._get_inventory_dashboard(token, database)
            elif dashboard_type == 'financial':
                return self._get_financial_dashboard(token, database)
            elif dashboard_type == 'operations':
                return self._get_operations_dashboard(token, database)
            else:
                return {
                    'success': False,
                    'error': f'Unknown dashboard type: {dashboard_type}'
                }
                
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_sales_dashboard(self, token: str, database: str) -> Dict[str, Any]:
        """Get sales dashboard data"""
        # Get current month sales
        current_month_report = self.generate_sales_report(token, database, 'month')
        
        # Get previous month for comparison
        previous_month_report = self.generate_sales_report(
            token, database, 'month',
            date_from=(timezone.now().replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d'),
            date_to=(timezone.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
        )
        
        # Get recent orders
        recent_orders = self.odoo_client.list_records(
            model_name='sale.order',
            token=token,
            database=database,
            domain=[
                ('date_order', '>=', (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')),
                ('state', 'in', ['sale', 'done'])
            ],
            fields=['id', 'name', 'partner_id', 'amount_total', 'date_order'],
            order='date_order desc',
            limit=10
        )
        
        return {
            'success': True,
            'dashboard': {
                'current_period': current_month_report.get('report', {}),
                'previous_period': previous_month_report.get('report', {}),
                'recent_orders': recent_orders.get('data', []),
                'kpis': {
                    'total_sales': current_month_report.get('report', {}).get('summary', {}).get('total_sales', 0),
                    'orders_count': current_month_report.get('report', {}).get('summary', {}).get('orders_count', 0),
                    'growth_rate': current_month_report.get('report', {}).get('summary', {}).get('growth_rate', 0),
                    'average_order_value': current_month_report.get('report', {}).get('summary', {}).get('average_order_value', 0)
                }
            }
        }
    
    def _get_inventory_dashboard(self, token: str, database: str) -> Dict[str, Any]:
        """Get inventory dashboard data"""
        inventory_report = self.generate_inventory_report(token, database)
        
        # Get recent stock movements
        recent_movements = self.odoo_client.list_records(
            model_name='stock.move',
            token=token,
            database=database,
            domain=[
                ('date', '>=', (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')),
                ('state', '=', 'done')
            ],
            fields=['product_id', 'product_uom_qty', 'location_id', 'location_dest_id', 'date'],
            order='date desc',
            limit=20
        )
        
        return {
            'success': True,
            'dashboard': {
                'inventory_summary': inventory_report.get('report', {}),
                'recent_movements': recent_movements.get('data', []),
                'kpis': {
                    'total_products': inventory_report.get('report', {}).get('summary', {}).get('total_products', 0),
                    'total_value': inventory_report.get('report', {}).get('summary', {}).get('total_inventory_value', 0),
                    'low_stock_count': inventory_report.get('report', {}).get('summary', {}).get('low_stock_count', 0),
                    'out_of_stock_count': inventory_report.get('report', {}).get('summary', {}).get('out_of_stock_count', 0)
                }
            }
        }
    
    def _get_financial_dashboard(self, token: str, database: str) -> Dict[str, Any]:
        """Get financial dashboard data"""
        # Get account moves for current month
        current_month = timezone.now().strftime('%Y-%m')
        
        account_moves = self.odoo_client.list_records(
            model_name='account.move',
            token=token,
            database=database,
            domain=[
                ('date', '>=', f'{current_month}-01'),
                ('state', '=', 'posted')
            ],
            fields=['id', 'name', 'date', 'amount_total', 'move_type', 'partner_id']
        )
        
        # Calculate financial metrics
        total_revenue = sum(
            move.get('amount_total', 0) for move in account_moves.get('data', [])
            if move.get('move_type') in ['out_invoice', 'out_refund']
        )
        
        total_expenses = sum(
            move.get('amount_total', 0) for move in account_moves.get('data', [])
            if move.get('move_type') in ['in_invoice', 'in_refund']
        )
        
        net_profit = total_revenue - total_expenses
        
        return {
            'success': True,
            'dashboard': {
                'financial_summary': {
                    'total_revenue': total_revenue,
                    'total_expenses': total_expenses,
                    'net_profit': net_profit,
                    'profit_margin': (net_profit / total_revenue * 100) if total_revenue > 0 else 0
                },
                'recent_transactions': account_moves.get('data', [])[:10],
                'kpis': {
                    'revenue': total_revenue,
                    'expenses': total_expenses,
                    'profit': net_profit,
                    'margin': (net_profit / total_revenue * 100) if total_revenue > 0 else 0
                }
            }
        }
    
    def _get_operations_dashboard(self, token: str, database: str) -> Dict[str, Any]:
        """Get operations dashboard data"""
        # Get recent activities across different models
        recent_activities = []
        
        # Recent sales orders
        recent_orders = self.odoo_client.list_records(
            model_name='sale.order',
            token=token,
            database=database,
            domain=[('date_order', '>=', (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d'))],
            fields=['id', 'name', 'date_order', 'state'],
            order='date_order desc',
            limit=5
        )
        
        for order in recent_orders.get('data', []):
            recent_activities.append({
                'type': 'sale_order',
                'description': f'Order {order.get("name", "")} created',
                'timestamp': order.get('date_order'),
                'status': order.get('state')
            })
        
        # Recent stock moves
        recent_moves = self.odoo_client.list_records(
            model_name='stock.move',
            token=token,
            database=database,
            domain=[('date', '>=', (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d'))],
            fields=['id', 'product_id', 'date', 'state'],
            order='date desc',
            limit=5
        )
        
        for move in recent_moves.get('data', []):
            recent_activities.append({
                'type': 'stock_move',
                'description': f'Stock movement for product {move.get("product_id", [0, "Unknown"])[1]}',
                'timestamp': move.get('date'),
                'status': move.get('state')
            })
        
        # Sort by timestamp
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'success': True,
            'dashboard': {
                'recent_activities': recent_activities[:10],
                'kpis': {
                    'orders_this_week': len(recent_orders.get('data', [])),
                    'stock_movements_this_week': len(recent_moves.get('data', [])),
                    'active_workflows': 0,  # TODO: Implement workflow counting
                    'pending_approvals': 0   # TODO: Implement approval counting
                }
            }
        }
    
    def _calculate_date_range(self, period: str) -> tuple:
        """Calculate date range for a given period"""
        now = timezone.now()
        
        if period == 'day':
            return now.strftime('%Y-%m-%d'), now.strftime('%Y-%m-%d')
        elif period == 'week':
            start = now - timedelta(days=now.weekday())
            end = start + timedelta(days=6)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
        elif period == 'month':
            start = now.replace(day=1)
            if now.month == 12:
                end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
        elif period == 'quarter':
            quarter = (now.month - 1) // 3
            start = now.replace(month=quarter * 3 + 1, day=1)
            if quarter == 3:
                end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = now.replace(month=(quarter + 1) * 3 + 1, day=1) - timedelta(days=1)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
        elif period == 'year':
            start = now.replace(month=1, day=1)
            end = now.replace(month=12, day=31)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
        else:
            # Default to current month
            start = now.replace(day=1)
            if now.month == 12:
                end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
    
    def _calculate_previous_period(self, date_from: str, date_to: str) -> tuple:
        """Calculate previous period dates"""
        from_date = datetime.strptime(date_from, '%Y-%m-%d')
        to_date = datetime.strptime(date_to, '%Y-%m-%d')
        
        period_days = (to_date - from_date).days + 1
        
        previous_from = from_date - timedelta(days=period_days)
        previous_to = from_date - timedelta(days=1)
        
        return previous_from.strftime('%Y-%m-%d'), previous_to.strftime('%Y-%m-%d')


# Global BI service instance
bi_service = BIService() 