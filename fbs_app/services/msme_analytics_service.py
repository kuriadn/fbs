"""
MSME Analytics Service

Comprehensive service for MSME business analytics including:
- Financial performance analysis
- Operational metrics
- Customer analytics
- Compliance monitoring
- Business intelligence reporting
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from django.db import transaction
from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json
from decimal import Decimal

from ..models.msme import (
    MSMEKPI, MSMECompliance, MSMEAnalytics, 
    MSMEMarketing, MSMEKPI
)
from ..models.accounting import (
    CashEntry, IncomeExpense, BasicLedger, TaxCalculation
)
from ..models.compliance import ComplianceRule, AuditTrail

logger = logging.getLogger('fbs_app')


class MSMEAnalyticsService:
    """Service for MSME business analytics and reporting"""
    
    def __init__(self, solution_name: str, user: User = None):
        self.solution_name = solution_name
        self.user = user
        self.logger = logging.getLogger(f"{__name__}.{solution_name}")
    
    def get_business_dashboard(self, business_id: int, period: str = 'monthly') -> Dict[str, Any]:
        """
        Get comprehensive business dashboard data
        
        Args:
            business_id: Business identifier
            period: Analysis period (daily, weekly, monthly, quarterly, yearly)
            
        Returns:
            Dict containing dashboard metrics and charts
        """
        try:
            # Get date range for the period
            start_date, end_date = self._get_period_dates(period)
            
            dashboard_data = {
                'period': period,
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'financial_metrics': self._get_financial_metrics(start_date, end_date),
                'operational_metrics': self._get_operational_metrics(start_date, end_date),
                'customer_metrics': self._get_customer_metrics(start_date, end_date),
                'compliance_metrics': self._get_compliance_metrics(start_date, end_date),
                'kpi_performance': self._get_kpi_performance(),
                'trends': self._get_business_trends(period),
                'alerts': self._get_business_alerts()
            }
            
            return {
                'success': True,
                'business_id': business_id,
                'dashboard': dashboard_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get business dashboard: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get business dashboard'
            }
    
    def _get_period_dates(self, period: str) -> Tuple[datetime, datetime]:
        """Get start and end dates for the specified period"""
        now = timezone.now()
        
        if period == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'weekly':
            start_date = now - timedelta(days=7)
            end_date = now
        elif period == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'quarterly':
            quarter = (now.month - 1) // 3
            start_date = now.replace(month=quarter * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'yearly':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        else:
            # Default to monthly
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        
        return start_date, end_date
    
    def _get_financial_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get financial performance metrics"""
        try:
            # Get cash flow data
            cash_entries = CashEntry.objects.filter(
                business_id=self.solution_name,
                entry_date__range=[start_date.date(), end_date.date()]
            )
            
            # Get income/expense data
            income_expenses = IncomeExpense.objects.filter(
                business_id=self.solution_name,
                transaction_date__range=[start_date.date(), end_date.date()]
            )
            
            # Calculate metrics
            total_receipts = cash_entries.filter(entry_type='receipt').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            total_payments = cash_entries.filter(entry_type='payment').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            total_income = income_expenses.filter(transaction_type='income').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            total_expenses = income_expenses.filter(transaction_type='expense').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            net_cash_flow = total_receipts - total_payments
            net_profit = total_income - total_expenses
            
            return {
                'total_receipts': float(total_receipts),
                'total_payments': float(total_payments),
                'net_cash_flow': float(net_cash_flow),
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'net_profit': float(net_profit),
                'profit_margin': round((net_profit / total_income * 100) if total_income > 0 else 0, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get financial metrics: {str(e)}")
            return {}
    
    def _get_operational_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get operational performance metrics"""
        try:
            # Get KPI data
            kpis = MSMEKPI.objects.filter(
                solution_name=self.solution_name,
                kpi_type='operational'
            )
            
            operational_metrics = {}
            
            for kpi in kpis:
                if kpi.kpi_name == 'Production Efficiency':
                    operational_metrics['production_efficiency'] = {
                        'current': float(kpi.current_value),
                        'target': float(kpi.target_value) if kpi.target_value else None,
                        'unit': kpi.unit
                    }
                elif kpi.kpi_name == 'Service Delivery Time':
                    operational_metrics['service_delivery_time'] = {
                        'current': float(kpi.current_value),
                        'target': float(kpi.target_value) if kpi.target_value else None,
                        'unit': kpi.unit
                    }
            
            return operational_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get operational metrics: {str(e)}")
            return {}
    
    def _get_customer_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get customer-related metrics"""
        try:
            # Get customer KPI data
            customer_kpis = MSMEKPI.objects.filter(
                solution_name=self.solution_name,
                kpi_type='customer'
            )
            
            customer_metrics = {}
            
            for kpi in customer_kpis:
                if kpi.kpi_name == 'Customer Satisfaction':
                    customer_metrics['satisfaction_score'] = {
                        'current': float(kpi.current_value),
                        'target': float(kpi.target_value) if kpi.target_value else None,
                        'unit': kpi.unit
                    }
            
            return customer_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get customer metrics: {str(e)}")
            return {}
    
    def _get_compliance_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get compliance and regulatory metrics"""
        try:
            # Get compliance rules
            compliance_rules = MSMECompliance.objects.filter(
                solution_name=self.solution_name
            )
            
            total_rules = compliance_rules.count()
            pending_rules = compliance_rules.filter(status='pending').count()
            completed_rules = compliance_rules.filter(status='completed').count()
            overdue_rules = compliance_rules.filter(
                status='pending',
                due_date__lt=timezone.now().date()
            ).count()
            
            # Calculate compliance score
            compliance_score = 0
            if total_rules > 0:
                compliance_score = (completed_rules / total_rules) * 100
            
            return {
                'total_rules': total_rules,
                'pending_rules': pending_rules,
                'completed_rules': completed_rules,
                'overdue_rules': overdue_rules,
                'compliance_score': round(compliance_score, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get compliance metrics: {str(e)}")
            return {}
    
    def _get_kpi_performance(self) -> List[Dict[str, Any]]:
        """Get KPI performance data"""
        try:
            kpis = MSMEKPI.objects.filter(
                solution_name=self.solution_name
            )
            
            kpi_performance = []
            for kpi in kpis:
                performance = self._calculate_kpi_performance(kpi)
                
                kpi_performance.append({
                    'id': kpi.id,
                    'name': kpi.kpi_name,
                    'type': kpi.kpi_type,
                    'current_value': float(kpi.current_value),
                    'target_value': float(kpi.target_value) if kpi.target_value else None,
                    'unit': kpi.unit,
                    'frequency': kpi.frequency,
                    'performance': performance
                })
            
            return kpi_performance
            
        except Exception as e:
            self.logger.error(f"Failed to get KPI performance: {str(e)}")
            return []
    
    def _calculate_kpi_performance(self, kpi: MSMEKPI) -> Dict[str, Any]:
        """Calculate KPI performance metrics"""
        if not kpi.target_value:
            return {'status': 'no_target', 'percentage': None}
        
        try:
            current = float(kpi.current_value)
            target = float(kpi.target_value)
            
            if target == 0:
                percentage = 100 if current == 0 else 0
            else:
                percentage = (current / target) * 100
            
            if percentage >= 100:
                status = 'exceeded'
            elif percentage >= 80:
                status = 'on_track'
            elif percentage >= 60:
                status = 'needs_attention'
            else:
                status = 'critical'
            
            return {
                'status': status,
                'percentage': round(percentage, 2),
                'gap': target - current
            }
            
        except (ValueError, TypeError):
            return {'status': 'error', 'percentage': None}
    
    def _get_business_trends(self, period: str) -> Dict[str, Any]:
        """Get business performance trends"""
        try:
            trends = {}
            
            # Get revenue trends
            revenue_trends = self._get_revenue_trends(period)
            trends['revenue'] = revenue_trends
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to get business trends: {str(e)}")
            return {}
    
    def _get_revenue_trends(self, period: str) -> List[Dict[str, Any]]:
        """Get revenue trends over time"""
        try:
            # Get last 6 periods
            periods = 6
            trends = []
            
            for i in range(periods):
                date = timezone.now() - timedelta(days=30 * i)
                start_date = date.replace(day=1)
                end_date = start_date.replace(day=28) + timedelta(days=4)
                end_date = end_date.replace(day=1) - timedelta(days=1)
                
                revenue = IncomeExpense.objects.filter(
                    created_by=self.user,
                    transaction_type='income',
                    transaction_date__range=[start_date.date(), end_date.date()]
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                trends.append({
                    'period': start_date.strftime('%Y-%m-%d'),
                    'value': float(revenue),
                    'formatted_period': start_date.strftime('%b %Y')
                })
            
            trends.reverse()
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to get revenue trends: {str(e)}")
            return []
    
    def _get_business_alerts(self) -> List[Dict[str, Any]]:
        """Get business alerts and notifications"""
        try:
            alerts = []
            
            # Check for overdue compliance items
            overdue_compliance = MSMECompliance.objects.filter(
                solution_name=self.solution_name,
                status='pending',
                due_date__lt=timezone.now().date()
            )
            
            for item in overdue_compliance:
                alerts.append({
                    'type': 'compliance_overdue',
                    'severity': 'high',
                    'message': f"Compliance item '{item.compliance_type}' is overdue",
                    'due_date': item.due_date,
                    'days_overdue': (timezone.now().date() - item.due_date).days
                })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to get business alerts: {str(e)}")
            return []
    
    def generate_business_report(self, business_id: int, report_type: str, 
                               start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate comprehensive business report
        
        Args:
            business_id: Business identifier
            report_type: Type of report (financial, operational, compliance, comprehensive)
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Dict containing report data and analysis
        """
        try:
            if report_type == 'financial':
                report_data = self._generate_financial_report(start_date, end_date)
            elif report_type == 'operational':
                report_data = self._generate_operational_report(start_date, end_date)
            elif report_type == 'compliance':
                report_data = self._generate_compliance_report(start_date, end_date)
            elif report_type == 'comprehensive':
                report_data = self._generate_comprehensive_report(start_date, end_date)
            else:
                return {
                    'success': False,
                    'error': f"Unknown report type: {report_type}",
                    'message': 'Invalid report type specified'
                }
            
            return {
                'success': True,
                'business_id': business_id,
                'report_type': report_type,
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'report_data': report_data,
                'generated_at': timezone.now()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate business report: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to generate business report'
            }
    
    def _generate_financial_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate financial performance report"""
        try:
            financial_metrics = self._get_financial_metrics(start_date, end_date)
            
            return {
                'current_period': financial_metrics,
                'analysis': self._analyze_financial_performance(financial_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate financial report: {str(e)}")
            return {}
    
    def _analyze_financial_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial performance and provide insights"""
        analysis = {
            'strengths': [],
            'concerns': [],
            'recommendations': []
        }
        
        # Analyze profit margin
        profit_margin = metrics.get('profit_margin', 0)
        if profit_margin > 20:
            analysis['strengths'].append(f'Strong profit margin of {profit_margin}%')
        elif profit_margin < 10:
            analysis['concerns'].append(f'Low profit margin of {profit_margin}%')
            analysis['recommendations'].append('Review pricing strategy and cost structure')
        
        # Analyze cash flow
        if metrics.get('net_cash_flow', 0) > 0:
            analysis['strengths'].append('Positive cash flow maintained')
        else:
            analysis['concerns'].append('Negative cash flow - review payment terms and collections')
            analysis['recommendations'].append('Implement stricter payment terms and improve collections process')
        
        return analysis
    
    def _generate_operational_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate operational performance report"""
        try:
            operational_metrics = self._get_operational_metrics(start_date, end_date)
            kpi_performance = self._get_kpi_performance()
            
            # Filter operational KPIs
            operational_kpis = [kpi for kpi in kpi_performance if kpi['type'] == 'operational']
            
            return {
                'metrics': operational_metrics,
                'kpi_performance': operational_kpis,
                'analysis': self._analyze_operational_performance(operational_kpis)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate operational report: {str(e)}")
            return {}
    
    def _analyze_operational_performance(self, kpis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze operational performance and provide insights"""
        analysis = {
            'strengths': [],
            'concerns': [],
            'recommendations': []
        }
        
        for kpi in kpis:
            performance = kpi.get('performance', {})
            status = performance.get('status', 'unknown')
            
            if status == 'exceeded':
                analysis['strengths'].append(f"KPI '{kpi['name']}' exceeding targets")
            elif status == 'critical':
                analysis['concerns'].append(f"KPI '{kpi['name']}' performing critically")
                analysis['recommendations'].append(f"Immediate action required for {kpi['name']}")
        
        return analysis
    
    def _generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance and regulatory report"""
        try:
            compliance_metrics = self._get_compliance_metrics(start_date, end_date)
            
            return {
                'metrics': compliance_metrics,
                'analysis': self._analyze_compliance_performance(compliance_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {str(e)}")
            return {}
    
    def _analyze_compliance_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze compliance performance and provide insights"""
        analysis = {
            'strengths': [],
            'concerns': [],
            'recommendations': []
        }
        
        compliance_score = metrics.get('compliance_score', 0)
        overdue_rules = metrics.get('overdue_rules', 0)
        
        if compliance_score >= 80:
            analysis['strengths'].append(f'Strong compliance score of {compliance_score}%')
        elif compliance_score < 60:
            analysis['concerns'].append(f'Low compliance score of {compliance_score}%')
            analysis['recommendations'].append('Prioritize compliance activities and allocate resources')
        
        if overdue_rules > 0:
            analysis['concerns'].append(f'{overdue_rules} compliance items overdue')
            analysis['recommendations'].append('Address overdue compliance items immediately')
        
        return analysis
    
    def _generate_comprehensive_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive business report"""
        try:
            return {
                'financial': self._generate_financial_report(start_date, end_date),
                'operational': self._generate_operational_report(start_date, end_date),
                'compliance': self._generate_compliance_report(start_date, end_date),
                'summary': self._generate_executive_summary(start_date, end_date)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate comprehensive report: {str(e)}")
            return {}
    
    def _generate_executive_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate executive summary of business performance"""
        try:
            financial_metrics = self._get_financial_metrics(start_date, end_date)
            compliance_metrics = self._get_compliance_metrics(start_date, end_date)
            
            # Overall business health score
            health_score = 0
            
            # Financial health (40% weight)
            if financial_metrics.get('profit_margin', 0) > 0:
                financial_score = min(100, financial_metrics.get('profit_margin', 0) * 2)
                health_score += financial_score * 0.4
            
            # Cash flow health (30% weight)
            if financial_metrics.get('net_cash_flow', 0) > 0:
                cash_flow_score = 100
            else:
                cash_flow_score = max(0, 100 + (financial_metrics.get('net_cash_flow', 0) / 1000))
            health_score += cash_flow_score * 0.3
            
            # Compliance health (30% weight)
            compliance_score = compliance_metrics.get('compliance_score', 0)
            health_score += compliance_score * 0.3
            
            # Overall assessment
            if health_score >= 80:
                assessment = 'Excellent'
                color = 'green'
            elif health_score >= 60:
                assessment = 'Good'
                color = 'blue'
            elif health_score >= 40:
                assessment = 'Fair'
                color = 'yellow'
            else:
                assessment = 'Poor'
                color = 'red'
            
            return {
                'business_health_score': round(health_score, 2),
                'assessment': assessment,
                'color': color,
                'key_highlights': self._get_key_highlights(financial_metrics, compliance_metrics),
                'key_concerns': self._get_key_concerns(financial_metrics, compliance_metrics),
                'recommendations': self._get_executive_recommendations(health_score)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate executive summary: {str(e)}")
            return {}
    
    def _get_key_highlights(self, financial_metrics: Dict[str, Any], 
                           compliance_metrics: Dict[str, Any]) -> List[str]:
        """Get key business highlights"""
        highlights = []
        
        if financial_metrics.get('profit_margin', 0) > 20:
            highlights.append(f"Strong profit margin of {financial_metrics.get('profit_margin')}%")
        
        if compliance_metrics.get('compliance_score', 0) >= 80:
            highlights.append(f"Excellent compliance score of {compliance_metrics.get('compliance_score')}%")
        
        if financial_metrics.get('net_cash_flow', 0) > 0:
            highlights.append("Positive cash flow maintained")
        
        return highlights
    
    def _get_key_concerns(self, financial_metrics: Dict[str, Any], 
                         compliance_metrics: Dict[str, Any]) -> List[str]:
        """Get key business concerns"""
        concerns = []
        
        if financial_metrics.get('profit_margin', 0) < 10:
            concerns.append(f"Low profit margin of {financial_metrics.get('profit_margin')}%")
        
        if financial_metrics.get('net_cash_flow', 0) < 0:
            concerns.append("Negative cash flow - review payment terms and collections")
        
        if compliance_metrics.get('overdue_rules', 0) > 0:
            concerns.append(f"{compliance_metrics.get('overdue_rules')} compliance items overdue")
        
        return concerns
    
    def _get_executive_recommendations(self, health_score: float) -> List[str]:
        """Get executive recommendations based on business health"""
        recommendations = []
        
        if health_score < 40:
            recommendations.extend([
                "Immediate action required to address critical business issues",
                "Review and restructure business operations",
                "Seek external consultation for business turnaround"
            ])
        elif health_score < 60:
            recommendations.extend([
                "Focus on improving operational efficiency",
                "Review pricing strategy and cost structure",
                "Strengthen compliance and risk management"
            ])
        elif health_score < 80:
            recommendations.extend([
                "Optimize business processes for better performance",
                "Explore growth opportunities and market expansion",
                "Enhance customer satisfaction and retention"
            ])
        else:
            recommendations.extend([
                "Maintain current performance levels",
                "Focus on sustainable growth and market leadership",
                "Continue innovation and process improvement"
            ])
        
        return recommendations
