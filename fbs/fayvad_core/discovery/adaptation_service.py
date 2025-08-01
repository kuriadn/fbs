import logging
from typing import Dict, Any, List
from django.conf import settings

logger = logging.getLogger(__name__)

class FBSAdaptationService:
    """
    Service for adapting discovered Odoo modules to specific business domains.
    Maps existing Odoo functionality to business needs without requiring custom modules.
    """
    
    def __init__(self):
        self.adaptation_rules = self._load_adaptation_rules()
    
    def _load_adaptation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load adaptation rules for different business domains"""
        return {
            'rental': {
                'model_mappings': {
                    'product.template': {
                        'business_model': 'rental_property',
                        'field_mappings': {
                            'name': 'property_name',
                            'description': 'property_description',
                            'list_price': 'rental_price',
                            'default_code': 'property_code',
                            'categ_id': 'property_category',
                            'active': 'is_available'
                        },
                        'business_logic': {
                            'availability_check': 'active = True',
                            'pricing_logic': 'list_price as monthly_rent'
                        }
                    },
                    'sale.order': {
                        'business_model': 'rental_lease',
                        'field_mappings': {
                            'name': 'lease_number',
                            'partner_id': 'tenant_id',
                            'date_order': 'lease_start_date',
                            'amount_total': 'total_rent_amount',
                            'state': 'lease_status'
                        },
                        'business_logic': {
                            'status_mapping': {
                                'draft': 'pending',
                                'sent': 'negotiating',
                                'sale': 'active',
                                'done': 'completed',
                                'cancel': 'cancelled'
                            }
                        }
                    },
                    'res.partner': {
                        'business_model': 'rental_tenant',
                        'field_mappings': {
                            'name': 'tenant_name',
                            'email': 'tenant_email',
                            'phone': 'tenant_phone',
                            'street': 'tenant_address',
                            'city': 'tenant_city',
                            'country_id': 'tenant_country',
                            'customer_rank': 'tenant_rating'
                        },
                        'business_logic': {
                            'tenant_type': 'customer_rank > 0',
                            'contact_info': 'email, phone required'
                        }
                    },
                    'account.move': {
                        'business_model': 'rental_payment',
                        'field_mappings': {
                            'name': 'payment_reference',
                            'partner_id': 'tenant_id',
                            'invoice_date': 'payment_date',
                            'amount_total': 'payment_amount',
                            'state': 'payment_status'
                        },
                        'business_logic': {
                            'status_mapping': {
                                'draft': 'pending',
                                'posted': 'paid',
                                'cancel': 'cancelled'
                            }
                        }
                    }
                },
                'workflow_mappings': {
                    'sale.order': {
                        'business_workflow': 'lease_management',
                        'state_mappings': {
                            'draft': 'lease_application',
                            'sent': 'lease_negotiation',
                            'sale': 'lease_active',
                            'done': 'lease_completed',
                            'cancel': 'lease_cancelled'
                        }
                    },
                    'account.move': {
                        'business_workflow': 'payment_processing',
                        'state_mappings': {
                            'draft': 'payment_pending',
                            'posted': 'payment_confirmed',
                            'cancel': 'payment_cancelled'
                        }
                    }
                },
                'bi_mappings': {
                    'sale.order': {
                        'business_reports': [
                            'Rental Income Report',
                            'Lease Performance Analysis',
                            'Tenant Occupancy Report'
                        ],
                        'business_dashboards': [
                            'Property Management Dashboard',
                            'Tenant Analytics',
                            'Revenue Performance'
                        ],
                        'business_metrics': [
                            'Total Rental Income',
                            'Average Lease Duration',
                            'Occupancy Rate'
                        ]
                    },
                    'account.move': {
                        'business_reports': [
                            'Rent Collection Report',
                            'Payment History',
                            'Outstanding Payments'
                        ],
                        'business_dashboards': [
                            'Financial Dashboard',
                            'Payment Analytics',
                            'Cash Flow Analysis'
                        ],
                        'business_metrics': [
                            'Total Collections',
                            'Payment Success Rate',
                            'Average Payment Time'
                        ]
                    }
                }
            },
            'ecommerce': {
                'model_mappings': {
                    'product.template': {
                        'business_model': 'ecommerce_product',
                        'field_mappings': {
                            'name': 'product_name',
                            'description': 'product_description',
                            'list_price': 'product_price',
                            'default_code': 'sku',
                            'categ_id': 'product_category'
                        }
                    },
                    'sale.order': {
                        'business_model': 'ecommerce_order',
                        'field_mappings': {
                            'name': 'order_number',
                            'partner_id': 'customer_id',
                            'date_order': 'order_date',
                            'amount_total': 'order_total'
                        }
                    }
                }
            },
            'hr': {
                'model_mappings': {
                    'hr.employee': {
                        'business_model': 'hr_employee',
                        'field_mappings': {
                            'name': 'employee_name',
                            'job_title': 'position',
                            'department_id': 'department',
                            'work_email': 'email',
                            'work_phone': 'phone'
                        }
                    }
                }
            }
        }
    
    def adapt_discoveries(self, domain: str, discoveries: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt discovered Odoo modules to business domain needs.
        
        Args:
            domain: Business domain (e.g., 'rental', 'ecommerce', 'hr')
            discoveries: Raw discovery results from Odoo
            
        Returns:
            Adapted discoveries with business domain mappings
        """
        try:
            if domain not in self.adaptation_rules:
                logger.warning(f"No adaptation rules found for domain: {domain}")
                return discoveries
            
            rules = self.adaptation_rules[domain]
            adapted_discoveries = {
                'domain': domain,
                'original_discoveries': discoveries,
                'adapted_models': {},
                'adapted_workflows': {},
                'adapted_bi_features': {},
                'business_mappings': rules
            }
            
            # Adapt models
            if 'models' in discoveries and discoveries['models'].get('status') == 'success':
                adapted_discoveries['adapted_models'] = self._adapt_models(
                    domain, discoveries['models'].get('discovered_models', {}), rules
                )
            
            # Adapt workflows
            if 'workflows' in discoveries and discoveries['workflows'].get('status') == 'success':
                adapted_discoveries['adapted_workflows'] = self._adapt_workflows(
                    domain, discoveries['workflows'].get('discovered_workflows', {}), rules
                )
            
            # Adapt BI features
            if 'bi_features' in discoveries and discoveries['bi_features'].get('status') == 'success':
                adapted_discoveries['adapted_bi_features'] = self._adapt_bi_features(
                    domain, discoveries['bi_features'].get('discovered_bi_features', {}), rules
                )
            
            return adapted_discoveries
            
        except Exception as e:
            logger.error(f"Error adapting discoveries for domain {domain}: {str(e)}")
            return {
                'domain': domain,
                'error': str(e),
                'original_discoveries': discoveries
            }
    
    def _adapt_models(self, domain: str, models: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt discovered models to business domain models"""
        adapted_models = {}
        
        for model_name, model_data in models.items():
            if model_name in rules.get('model_mappings', {}):
                mapping = rules['model_mappings'][model_name]
                adapted_models[model_name] = {
                    'original_model': model_name,
                    'business_model': mapping['business_model'],
                    'field_mappings': mapping.get('field_mappings', {}),
                    'business_logic': mapping.get('business_logic', {}),
                    'original_data': model_data,
                    'adaptation_notes': f"Adapted {model_name} to {mapping['business_model']} for {domain} domain"
                }
            else:
                # Keep original model if no mapping exists
                adapted_models[model_name] = {
                    'original_model': model_name,
                    'business_model': model_name,
                    'field_mappings': {},
                    'business_logic': {},
                    'original_data': model_data,
                    'adaptation_notes': f"No specific adaptation for {model_name} in {domain} domain"
                }
        
        return adapted_models
    
    def _adapt_workflows(self, domain: str, workflows: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt discovered workflows to business domain workflows"""
        adapted_workflows = {}
        
        for workflow_name, workflow_data in workflows.items():
            if workflow_name in rules.get('workflow_mappings', {}):
                mapping = rules['workflow_mappings'][workflow_name]
                adapted_workflows[workflow_name] = {
                    'original_workflow': workflow_name,
                    'business_workflow': mapping['business_workflow'],
                    'state_mappings': mapping.get('state_mappings', {}),
                    'original_data': workflow_data,
                    'adaptation_notes': f"Adapted {workflow_name} to {mapping['business_workflow']} for {domain} domain"
                }
            else:
                # Keep original workflow if no mapping exists
                adapted_workflows[workflow_name] = {
                    'original_workflow': workflow_name,
                    'business_workflow': workflow_name,
                    'state_mappings': {},
                    'original_data': workflow_data,
                    'adaptation_notes': f"No specific adaptation for {workflow_name} in {domain} domain"
                }
        
        return adapted_workflows
    
    def _adapt_bi_features(self, domain: str, bi_features: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt discovered BI features to business domain BI features"""
        adapted_bi_features = {}
        
        for bi_name, bi_data in bi_features.items():
            if bi_name in rules.get('bi_mappings', {}):
                mapping = rules['bi_mappings'][bi_name]
                adapted_bi_features[bi_name] = {
                    'original_bi': bi_name,
                    'business_reports': mapping.get('business_reports', []),
                    'business_dashboards': mapping.get('business_dashboards', []),
                    'business_metrics': mapping.get('business_metrics', []),
                    'original_data': bi_data,
                    'adaptation_notes': f"Adapted {bi_name} BI features for {domain} domain"
                }
            else:
                # Keep original BI features if no mapping exists
                adapted_bi_features[bi_name] = {
                    'original_bi': bi_name,
                    'business_reports': bi_data.get('reports', []),
                    'business_dashboards': bi_data.get('dashboards', []),
                    'business_metrics': bi_data.get('metrics', []),
                    'original_data': bi_data,
                    'adaptation_notes': f"No specific adaptation for {bi_name} in {domain} domain"
                }
        
        return adapted_bi_features
    
    def get_adaptation_summary(self, domain: str, discoveries: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of adaptations for a domain"""
        adapted = self.adapt_discoveries(domain, discoveries)
        
        summary = {
            'domain': domain,
            'total_models': len(adapted.get('adapted_models', {})),
            'total_workflows': len(adapted.get('adapted_workflows', {})),
            'total_bi_features': len(adapted.get('adapted_bi_features', {})),
            'adaptation_coverage': {
                'models_with_mappings': sum(1 for m in adapted.get('adapted_models', {}).values() 
                                          if m.get('business_model') != m.get('original_model')),
                'workflows_with_mappings': sum(1 for w in adapted.get('adapted_workflows', {}).values() 
                                             if w.get('business_workflow') != w.get('original_workflow')),
                'bi_features_with_mappings': sum(1 for b in adapted.get('adapted_bi_features', {}).values() 
                                               if b.get('business_reports') or b.get('business_dashboards'))
            }
        }
        
        return summary 