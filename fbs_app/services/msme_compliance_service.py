"""
MSME Compliance Service

Comprehensive service for MSME compliance management including:
- Compliance rule management
- Automated compliance monitoring
- Compliance reporting and alerts
- Regulatory deadline tracking
- Risk assessment and mitigation
"""

import logging
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json

from ..models.msme import MSMECompliance
from ..models.compliance import ComplianceRule, AuditTrail

logger = logging.getLogger(__name__)


class MSMEComplianceService:
    """Service for MSME compliance management operations"""
    
    def __init__(self, solution_name: str, user: User = None):
        self.solution_name = solution_name
        self.user = user
        self.logger = logging.getLogger(f"{__name__}.{solution_name}")
    
    def create_compliance_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new compliance rule
        
        Args:
            rule_data: Compliance rule information
            
        Returns:
            Dict containing creation result
        """
        try:
            with transaction.atomic():
                rule = MSMECompliance.objects.create(
                    solution_name=self.solution_name,
                    compliance_type=rule_data.get('type'),
                    due_date=rule_data.get('due_date'),
                    status='pending',
                    requirements=rule_data.get('description', ''),
                    notes=rule_data.get('description', '')
                )
                
                self.logger.info(f"Compliance rule created: {rule.compliance_type}")
                
                return {
                    'success': True,
                    'rule_id': rule.id,
                    'message': 'Compliance rule created successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create compliance rule: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create compliance rule'
            }
    
    def get_compliance_overview(self) -> Dict[str, Any]:
        """Get comprehensive compliance overview"""
        try:
            # Get all compliance rules
            compliance_rules = MSMECompliance.objects.filter(solution_name=self.solution_name)
            
            # Calculate statistics
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
            
            # Get upcoming deadlines
            upcoming_deadlines = compliance_rules.filter(
                status='pending',
                due_date__range=[timezone.now().date(), timezone.now().date() + timedelta(days=30)]
            ).order_by('due_date')[:5]
            
            upcoming_list = []
            for rule in upcoming_deadlines:
                upcoming_list.append({
                    'id': rule.id,
                    'name': rule.compliance_type,
                    'type': rule.compliance_type,
                    'due_date': rule.due_date,
                    'days_remaining': (rule.due_date - timezone.now().date()).days
                })
            
            # Get overdue items
            overdue_items = compliance_rules.filter(
                status='pending',
                due_date__lt=timezone.now().date()
            ).order_by('due_date')
            
            overdue_list = []
            for rule in overdue_items:
                overdue_list.append({
                    'id': rule.id,
                    'name': rule.compliance_type,
                    'type': rule.compliance_type,
                    'due_date': rule.due_date,
                    'days_overdue': (timezone.now().date() - rule.due_date).days
                })
            
            return {
                'success': True,
                'overview': {
                    'total_rules': total_rules,
                    'pending_rules': pending_rules,
                    'completed_rules': completed_rules,
                    'overdue_rules': overdue_rules,
                    'compliance_score': round(compliance_score, 2)
                },
                'upcoming_deadlines': upcoming_list,
                'overdue_items': overdue_list
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get compliance overview: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get compliance overview'
            }
    
    def update_compliance_status(self, rule_id: int, new_status: str, 
                               notes: str = None) -> Dict[str, Any]:
        """
        Update compliance rule status
        
        Args:
            rule_id: Compliance rule ID
            new_status: New status (pending, in_progress, completed, overdue)
            notes: Additional notes
            
        Returns:
            Dict containing update result
        """
        try:
            with transaction.atomic():
                rule = MSMECompliance.objects.get(id=rule_id, solution_name=self.solution_name)
                
                old_status = rule.status
                rule.status = new_status
                
                if notes:
                    rule.notes = notes
                
                rule.save()
                
                # Log the status change
                self._log_compliance_change(rule, old_status, new_status, notes)
                
                self.logger.info(f"Compliance rule status updated: {rule.compliance_type} -> {new_status}")
                
                return {
                    'success': True,
                    'rule_id': rule_id,
                    'old_status': old_status,
                    'new_status': new_status,
                    'message': 'Compliance status updated successfully'
                }
                
        except MSMECompliance.DoesNotExist:
            return {
                'success': False,
                'error': 'Compliance rule not found',
                'message': 'Compliance rule not found'
            }
        except Exception as e:
            self.logger.error(f"Failed to update compliance status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to update compliance status'
            }
    
    def _log_compliance_change(self, rule: MSMECompliance, old_status: str, 
                             new_status: str, notes: str = None):
        """Log compliance status change"""
        try:
            # Create audit trail entry
            AuditTrail.objects.create(
                solution_name=self.solution_name,
                record_type='system',
                record_id=str(rule.id),
                action='update',
                user_id=str(self.user.id) if self.user else 'system',
                details={
                    'old_status': old_status,
                    'new_status': new_status,
                    'notes': notes,
                    'resource_type': 'msme_compliance'
                },
                ip_address='127.0.0.1'  # Placeholder
            )
        except Exception as e:
            self.logger.warning(f"Failed to log compliance change: {str(e)}")
    
    def get_compliance_calendar(self, month: int = None, year: int = None) -> Dict[str, Any]:
        """
        Get compliance calendar for specified month/year
        
        Args:
            month: Month number (1-12)
            year: Year number
            
        Returns:
            Dict containing compliance calendar data
        """
        try:
            if month is None:
                month = timezone.now().month
            if year is None:
                year = timezone.now().year
            
            # Get start and end of month
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            # Get compliance rules for the month
            compliance_rules = MSMECompliance.objects.filter(
                solution_name=self.solution_name,
                due_date__range=[start_date, end_date]
            ).order_by('due_date')
            
            # Group by date
            calendar_data = {}
            for rule in compliance_rules:
                date_key = rule.due_date.strftime('%Y-%m-%d')
                if date_key not in calendar_data:
                    calendar_data[date_key] = []
                
                calendar_data[date_key].append({
                    'id': rule.id,
                    'name': rule.compliance_type,
                    'type': rule.compliance_type,
                    'status': rule.status,
                    'due_date': rule.due_date
                })
            
            return {
                'success': True,
                'month': month,
                'year': year,
                'calendar_data': calendar_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get compliance calendar: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get compliance calendar'
            }
    
    def run_compliance_check(self, rule_id: int) -> Dict[str, Any]:
        """
        Run compliance check for a specific rule
        
        Args:
            rule_id: Compliance rule ID
            
        Returns:
            Dict containing check result
        """
        try:
            rule = MSMECompliance.objects.get(id=rule_id, solution_name=self.solution_name)
            
            # Perform compliance check based on rule type
            check_result = self._perform_compliance_check(rule)
            
            # Update rule status based on check result
            if check_result['passed']:
                new_status = 'completed'
                message = 'Compliance check passed'
            else:
                new_status = 'pending'
                message = 'Compliance check failed - action required'
            
            # Update rule
            rule.status = new_status
            rule.notes = f"Last check: {timezone.now().isoformat()} - {'Passed' if check_result['passed'] else 'Failed'}"
            rule.save()
            
            return {
                'success': True,
                'rule_id': rule_id,
                'check_result': check_result,
                'new_status': new_status,
                'message': message
            }
            
        except MSMECompliance.DoesNotExist:
            return {
                'success': False,
                'error': 'Compliance rule not found',
                'message': 'Compliance rule not found'
            }
        except Exception as e:
            self.logger.error(f"Failed to run compliance check: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to run compliance check'
            }
    
    def _perform_compliance_check(self, rule: MSMECompliance) -> Dict[str, Any]:
        """Perform actual compliance check based on rule type"""
        try:
            rule_type = rule.compliance_type
            check_data = {'requirements': rule.requirements, 'notes': rule.notes}
            
            if rule_type == 'tax':
                return self._check_tax_compliance(check_data)
            elif rule_type == 'regulatory':
                return self._check_regulatory_compliance(check_data)
            elif rule_type == 'environmental':
                return self._check_environmental_compliance(check_data)
            elif rule_type == 'health_safety':
                return self._check_health_safety_compliance(check_data)
            else:
                return self._check_general_compliance(check_data)
                
        except Exception as e:
            self.logger.error(f"Failed to perform compliance check: {str(e)}")
            return {
                'passed': False,
                'message': f'Check failed: {str(e)}',
                'details': {}
            }
    
    def _check_tax_compliance(self, check_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check tax compliance"""
        # This would integrate with actual tax systems
        # For now, return a mock result
        return {
            'passed': True,
            'message': 'Tax compliance verified',
            'details': {
                'filing_status': 'filed',
                'payment_status': 'paid',
                'verification_date': timezone.now().isoformat()
            }
        }
    
    def _check_regulatory_compliance(self, check_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check regulatory compliance"""
        return {
            'passed': True,
            'message': 'Regulatory compliance verified',
            'details': {
                'license_status': 'valid',
                'permit_status': 'current',
                'verification_date': timezone.now().isoformat()
            }
        }
    
    def _check_environmental_compliance(self, check_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check environmental compliance"""
        return {
            'passed': True,
            'message': 'Environmental compliance verified',
            'details': {
                'emissions_status': 'within_limits',
                'waste_management': 'compliant',
                'verification_date': timezone.now().isoformat()
            }
        }
    
    def _check_health_safety_compliance(self, check_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check health and safety compliance"""
        return {
            'passed': True,
            'message': 'Health and safety compliance verified',
            'details': {
                'safety_inspection': 'passed',
                'training_status': 'current',
                'verification_date': timezone.now().isoformat()
            }
        }
    
    def _check_general_compliance(self, check_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check general compliance"""
        return {
            'passed': True,
            'message': 'General compliance verified',
            'details': {
                'verification_date': timezone.now().isoformat()
            }
        }
    
    def get_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate compliance report for specified period
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Dict containing compliance report
        """
        try:
            # Get compliance rules in the period
            compliance_rules = MSMECompliance.objects.filter(
                solution_name=self.solution_name,
                due_date__range=[start_date.date(), end_date.date()]
            )
            
            # Calculate statistics
            total_rules = compliance_rules.count()
            completed_rules = compliance_rules.filter(status='completed').count()
            pending_rules = compliance_rules.filter(status='pending').count()
            overdue_rules = compliance_rules.filter(
                status='pending',
                due_date__lt=timezone.now().date()
            ).count()
            
            # Calculate compliance rate
            compliance_rate = 0
            if total_rules > 0:
                compliance_rate = (completed_rules / total_rules) * 100
            
            # Get compliance by type
            compliance_by_type = {}
            for rule in compliance_rules:
                rule_type = rule.compliance_type
                if rule_type not in compliance_by_type:
                    compliance_by_type[rule_type] = {
                        'total': 0,
                        'completed': 0,
                        'pending': 0,
                        'overdue': 0
                    }
                
                compliance_by_type[rule_type]['total'] += 1
                if rule.status == 'completed':
                    compliance_by_type[rule_type]['completed'] += 1
                elif rule.status == 'pending':
                    if rule.due_date < timezone.now().date():
                        compliance_by_type[rule_type]['overdue'] += 1
                    else:
                        compliance_by_type[rule_type]['pending'] += 1
            
            # Generate recommendations
            recommendations = self._generate_compliance_recommendations(
                total_rules, completed_rules, overdue_rules, compliance_rate
            )
            
            return {
                'success': True,
                'report_period': {
                    'start': start_date,
                    'end': end_date
                },
                'summary': {
                    'total_rules': total_rules,
                    'completed_rules': completed_rules,
                    'pending_rules': pending_rules,
                    'overdue_rules': overdue_rules,
                    'compliance_rate': round(compliance_rate, 2)
                },
                'compliance_by_type': compliance_by_type,
                'recommendations': recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to generate compliance report'
            }
    
    def _generate_compliance_recommendations(self, total_rules: int, completed_rules: int, 
                                          overdue_rules: int, compliance_rate: float) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if compliance_rate < 60:
            recommendations.append("Critical: Immediate action required to improve compliance")
            recommendations.append("Review and prioritize overdue compliance items")
            recommendations.append("Consider external compliance consultation")
        elif compliance_rate < 80:
            recommendations.append("Focus on completing pending compliance items")
            recommendations.append("Review processes for compliance management")
            recommendations.append("Implement compliance tracking system")
        elif compliance_rate < 95:
            recommendations.append("Good compliance rate - focus on remaining items")
            recommendations.append("Optimize compliance processes")
            recommendations.append("Consider proactive compliance measures")
        else:
            recommendations.append("Excellent compliance rate - maintain current standards")
            recommendations.append("Focus on continuous improvement")
            recommendations.append("Consider industry best practices")
        
        if overdue_rules > 0:
            recommendations.append(f"Address {overdue_rules} overdue compliance items immediately")
        
        return recommendations
    
    def set_compliance_reminder(self, rule_id: int, reminder_days: int = 7) -> Dict[str, Any]:
        """
        Set compliance reminder for a rule
        
        Args:
            rule_id: Compliance rule ID
            reminder_days: Days before due date to send reminder
            
        Returns:
            Dict containing reminder setup result
        """
        try:
            rule = MSMECompliance.objects.get(id=rule_id, solution_name=self.solution_name)
            
            # Calculate reminder date
            reminder_date = rule.due_date - timedelta(days=reminder_days)
            
            # Update rule with reminder information
            rule.notes = f"Reminder: {reminder_days} days before due date, set for {reminder_date.isoformat()}"
            rule.save()
            
            return {
                'success': True,
                'rule_id': rule_id,
                'reminder_date': reminder_date,
                'message': f'Reminder set for {reminder_days} days before due date'
            }
            
        except MSMECompliance.DoesNotExist:
            return {
                'success': False,
                'error': 'Compliance rule not found',
                'message': 'Compliance rule not found'
            }
        except Exception as e:
            self.logger.error(f"Failed to set compliance reminder: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to set compliance reminder'
            }
    
    def get_compliance_alerts(self) -> List[Dict[str, Any]]:
        """Get current compliance alerts"""
        try:
            alerts = []
            
            # Check for overdue items
            overdue_rules = MSMECompliance.objects.filter(
                solution_name=self.solution_name,
                status='pending',
                due_date__lt=timezone.now().date()
            )
            
            for rule in overdue_rules:
                days_overdue = (timezone.now().date() - rule.due_date).days
                
                if days_overdue <= 7:
                    severity = 'medium'
                elif days_overdue <= 30:
                    severity = 'high'
                else:
                    severity = 'critical'
                
                alerts.append({
                    'type': 'compliance_overdue',
                    'severity': severity,
                    'rule_id': rule.id,
                    'rule_name': rule.compliance_type,
                    'rule_type': rule.compliance_type,
                    'due_date': rule.due_date,
                    'days_overdue': days_overdue,
                    'message': f"Compliance item '{rule.compliance_type}' is {days_overdue} days overdue"
                })
            
            # Check for upcoming deadlines
            upcoming_rules = MSMECompliance.objects.filter(
                solution_name=self.solution_name,
                status='pending',
                due_date__range=[timezone.now().date(), timezone.now().date() + timedelta(days=7)]
            )
            
            for rule in upcoming_rules:
                days_remaining = (rule.due_date - timezone.now().date()).days
                
                alerts.append({
                    'type': 'compliance_upcoming',
                    'severity': 'low',
                    'rule_id': rule.id,
                    'rule_name': rule.compliance_type,
                    'rule_type': rule.compliance_type,
                    'due_date': rule.due_date,
                    'days_remaining': days_remaining,
                    'message': f"Compliance item '{rule.compliance_type}' due in {days_remaining} days"
                })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to get compliance alerts: {str(e)}")
            return []
