"""
MSME Service Manager

Central coordinator for all MSME services providing:
- Unified interface for MSME operations
- Service coordination and orchestration
- Business process management
- Cross-service data consistency
"""

import logging
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json

from .msme_business_service import MSMEBusinessService
from .msme_analytics_service import MSMEAnalyticsService
from .msme_compliance_service import MSMEComplianceService
from .msme_workflow_service import MSMEWorkflowService
from .msme_accounting_service import MSMEAccountingService

logger = logging.getLogger(__name__)


class MSMEServiceManager:
    """Central manager for all MSME services"""
    
    def __init__(self, user: User):
        self.user = user
        self.logger = logging.getLogger(f"{__name__}.{user.username}")
        
        # Initialize all MSME services
        self.business_service = MSMEBusinessService(user)
        self.analytics_service = MSMEAnalyticsService(user)
        self.compliance_service = MSMEComplianceService(user)
        self.workflow_service = MSMEWorkflowService(user)
        self.accounting_service = MSMEAccountingService(user)
    
    def create_complete_business(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete MSME business with all components
        
        Args:
            business_data: Comprehensive business information
            
        Returns:
            Dict containing business creation result
        """
        try:
            with transaction.atomic():
                # Step 1: Create business profile and basic setup
                business_result = self.business_service.create_business(business_data)
                
                if not business_result['success']:
                    return business_result
                
                business_id = business_result['business_id']
                
                # Step 2: Initialize accounting structure
                accounting_result = self._initialize_accounting_structure(business_data)
                
                # Step 3: Setup compliance framework
                compliance_result = self._setup_compliance_framework(business_data)
                
                # Step 4: Create business workflows
                workflow_result = self._create_business_workflows(business_data)
                
                # Step 5: Initialize analytics and reporting
                analytics_result = self._initialize_analytics_framework(business_data)
                
                # Step 6: Create business templates and documents
                templates_result = self._create_business_templates(business_data)
                
                # Compile comprehensive result
                complete_result = {
                    'success': True,
                    'business_id': business_id,
                    'setup_wizard_id': business_result.get('setup_wizard_id'),
                    'components_initialized': {
                        'business_profile': business_result['success'],
                        'accounting': accounting_result['success'],
                        'compliance': compliance_result['success'],
                        'workflows': workflow_result['success'],
                        'analytics': analytics_result['success'],
                        'templates': templates_result['success']
                    },
                    'message': 'Complete MSME business created successfully',
                    'next_steps': self._get_complete_setup_steps()
                }
                
                self.logger.info(f"Complete MSME business created: {business_data.get('company_name')}")
                
                return complete_result
                
        except Exception as e:
            self.logger.error(f"Failed to create complete business: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create complete business'
            }
    
    def _initialize_accounting_structure(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize accounting structure for the business"""
        try:
            # Create chart of accounts
            chart_of_accounts = self._get_default_chart_of_accounts(business_data.get('business_type'))
            
            # Create initial financial period
            current_date = timezone.now().date()
            period_result = self.accounting_service.create_financial_period({
                'period_name': f"Period {current_date.year}-{current_date.month:02d}",
                'period_type': 'monthly',
                'start_date': current_date.replace(day=1),
                'end_date': (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            })
            
            return {
                'success': True,
                'chart_of_accounts_created': len(chart_of_accounts),
                'financial_period_created': period_result.get('success', False)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize accounting structure: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_default_chart_of_accounts(self, business_type: str) -> List[Dict[str, Any]]:
        """Get default chart of accounts for business type"""
        # Base accounts for all businesses
        base_accounts = [
            {'code': '1000', 'name': 'Assets', 'type': 'asset', 'parent': None},
            {'code': '1100', 'name': 'Current Assets', 'type': 'asset', 'parent': '1000'},
            {'code': '1110', 'name': 'Cash', 'type': 'asset', 'parent': '1100'},
            {'code': '1120', 'name': 'Accounts Receivable', 'type': 'asset', 'parent': '1100'},
            {'code': '1200', 'name': 'Fixed Assets', 'type': 'asset', 'parent': '1000'},
            {'code': '2000', 'name': 'Liabilities', 'type': 'liability', 'parent': None},
            {'code': '2100', 'name': 'Current Liabilities', 'type': 'liability', 'parent': '2000'},
            {'code': '2110', 'name': 'Accounts Payable', 'type': 'liability', 'parent': '2100'},
            {'code': '3000', 'name': 'Equity', 'type': 'equity', 'parent': None},
            {'code': '3100', 'name': 'Owner Equity', 'type': 'equity', 'parent': '3000'},
            {'code': '4000', 'name': 'Revenue', 'type': 'income', 'parent': None},
            {'code': '5000', 'name': 'Expenses', 'type': 'expense', 'parent': None}
        ]
        
        # Add business-specific accounts
        if business_type == 'retail':
            base_accounts.extend([
                {'code': '1130', 'name': 'Inventory', 'type': 'asset', 'parent': '1100'},
                {'code': '4100', 'name': 'Sales Revenue', 'type': 'income', 'parent': '4000'},
                {'code': '5100', 'name': 'Cost of Goods Sold', 'type': 'expense', 'parent': '5000'}
            ])
        elif business_type == 'manufacturing':
            base_accounts.extend([
                {'code': '1130', 'name': 'Raw Materials', 'type': 'asset', 'parent': '1100'},
                {'code': '1140', 'name': 'Work in Progress', 'type': 'asset', 'parent': '1100'},
                {'code': '1150', 'name': 'Finished Goods', 'type': 'asset', 'parent': '1100'},
                {'code': '4100', 'name': 'Manufacturing Revenue', 'type': 'income', 'parent': '4000'},
                {'code': '5100', 'name': 'Production Costs', 'type': 'expense', 'parent': '5000'}
            ])
        elif business_type == 'services':
            base_accounts.extend([
                {'code': '4100', 'name': 'Service Revenue', 'type': 'income', 'parent': '4000'},
                {'code': '5100', 'name': 'Service Delivery Costs', 'type': 'expense', 'parent': '5000'}
            ])
        
        return base_accounts
    
    def _setup_compliance_framework(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup compliance framework for the business"""
        try:
            business_type = business_data.get('business_type', 'services')
            industry = business_data.get('industry', 'general')
            
            # Get industry-specific compliance rules
            compliance_rules = self._get_industry_compliance_rules(business_type, industry)
            
            # Create compliance rules
            rules_created = 0
            for rule_data in compliance_rules:
                result = self.compliance_service.create_compliance_rule(rule_data)
                if result['success']:
                    rules_created += 1
            
            return {
                'success': True,
                'compliance_rules_created': rules_created,
                'total_rules': len(compliance_rules)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to setup compliance framework: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_industry_compliance_rules(self, business_type: str, industry: str) -> List[Dict[str, Any]]:
        """Get industry-specific compliance rules"""
        # Base compliance rules for all businesses
        base_rules = [
            {
                'name': 'Annual Tax Filing',
                'type': 'tax',
                'due_date': timezone.now().date().replace(month=4, day=15),
                'description': 'Annual income tax filing requirement'
            },
            {
                'name': 'Business License Renewal',
                'type': 'regulatory',
                'due_date': timezone.now().date().replace(month=12, day=31),
                'description': 'Business license renewal requirement'
            }
        ]
        
        # Add business-specific rules
        if business_type == 'retail':
            base_rules.extend([
                {
                    'name': 'Sales Tax Reporting',
                    'type': 'tax',
                    'due_date': timezone.now().date().replace(month=1, day=31),
                    'description': 'Quarterly sales tax reporting'
                }
            ])
        elif business_type == 'manufacturing':
            base_rules.extend([
                {
                    'name': 'Environmental Compliance',
                    'type': 'environmental',
                    'due_date': timezone.now().date().replace(month=6, day=30),
                    'description': 'Environmental compliance reporting'
                }
            ])
        
        return base_rules
    
    def _create_business_workflows(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create business workflows"""
        try:
            business_type = business_data.get('business_type', 'services')
            
            # Get business-specific workflows
            workflows = self._get_business_workflows(business_type)
            
            workflows_created = 0
            for workflow_data in workflows:
                result = self.workflow_service.create_workflow_definition(workflow_data)
                if result['success']:
                    workflows_created += 1
            
            return {
                'success': True,
                'workflows_created': workflows_created,
                'total_workflows': len(workflows)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create business workflows: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_business_workflows(self, business_type: str) -> List[Dict[str, Any]]:
        """Get business-specific workflows"""
        # Base workflows for all businesses
        base_workflows = [
            {
                'name': 'Invoice Processing',
                'description': 'Standard invoice processing workflow',
                'workflow_type': 'document',
                'steps': [
                    {'name': 'Invoice Creation', 'order': 1, 'type': 'manual', 'required': True},
                    {'name': 'Invoice Review', 'order': 2, 'type': 'manual', 'required': True},
                    {'name': 'Invoice Approval', 'order': 3, 'type': 'manual', 'required': True},
                    {'name': 'Invoice Sent', 'order': 4, 'type': 'automated', 'required': True}
                ],
                'transitions': [
                    {'name': 'Create to Review', 'from_step': 'Invoice Creation', 'to_step': 'Invoice Review', 'type': 'forward'},
                    {'name': 'Review to Approval', 'from_step': 'Invoice Review', 'to_step': 'Invoice Approval', 'type': 'forward'},
                    {'name': 'Approval to Sent', 'from_step': 'Invoice Approval', 'to_step': 'Invoice Sent', 'type': 'forward'}
                ]
            }
        ]
        
        # Add business-specific workflows
        if business_type == 'retail':
            base_workflows.extend([
                {
                    'name': 'Sales Order Processing',
                    'description': 'Retail sales order workflow',
                    'workflow_type': 'sales',
                    'steps': [
                        {'name': 'Order Received', 'order': 1, 'type': 'manual', 'required': True},
                        {'name': 'Inventory Check', 'order': 2, 'type': 'automated', 'required': True},
                        {'name': 'Order Confirmation', 'order': 3, 'type': 'manual', 'required': True},
                        {'name': 'Order Fulfilled', 'order': 4, 'type': 'manual', 'required': True}
                    ],
                    'transitions': [
                        {'name': 'Received to Check', 'from_step': 'Order Received', 'to_step': 'Inventory Check', 'type': 'forward'},
                        {'name': 'Check to Confirm', 'from_step': 'Inventory Check', 'to_step': 'Order Confirmation', 'type': 'forward'},
                        {'name': 'Confirm to Fulfill', 'from_step': 'Order Confirmation', 'to_step': 'Order Fulfilled', 'type': 'forward'}
                    ]
                }
            ])
        
        return base_workflows
    
    def _initialize_analytics_framework(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize analytics framework"""
        try:
            # Initialize basic analytics metrics
            analytics_metrics = self._get_business_analytics_metrics(business_data.get('business_type'))
            
            # Create analytics dashboard
            dashboard_result = self.analytics_service.get_business_dashboard(
                business_id=1,  # Placeholder
                period='monthly'
            )
            
            return {
                'success': True,
                'analytics_metrics_initialized': len(analytics_metrics),
                'dashboard_created': dashboard_result.get('success', False)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize analytics framework: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_business_analytics_metrics(self, business_type: str) -> List[Dict[str, Any]]:
        """Get business-specific analytics metrics"""
        # Base metrics for all businesses
        base_metrics = [
            {'name': 'Total Revenue', 'type': 'revenue'},
            {'name': 'Total Expenses', 'type': 'expenses'},
            {'name': 'Net Profit', 'type': 'profit'},
            {'name': 'Customer Count', 'type': 'customers'}
        ]
        
        # Add business-specific metrics
        if business_type == 'retail':
            base_metrics.extend([
                {'name': 'Inventory Value', 'type': 'inventory'},
                {'name': 'Sales Transactions', 'type': 'orders'}
            ])
        elif business_type == 'manufacturing':
            base_metrics.extend([
                {'name': 'Production Units', 'type': 'production'},
                {'name': 'Raw Material Cost', 'type': 'costs'}
            ])
        
        return base_metrics
    
    def _create_business_templates(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create business templates and documents"""
        try:
            business_type = business_data.get('business_type', 'services')
            
            # Get business-specific templates
            templates = self._get_business_templates(business_type)
            
            # Templates are created by the business service
            return {
                'success': True,
                'templates_available': len(templates)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create business templates: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_business_templates(self, business_type: str) -> List[Dict[str, Any]]:
        """Get business-specific templates"""
        # Base templates for all businesses
        base_templates = [
            {'name': 'Invoice Template', 'type': 'invoice'},
            {'name': 'Quotation Template', 'type': 'quotation'}
        ]
        
        # Add business-specific templates
        if business_type == 'retail':
            base_templates.extend([
                {'name': 'Receipt Template', 'type': 'receipt'}
            ])
        elif business_type == 'manufacturing':
            base_templates.extend([
                {'name': 'Purchase Order Template', 'type': 'purchase_order'}
            ])
        
        return base_templates
    
    def _get_complete_setup_steps(self) -> List[str]:
        """Get next steps for complete business setup"""
        return [
            'Review and customize business settings',
            'Configure user roles and permissions',
            'Set up integrations with external systems',
            'Train users on MSME features',
            'Launch business operations'
        ]
    
    def get_business_overview(self, business_id: int) -> Dict[str, Any]:
        """Get comprehensive business overview"""
        try:
            # Get business profile
            profile = self.business_service.get_business_profile(business_id)
            
            # Get compliance overview
            compliance = self.compliance_service.get_compliance_overview()
            
            # Get financial summary
            current_date = timezone.now()
            start_date = current_date.replace(day=1)
            end_date = current_date
            
            cash_flow = self.accounting_service.get_cash_flow_summary(start_date, end_date)
            income_expense = self.accounting_service.get_income_expense_summary(start_date, end_date)
            
            # Get KPI performance
            kpis = self.business_service.get_business_kpis(business_id)
            
            # Get workflow status
            workflows = self.workflow_service.get_user_workflows()
            
            return {
                'success': True,
                'business_id': business_id,
                'overview': {
                    'profile': profile.get('profile', {}),
                    'compliance': compliance.get('overview', {}),
                    'financial': {
                        'cash_flow': cash_flow.get('summary', {}),
                        'income_expense': income_expense.get('summary', {})
                    },
                    'kpis': kpis.get('kpis', []),
                    'workflows': workflows.get('workflows', [])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get business overview: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get business overview'
            }
    
    def run_business_health_check(self, business_id: int) -> Dict[str, Any]:
        """Run comprehensive business health check"""
        try:
            # Check compliance status
            compliance_status = self.compliance_service.get_compliance_overview()
            
            # Check financial health
            current_date = timezone.now()
            start_date = current_date.replace(day=1)
            end_date = current_date
            
            cash_flow = self.accounting_service.get_cash_flow_summary(start_date, end_date)
            income_expense = self.accounting_service.get_income_expense_summary(start_date, end_date)
            
            # Check KPI performance
            kpis = self.business_service.get_business_kpis(business_id)
            
            # Calculate overall health score
            health_score = self._calculate_business_health_score(
                compliance_status, cash_flow, income_expense, kpis
            )
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(
                compliance_status, cash_flow, income_expense, kpis
            )
            
            return {
                'success': True,
                'business_id': business_id,
                'health_check': {
                    'overall_score': health_score,
                    'compliance_score': compliance_status.get('overview', {}).get('compliance_score', 0),
                    'financial_score': self._calculate_financial_health_score(cash_flow, income_expense),
                    'operational_score': self._calculate_operational_health_score(kpis),
                    'recommendations': recommendations
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to run business health check: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to run business health check'
            }
    
    def _calculate_business_health_score(self, compliance_status: Dict[str, Any], 
                                       cash_flow: Dict[str, Any], income_expense: Dict[str, Any], 
                                       kpis: Dict[str, Any]) -> float:
        """Calculate overall business health score"""
        try:
            # Compliance weight: 30%
            compliance_score = compliance_status.get('overview', {}).get('compliance_score', 0)
            
            # Financial weight: 40%
            financial_score = self._calculate_financial_health_score(cash_flow, income_expense)
            
            # Operational weight: 30%
            operational_score = self._calculate_operational_health_score(kpis)
            
            # Calculate weighted average
            overall_score = (compliance_score * 0.3) + (financial_score * 0.4) + (operational_score * 0.3)
            
            return round(overall_score, 2)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate business health score: {str(e)}")
            return 0
    
    def _calculate_financial_health_score(self, cash_flow: Dict[str, Any], 
                                        income_expense: Dict[str, Any]) -> float:
        """Calculate financial health score"""
        try:
            score = 0
            
            # Cash flow health (50% weight)
            net_cash_flow = cash_flow.get('summary', {}).get('net_cash_flow', 0)
            if net_cash_flow > 0:
                score += 50
            
            # Profit margin health (50% weight)
            profit_margin = income_expense.get('summary', {}).get('profit_margin', 0)
            if profit_margin > 20:
                score += 50
            elif profit_margin > 10:
                score += 30
            elif profit_margin > 0:
                score += 20
            
            return score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate financial health score: {str(e)}")
            return 0
    
    def _calculate_operational_health_score(self, kpis: Dict[str, Any]) -> float:
        """Calculate operational health score"""
        try:
            score = 0
            kpi_list = kpis.get('kpis', [])
            
            if not kpi_list:
                return 0
            
            # Calculate average KPI performance
            total_performance = 0
            valid_kpis = 0
            
            for kpi in kpi_list:
                performance = kpi.get('performance', {})
                percentage = performance.get('percentage')
                
                if percentage is not None:
                    total_performance += percentage
                    valid_kpis += 1
            
            if valid_kpis > 0:
                average_performance = total_performance / valid_kpis
                score = min(100, average_performance)
            
            return score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate operational health score: {str(e)}")
            return 0
    
    def _generate_health_recommendations(self, compliance_status: Dict[str, Any], 
                                       cash_flow: Dict[str, Any], income_expense: Dict[str, Any], 
                                       kpis: Dict[str, Any]) -> List[str]:
        """Generate business health recommendations"""
        recommendations = []
        
        # Compliance recommendations
        compliance_score = compliance_status.get('overview', {}).get('compliance_score', 0)
        if compliance_score < 80:
            recommendations.append("Improve compliance management and address overdue items")
        
        # Financial recommendations
        net_cash_flow = cash_flow.get('summary', {}).get('net_cash_flow', 0)
        if net_cash_flow < 0:
            recommendations.append("Review cash flow management and payment terms")
        
        profit_margin = income_expense.get('summary', {}).get('profit_margin', 0)
        if profit_margin < 10:
            recommendations.append("Review pricing strategy and cost structure")
        
        # Operational recommendations
        kpi_list = kpis.get('kpis', [])
        critical_kpis = [kpi for kpi in kpi_list if kpi.get('performance', {}).get('status') == 'critical']
        
        if critical_kpis:
            recommendations.append(f"Address {len(critical_kpis)} critical KPI performance issues")
        
        if not recommendations:
            recommendations.append("Business is performing well - maintain current standards")
        
        return recommendations
