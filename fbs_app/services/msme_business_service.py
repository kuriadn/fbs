"""
MSME Business Service

Comprehensive service for MSME business management including:
- Business setup and creation
- Business profile management
- Industry-specific configuration
- Business analytics and reporting
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

# Lazy imports to avoid Django configuration issues
# Models will be imported only when methods are called

logger = logging.getLogger(__name__)


class MSMEBusinessService:
    """Service for MSME business management operations"""
    
    def __init__(self, solution_name: str, user=None):
        self.solution_name = solution_name
        self.user = user
        self.logger = logging.getLogger(f"{__name__}.{solution_name}")
    
    def create_business(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new MSME business with complete setup
        
        Args:
            business_data: Business information including name, type, industry, etc.
            
        Returns:
            Dict containing business creation result and business ID
        """
        # Lazy imports to avoid Django configuration issues
        from django.db import transaction
        from django.utils import timezone
        from ..models.msme import MSMESetupWizard, MSMEKPI, MSMECompliance, MSMEMarketing, MSMETemplate, MSMEAnalytics
        from ..models.core import BusinessRule, CustomField
        
        try:
            with transaction.atomic():
                # Create business setup wizard
                setup_wizard = MSMESetupWizard.objects.create(
                    solution_name=self.solution_name,
                    status='in_progress',
                    business_type=business_data.get('business_type', 'services'),
                    configuration=business_data
                )
                
                # Create business profile
                business_profile = self._create_business_profile(business_data)
                
                # Initialize business KPIs
                kpis = self._initialize_business_kpis(business_data)
                
                # Setup compliance rules
                compliance_rules = self._setup_compliance_rules(business_data)
                
                # Create business templates
                templates = self._create_business_templates(business_data)
                
                # Initialize analytics
                analytics = self._initialize_business_analytics(business_data)
                
                # Update setup wizard status
                setup_wizard.setup_stage = 'basic_info'
                setup_wizard.setup_data.update({
                    'business_profile_id': business_profile.id,
                    'kpis_created': len(kpis),
                    'compliance_rules_created': len(compliance_rules),
                    'templates_created': len(templates),
                    'analytics_initialized': True
                })
                setup_wizard.save()
                
                self.logger.info(f"Business created successfully: {business_data.get('company_name')}")
                
                return {
                    'success': True,
                    'business_id': business_profile.id,
                    'setup_wizard_id': setup_wizard.id,
                    'message': 'Business created successfully',
                    'next_steps': self._get_next_setup_steps(setup_wizard.setup_stage)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create business: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create business'
            }
    
    def _create_business_profile(self, business_data: Dict[str, Any]) -> Any:
        """Create business profile with custom fields"""
        try:
            # Create business profile using custom fields system
            profile_data = {
                'company_name': business_data.get('company_name'),
                'business_type': business_data.get('business_type'),
                'industry': business_data.get('industry'),
                'registration_number': business_data.get('registration_number'),
                'tax_id': business_data.get('tax_id'),
                'address': business_data.get('address'),
                'phone': business_data.get('phone'),
                'email': business_data.get('email'),
                'website': business_data.get('website'),
                'founded_date': business_data.get('founded_date'),
                'employee_count': business_data.get('employee_count'),
                'annual_revenue': business_data.get('annual_revenue'),
                'business_description': business_data.get('business_description')
            }
            
            # Store as custom fields for the business profile
            profile_fields = []
            for field_name, field_value in profile_data.items():
                if field_value is not None:
                    profile_field = CustomField.objects.create(
                        model_name='msme_business_profile',
                        record_id=1,  # Will be updated with actual business ID
                        field_name=field_name,
                        field_type=self._get_field_type(field_value),
                        field_value=str(field_value),
                        solution_name='msme_business',
                        created_by=self.user
                    )
                    profile_fields.append(profile_field)
            
            # Create a business profile record
            business_profile = {
                'id': 1,  # Placeholder, will be updated
                'fields': profile_fields,
                'data': profile_data
            }
            
            return business_profile
            
        except Exception as e:
            self.logger.error(f"Failed to create business profile: {str(e)}")
            raise
    
    def _initialize_business_kpis(self, business_data: Dict[str, Any]) -> List[Any]:
        """Initialize standard KPIs for the business type"""
        # Lazy import
        from ..models.msme import MSMEKPI
        
        try:
            business_type = business_data.get('business_type', 'services')
            industry = business_data.get('industry', 'general')
            
            # Get industry-specific KPIs
            standard_kpis = self._get_industry_kpis(business_type, industry)
            
            kpis = []
            for kpi_data in standard_kpis:
                kpi = MSMEKPI.objects.create(
                    solution_name=self.solution_name,
                    kpi_name=kpi_data['name'],
                    kpi_type=kpi_data['type'],
                    current_value=kpi_data.get('current_value', 0),
                    target_value=kpi_data.get('target_value', 0),
                    unit=kpi_data.get('unit', ''),
                    period=kpi_data.get('frequency', 'monthly')
                )
                kpis.append(kpi)
            
            return kpis
            
        except Exception as e:
            self.logger.error(f"Failed to initialize business KPIs: {str(e)}")
            raise
    
    def _get_industry_kpis(self, business_type: str, industry: str) -> List[Dict[str, Any]]:
        """Get industry-specific KPIs"""
        # Base KPIs for all businesses
        base_kpis = [
            {
                'name': 'Monthly Revenue',
                'description': 'Total monthly revenue',
                'type': 'financial',
                'current_value': 0,
                'target_value': 0,
                'unit': 'USD',
                'frequency': 'monthly'
            },
            {
                'name': 'Customer Acquisition Cost',
                'description': 'Cost to acquire new customers',
                'type': 'operational',
                'current_value': 0,
                'target_value': 0,
                'unit': 'USD',
                'frequency': 'monthly'
            },
            {
                'name': 'Customer Satisfaction',
                'description': 'Customer satisfaction score',
                'type': 'customer',
                'current_value': 0,
                'target_value': 85,
                'unit': 'Score',
                'frequency': 'monthly'
            }
        ]
        
        # Add industry-specific KPIs
        if business_type == 'retail':
            base_kpis.extend([
                {
                    'name': 'Inventory Turnover',
                    'description': 'How quickly inventory is sold',
                    'type': 'operational',
                    'current_value': 0,
                    'target_value': 0,
                    'unit': 'Times per year',
                    'frequency': 'monthly'
                },
                {
                    'name': 'Average Transaction Value',
                    'description': 'Average value per customer transaction',
                    'type': 'financial',
                    'current_value': 0,
                    'target_value': 0,
                    'unit': 'USD',
                    'frequency': 'monthly'
                }
            ])
        elif business_type == 'manufacturing':
            base_kpis.extend([
                {
                    'name': 'Production Efficiency',
                    'description': 'Production output vs. capacity',
                    'type': 'operational',
                    'current_value': 0,
                    'target_value': 85,
                    'unit': 'Percentage',
                    'frequency': 'weekly'
                },
                {
                    'name': 'Quality Control Score',
                    'description': 'Product quality rating',
                    'type': 'operational',
                    'current_value': 0,
                    'target_value': 95,
                    'unit': 'Percentage',
                    'frequency': 'weekly'
                }
            ])
        elif business_type == 'services':
            base_kpis.extend([
                {
                    'name': 'Service Delivery Time',
                    'description': 'Average time to deliver services',
                    'type': 'operational',
                    'current_value': 0,
                    'target_value': 0,
                    'unit': 'Days',
                    'frequency': 'weekly'
                },
                {
                    'name': 'Client Retention Rate',
                    'description': 'Percentage of clients retained',
                    'type': 'customer',
                    'current_value': 0,
                    'target_value': 80,
                    'unit': 'Percentage',
                    'frequency': 'monthly'
                }
            ])
        
        return base_kpis
    
    def _setup_compliance_rules(self, business_data: Dict[str, Any]) -> List[Any]:
        """Setup compliance rules for the business"""
        # Lazy import
        from ..models.msme import MSMECompliance
        from django.utils import timezone
        
        try:
            business_type = business_data.get('business_type', 'services')
            industry = business_data.get('industry', 'general')
            
            # Get industry-specific compliance rules
            compliance_rules = self._get_industry_compliance_rules(business_type, industry)
            
            rules = []
            for rule_data in compliance_rules:
                rule = MSMECompliance.objects.create(
                    solution_name=self.solution_name,
                    compliance_type=rule_data['type'],
                    due_date=rule_data['due_date'],
                    status='pending',
                    requirements=rule_data.get('description', ''),
                    notes=rule_data.get('description', '')
                )
                rules.append(rule)
            
            return rules
            
        except Exception as e:
            self.logger.error(f"Failed to setup compliance rules: {str(e)}")
            raise
    
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
        
        # Add industry-specific compliance rules
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
                },
                {
                    'name': 'Safety Inspection',
                    'type': 'health_safety',
                    'due_date': timezone.now().date().replace(month=3, day=31),
                    'description': 'Annual workplace safety inspection'
                }
            ])
        
        return base_rules
    
    def _create_business_templates(self, business_data: Dict[str, Any]) -> List[Any]:
        """Create business document templates"""
        # Lazy import
        from ..models.msme import MSMETemplate
        
        try:
            business_type = business_data.get('business_type', 'services')
            
            # Get industry-specific templates
            templates_data = self._get_industry_templates(business_type)
            
            templates = []
            for template_data in templates_data:
                template = MSMETemplate.objects.create(
                    name=template_data['name'],
                    business_type=template_data['type'],
                    description=template_data['content'],
                    configuration=template_data
                )
                templates.append(template)
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Failed to create business templates: {str(e)}")
            raise
    
    def _get_industry_templates(self, business_type: str) -> List[Dict[str, Any]]:
        """Get industry-specific document templates"""
        # Base templates for all businesses
        base_templates = [
            {
                'name': 'Invoice Template',
                'type': 'invoice',
                'content': self._get_invoice_template(),
                'is_default': True
            },
            {
                'name': 'Quotation Template',
                'type': 'quotation',
                'content': self._get_quotation_template(),
                'is_default': True
            }
        ]
        
        # Add industry-specific templates
        if business_type == 'retail':
            base_templates.extend([
                {
                    'name': 'Receipt Template',
                    'type': 'receipt',
                    'content': self._get_receipt_template(),
                    'is_default': True
                }
            ])
        elif business_type == 'manufacturing':
            base_templates.extend([
                {
                    'name': 'Purchase Order Template',
                    'type': 'purchase_order',
                    'content': self._get_purchase_order_template(),
                    'is_default': True
                }
            ])
        
        return base_templates
    
    def _initialize_business_analytics(self, business_data: Dict[str, Any]) -> List[Any]:
        """Initialize business analytics and metrics"""
        # Lazy import
        from ..models.msme import MSMEAnalytics
        from django.utils import timezone
        
        try:
            business_type = business_data.get('business_type', 'services')
            
            # Get industry-specific analytics
            analytics_data = self._get_industry_analytics(business_type)
            
            analytics = []
            for metric_data in analytics_data:
                metric = MSMEAnalytics.objects.create(
                    solution_name=self.solution_name,
                    metric_name=metric_data['name'],
                    metric_value=metric_data.get('value', 0),
                    date=timezone.now().date(),
                    metric_type=metric_data['type']
                )
                analytics.append(metric)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to initialize business analytics: {str(e)}")
            raise
    
    def _get_industry_analytics(self, business_type: str) -> List[Dict[str, Any]]:
        """Get industry-specific analytics metrics"""
        # Base analytics for all businesses
        base_analytics = [
            {
                'name': 'Total Revenue',
                'value': 0,
                'type': 'revenue'
            },
            {
                'name': 'Total Expenses',
                'value': 0,
                'type': 'expenses'
            },
            {
                'name': 'Net Profit',
                'value': 0,
                'type': 'profit'
            },
            {
                'name': 'Customer Count',
                'value': 0,
                'type': 'customers'
            }
        ]
        
        # Add industry-specific analytics
        if business_type == 'retail':
            base_analytics.extend([
                {
                    'name': 'Inventory Value',
                    'value': 0,
                    'type': 'inventory'
                },
                {
                    'name': 'Sales Transactions',
                    'value': 0,
                    'type': 'orders'
                }
            ])
        elif business_type == 'manufacturing':
            base_analytics.extend([
                {
                    'name': 'Production Units',
                    'value': 0,
                    'type': 'production'
                },
                {
                    'name': 'Raw Material Cost',
                    'value': 0,
                    'type': 'costs'
                }
            ])
        
        return base_analytics
    
    def _get_field_type(self, value: Any) -> str:
        """Determine the appropriate field type for a value"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, dict):
            return 'json'
        else:
            return 'text'
    
    def _get_next_setup_steps(self, current_stage: str) -> List[str]:
        """Get next steps for business setup"""
        setup_stages = {
            'initial': ['Complete basic information', 'Configure business settings'],
            'basic_info': ['Select business modules', 'Configure workflows'],
            'modules': ['Test configurations', 'Validate setup'],
            'configuration': ['Run system tests', 'Verify integrations'],
            'testing': ['Complete setup', 'Launch business'],
            'complete': ['Setup complete', 'Business ready']
        }
        
        return setup_stages.get(current_stage, ['Setup in progress'])
    
    def get_business_profile(self, business_id: int) -> Dict[str, Any]:
        """Get business profile information"""
        try:
            # Get business profile from custom fields
            profile_fields = CustomField.objects.filter(
                model_name='msme_business_profile',
                record_id=business_id,
                solution_name='msme_business',
                is_active=True
            )
            
            profile_data = {}
            for field in profile_fields:
                profile_data[field.field_name] = field.field_value
            
            return {
                'success': True,
                'business_id': business_id,
                'profile': profile_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get business profile: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get business profile'
            }
    
    def update_business_profile(self, business_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update business profile information"""
        try:
            with transaction.atomic():
                updated_fields = []
                
                for field_name, field_value in updates.items():
                    if field_value is not None:
                        # Update existing field or create new one
                        field, created = CustomField.objects.update_or_create(
                            model_name='msme_business_profile',
                            record_id=business_id,
                            field_name=field_name,
                            solution_name='msme_business',
                            defaults={
                                'field_type': self._get_field_type(field_value),
                                'field_value': str(field_value),
                                'is_active': True
                            }
                        )
                        updated_fields.append(field_name)
                
                self.logger.info(f"Business profile updated: {updated_fields}")
                
                return {
                    'success': True,
                    'business_id': business_id,
                    'updated_fields': updated_fields,
                    'message': 'Business profile updated successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to update business profile: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to update business profile'
            }
    
    def get_business_kpis(self, business_id: int) -> Dict[str, Any]:
        """Get business KPIs and performance metrics"""
        # Lazy import
        from ..models.msme import MSMEKPI
        
        try:
            kpis = MSMEKPI.objects.filter(solution_name=self.solution_name)
            
            kpi_data = []
            for kpi in kpis:
                kpi_data.append({
                    'id': kpi.id,
                    'name': kpi.kpi_name,
                    'type': kpi.kpi_type,
                    'current_value': float(kpi.current_value),
                    'target_value': float(kpi.current_value) if kpi.target_value else None,
                    'unit': kpi.unit,
                    'period': kpi.period,
                    'performance': self._calculate_kpi_performance(kpi)
                })
            
            return {
                'success': True,
                'business_id': business_id,
                'kpis': kpi_data,
                'total_kpis': len(kpi_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get business KPIs: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get business KPIs'
            }
    
    def _calculate_kpi_performance(self, kpi: Any) -> Dict[str, Any]:
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
    
    # Template content methods
    def _get_invoice_template(self) -> str:
        return """INVOICE
Company: {company_name}
Invoice #: {invoice_number}
Date: {invoice_date}
Due Date: {due_date}

Customer: {customer_name}
Address: {customer_address}

Items:
{items}

Subtotal: {subtotal}
Tax: {tax}
Total: {total}

Payment Terms: {payment_terms}"""
    
    def _get_quotation_template(self) -> str:
        return """QUOTATION
Company: {company_name}
Quote #: {quote_number}
Date: {quote_date}
Valid Until: {valid_until}

Customer: {customer_name}
Address: {customer_address}

Services/Products:
{items}

Subtotal: {subtotal}
Tax: {tax}
Total: {total}

Terms & Conditions: {terms}"""
    
    def _get_receipt_template(self) -> str:
        return """RECEIPT
Company: {company_name}
Receipt #: {receipt_number}
Date: {receipt_date}
Time: {receipt_time}

Customer: {customer_name}

Items:
{items}

Subtotal: {subtotal}
Tax: {tax}
Total: {total}
Amount Paid: {amount_paid}
Change: {change}

Thank you for your business!"""
    
    def _get_purchase_order_template(self) -> str:
        return """PURCHASE ORDER
Company: {company_name}
PO #: {po_number}
Date: {po_date}
Required By: {required_by}

Supplier: {supplier_name}
Address: {supplier_address}

Items:
{items}

Subtotal: {subtotal}
Tax: {tax}
Total: {total}

Delivery Terms: {delivery_terms}
Payment Terms: {payment_terms}"""
