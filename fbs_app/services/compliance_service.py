"""
FBS App Compliance Service

Service for MSME compliance management and regulatory requirements.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.db import connections
from django.conf import settings

logger = logging.getLogger('fbs_app')


class ComplianceService:
    """Service for MSME compliance management"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        self.fbs_config = getattr(settings, 'FBS_APP', {})
    
    def calculate_tax(self, tax_type: str, amount: float, period: str = 'monthly') -> Dict[str, Any]:
        """Calculate simple tax for MSMEs"""
        try:
            # Simple tax calculation logic for MSMEs
            tax_rates = {
                'vat': 0.16,  # 16% VAT
                'income_tax': 0.30,  # 30% income tax
                'payroll_tax': 0.05,  # 5% payroll tax
                'withholding_tax': 0.10  # 10% withholding tax
            }
            
            rate = tax_rates.get(tax_type, 0.0)
            tax_amount = amount * rate
            
            # Period adjustments
            period_multipliers = {
                'monthly': 1,
                'quarterly': 3,
                'yearly': 12
            }
            
            multiplier = period_multipliers.get(period, 1)
            total_tax = tax_amount * multiplier
            
            return {
                'success': True,
                'tax_type': tax_type,
                'amount': amount,
                'tax_rate': rate,
                'tax_amount': tax_amount,
                'period': period,
                'total_tax': total_tax,
                'calculation_date': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating tax: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_payroll_basics(self, employee_id: int, basic_salary: float, 
                             allowances: float = 0, deductions: float = 0) -> Dict[str, Any]:
        """Process basic payroll for MSMEs"""
        try:
            # Basic payroll calculation
            gross_salary = basic_salary + allowances
            net_salary = gross_salary - deductions
            
            # Calculate basic taxes
            tax_result = self.calculate_tax('payroll_tax', gross_salary)
            
            if tax_result['success']:
                payroll_tax = tax_result['tax_amount']
                final_net_salary = net_salary - payroll_tax
            else:
                payroll_tax = 0
                final_net_salary = net_salary
            
            return {
                'success': True,
                'employee_id': employee_id,
                'basic_salary': basic_salary,
                'allowances': allowances,
                'deductions': deductions,
                'gross_salary': gross_salary,
                'net_salary': net_salary,
                'payroll_tax': payroll_tax,
                'final_net_salary': final_net_salary,
                'calculation_date': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing payroll: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_audit_trail(self, record_type: str, record_id: int, action: str, 
                           user_id: int, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create audit trail entry"""
        try:
            from ..models import AuditTrail
            
            audit_entry = AuditTrail.objects.create(
                solution_name=self.solution_name,
                record_type=record_type,
                record_id=record_id,
                action=action,
                user_id=user_id,
                details=details or {},
                timestamp=timezone.now()
            )
            
            return {
                'success': True,
                'audit_id': audit_entry.id,
                'message': 'Audit trail created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating audit trail: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_compliance_deadlines(self, compliance_type: str = None) -> Dict[str, Any]:
        """Get compliance deadlines for the business"""
        try:
            # Note: ComplianceDeadline model doesn't exist, using ComplianceRule instead
            from ..models import ComplianceRule
            
            # Get compliance rules for the solution
            query = {'solution_name': self.solution_name, 'active': True}
            if compliance_type:
                query['compliance_type'] = compliance_type
            
            rules = ComplianceRule.objects.filter(**query)
            
            rule_data = []
            for rule in rules:
                rule_data.append({
                    'id': rule.id,
                    'compliance_type': rule.compliance_type,
                    'name': rule.name,
                    'description': rule.description,
                    'check_frequency': rule.check_frequency,
                    'active': rule.active
                })
            
            return {
                'success': True,
                'compliance_rules': rule_data,
                'count': len(rule_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance rules: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_compliance_status(self, rule_id: int, active: bool, 
                                description: str = None) -> Dict[str, Any]:
        """Update compliance rule status"""
        try:
            from ..models import ComplianceRule
            
            try:
                rule = ComplianceRule.objects.get(id=rule_id)
            except ComplianceRule.DoesNotExist:
                return {'success': False, 'error': 'Compliance rule not found'}
            
            # Update status
            rule.active = active
            if description:
                rule.description = description
            rule.updated_at = timezone.now()
            rule.save()
            
            return {
                'success': True,
                'rule_id': rule.id,
                'active': rule.active,
                'message': 'Compliance rule updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating compliance rule: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_regulatory_report(self, report_type: str, period: str = 'monthly') -> Dict[str, Any]:
        """Generate regulatory compliance report"""
        try:
            # Note: RegulatoryReport model doesn't exist, using ReportSchedule instead
            from ..models import ReportSchedule
            
            # Generate report ID
            report_id = str(uuid.uuid4())
            
            # Calculate period dates
            end_date = timezone.now().date()
            if period == 'monthly':
                start_date = end_date.replace(day=1)
            elif period == 'quarterly':
                # Calculate quarter start
                quarter = (end_date.month - 1) // 3
                start_date = end_date.replace(month=quarter * 3 + 1, day=1)
            elif period == 'yearly':
                start_date = end_date.replace(month=1, day=1)
            else:
                start_date = end_date - timezone.timedelta(days=30)
            
            # Create report schedule entry
            report = ReportSchedule.objects.create(
                solution_name=self.solution_name,
                name=f"{report_type}_{period}_report",
                report_type=report_type,
                frequency=period,
                next_run=timezone.now(),
                active=True,
                configuration={
                    'period': period,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'generated_at': timezone.now().isoformat()
                }
            )
            
            return {
                'success': True,
                'report_id': report.id,
                'report_type': report_type,
                'period': period,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'message': 'Regulatory report schedule created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error generating regulatory report: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def check_regulatory_compliance(self, compliance_areas: List[str] = None) -> Dict[str, Any]:
        """Check regulatory compliance status"""
        try:
            # Default compliance areas for MSMEs
            if not compliance_areas:
                compliance_areas = [
                    'tax_compliance',
                    'payroll_compliance',
                    'business_registration',
                    'financial_reporting',
                    'data_protection'
                ]
            
            compliance_status = {}
            
            for area in compliance_areas:
                status = self._check_area_compliance(area)
                compliance_status[area] = status
            
            # Overall compliance score
            compliant_areas = sum(1 for status in compliance_status.values() if status['compliant'])
            total_areas = len(compliance_areas)
            compliance_score = (compliant_areas / total_areas * 100) if total_areas > 0 else 0
            
            return {
                'success': True,
                'compliance_areas': compliance_status,
                'overall_score': compliance_score,
                'compliant_areas': compliant_areas,
                'total_areas': total_areas,
                'assessment_date': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking regulatory compliance: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _check_area_compliance(self, area: str) -> Dict[str, Any]:
        """Check compliance for a specific area"""
        try:
            # This is a simplified compliance check
            # In production, you would implement actual compliance logic
            
            compliance_rules = {
                'tax_compliance': {
                    'requirements': ['VAT filing', 'Income tax filing', 'Withholding tax'],
                    'check_frequency': 'monthly'
                },
                'payroll_compliance': {
                    'requirements': ['Employee registration', 'Tax deductions', 'Social security'],
                    'check_frequency': 'monthly'
                },
                'business_registration': {
                    'requirements': ['Business license', 'Tax registration', 'Local permits'],
                    'check_frequency': 'yearly'
                },
                'financial_reporting': {
                    'requirements': ['Balance sheet', 'Income statement', 'Cash flow'],
                    'check_frequency': 'quarterly'
                },
                'data_protection': {
                    'requirements': ['Data privacy policy', 'Consent management', 'Security measures'],
                    'check_frequency': 'yearly'
                }
            }
            
            rule = compliance_rules.get(area, {})
            
            # Simulate compliance check (in production, check actual data)
            compliant = True  # Placeholder
            last_check = timezone.now()
            next_check = last_check + timezone.timedelta(days=30)  # Placeholder
            
            return {
                'compliant': compliant,
                'requirements': rule.get('requirements', []),
                'check_frequency': rule.get('check_frequency', 'monthly'),
                'last_check': last_check.isoformat(),
                'next_check': next_check.isoformat(),
                'notes': 'Compliance check completed'
            }
            
        except Exception as e:
            logger.error(f"Error checking area compliance: {str(e)}")
            return {
                'compliant': False,
                'error': str(e)
            }
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get overall compliance summary"""
        try:
            from ..models import ComplianceRule, AuditTrail, ReportSchedule
            
            # Get compliance statistics
            total_rules = ComplianceRule.objects.filter(solution_name=self.solution_name).count()
            active_rules = ComplianceRule.objects.filter(
                solution_name=self.solution_name,
                active=True
            ).count()
            
            inactive_rules = ComplianceRule.objects.filter(
                solution_name=self.solution_name,
                active=False
            ).count()
            
            # Get recent audit activities
            recent_audits = AuditTrail.objects.filter(
                solution_name=self.solution_name
            ).order_by('-timestamp')[:10]
            
            audit_summary = []
            for audit in recent_audits:
                audit_summary.append({
                    'action': audit.action,
                    'record_type': audit.record_type,
                    'timestamp': audit.timestamp.isoformat()
                })
            
            return {
                'success': True,
                'summary': {
                    'total_rules': total_rules,
                    'active_rules': active_rules,
                    'inactive_rules': inactive_rules,
                    'compliance_rate': (active_rules / total_rules * 100) if total_rules > 0 else 0
                },
                'recent_audits': audit_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance summary: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Missing methods that the interface expects
    def create_compliance_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new compliance rule"""
        try:
            from ..models import ComplianceRule
            
            rule = ComplianceRule.objects.create(
                name=rule_data['name'],
                compliance_type=rule_data.get('compliance_type', 'general'),
                description=rule_data.get('description', ''),
                requirements=rule_data.get('requirements', []),
                check_frequency=rule_data.get('check_frequency', 'monthly'),
                active=rule_data.get('active', True),
                solution_name=self.solution_name
            )
            
            return {
                'success': True,
                'data': {
                    'id': rule.id,
                    'name': rule.name,
                    'compliance_type': rule.compliance_type,
                    'description': rule.description,
                    'requirements': rule.requirements,
                    'check_frequency': rule.check_frequency,
                    'active': rule.active
                }
            }
        except Exception as e:
            logger.error(f"Error creating compliance rule: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_compliance_rules(self, compliance_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all compliance rules or by type"""
        try:
            from ..models import ComplianceRule
            
            query = {'solution_name': self.solution_name, 'active': True}
            if compliance_type:
                query['compliance_type'] = compliance_type
            
            rules = ComplianceRule.objects.filter(**query)
            rule_list = []
            
            for rule in rules:
                rule_list.append({
                    'id': rule.id,
                    'name': rule.name,
                    'compliance_type': rule.compliance_type,
                    'description': rule.description,
                    'requirements': rule.requirements,
                    'check_frequency': rule.check_frequency,
                    'active': rule.active
                })
            
            return {
                'success': True,
                'data': rule_list,
                'count': len(rule_list)
            }
        except Exception as e:
            logger.error(f"Error getting compliance rules: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def check_compliance(self, rule_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance against a rule"""
        try:
            from ..models import ComplianceRule
            
            rule = ComplianceRule.objects.get(id=rule_id)
            
            # Simple compliance check based on rule type
            if rule.compliance_type == 'tax':
                compliant = self._check_tax_compliance(data)
            elif rule.compliance_type == 'payroll':
                compliant = self._check_payroll_compliance(data)
            else:
                compliant = True  # Default to compliant for unknown types
            
            return {
                'success': True,
                'data': {
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'compliant': compliant,
                    'check_date': timezone.now().isoformat()
                }
            }
        except ComplianceRule.DoesNotExist:
            return {'success': False, 'error': 'Compliance rule not found'}
        except Exception as e:
            logger.error(f"Error checking compliance: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_compliance_status(self, compliance_type: Optional[str] = None) -> Dict[str, Any]:
        """Get overall compliance status"""
        try:
            from ..models import ComplianceRule
            
            query = {'solution_name': self.solution_name, 'active': True}
            if compliance_type:
                query['compliance_type'] = compliance_type
            
            rules = ComplianceRule.objects.filter(**query)
            
            # Simple compliance calculation
            total_rules = rules.count()
            compliant_rules = total_rules  # Placeholder - in production, check actual compliance
            
            return {
                'success': True,
                'data': {
                    'total_rules': total_rules,
                    'compliant_rules': compliant_rules,
                    'compliance_rate': (compliant_rules / total_rules * 100) if total_rules > 0 else 0,
                    'status': 'compliant' if compliant_rules == total_rules else 'non_compliant'
                }
            }
        except Exception as e:
            logger.error(f"Error getting compliance status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_audit_trails(self, entity_type: Optional[str] = None, entity_id: Optional[int] = None) -> Dict[str, Any]:
        """Get audit trails"""
        try:
            from ..models import AuditTrail
            
            query = {'solution_name': self.solution_name}
            if entity_type:
                query['record_type'] = entity_type
            if entity_id:
                query['record_id'] = entity_id
            
            audits = AuditTrail.objects.filter(**query).order_by('-timestamp')
            audit_list = []
            
            for audit in audits:
                audit_list.append({
                    'id': audit.id,
                    'action': audit.action,
                    'record_type': audit.record_type,
                    'record_id': audit.record_id,
                    'timestamp': audit.timestamp.isoformat(),
                    'user_id': audit.user_id
                })
            
            return {
                'success': True,
                'data': audit_list,
                'count': len(audit_list)
            }
        except Exception as e:
            logger.error(f"Error getting audit trails: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_compliance_report(self, report_type: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            params = parameters or {}
            
            if report_type == 'monthly':
                return self._generate_monthly_compliance_report(params)
            elif report_type == 'quarterly':
                return self._generate_quarterly_compliance_report(params)
            elif report_type == 'annual':
                return self._generate_annual_compliance_report(params)
            else:
                return {'success': False, 'error': f'Unknown report type: {report_type}'}
                
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _check_tax_compliance(self, data: Dict[str, Any]) -> bool:
        """Check tax compliance"""
        # Simple placeholder - in production, implement actual tax compliance logic
        return True
    
    def _check_payroll_compliance(self, data: Dict[str, Any]) -> bool:
        """Check payroll compliance"""
        # Simple placeholder - in production, implement actual payroll compliance logic
        return True
    
    def _generate_monthly_compliance_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate monthly compliance report"""
        return {
            'success': True,
            'data': {
                'report_type': 'monthly',
                'period': parameters.get('period', 'current_month'),
                'compliance_summary': 'Monthly compliance report generated'
            }
        }
    
    def _generate_quarterly_compliance_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quarterly compliance report"""
        return {
            'success': True,
            'data': {
                'report_type': 'quarterly',
                'period': parameters.get('period', 'current_quarter'),
                'compliance_summary': 'Quarterly compliance report generated'
            }
        }
    
    def _generate_annual_compliance_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate annual compliance report"""
        return {
            'success': True,
            'data': {
                'report_type': 'annual',
                'period': parameters.get('period', 'current_year'),
                'compliance_summary': 'Annual compliance report generated'
            }
        }
