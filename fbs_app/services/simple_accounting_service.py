"""
FBS App Simple Accounting Service

Service for simple MSME accounting and financial management.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.db import connections
from django.conf import settings

logger = logging.getLogger('fbs_app')


class SimpleAccountingService:
    """Service for simple MSME accounting"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        self.fbs_config = getattr(settings, 'FBS_APP', {})
    
    def create_cash_basis_entry(self, entry_type: str, amount: float, description: str = '', 
                               category: str = '', date: str = None) -> Dict[str, Any]:
        """Create cash basis accounting entry"""
        try:
            from ..models import CashEntry
            
            entry_id = str(uuid.uuid4())
            
            if not date:
                date = timezone.now().date().isoformat()
            
            # Create cash entry
            entry = CashEntry.objects.create(
                business_id=self.solution_name,
                entry_date=timezone.now().date(),
                entry_type=entry_type,  # 'income' or 'expense'
                amount=amount,
                description=description,
                category=category,
                subcategory='',
                payment_method='cash',
                reference_number=''
            )
            
            return {
                'success': True,
                'entry_id': entry.id,
                'entry_type': entry_type,
                'amount': amount,
                'description': description,
                'category': category,
                'date': date,
                'message': f'Cash basis entry created for {entry_type}'
            }
            
        except Exception as e:
            logger.error(f"Error creating cash basis entry: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_basic_ledger(self, start_date: str = None, end_date: str = None, 
                        account_type: str = None) -> Dict[str, Any]:
        """Get simple general ledger"""
        try:
            from ..models import CashEntry
            
            # Build query
            query = {'solution_name': self.solution_name}
            if start_date:
                query['date__gte'] = start_date
            if end_date:
                query['date__lte'] = end_date
            if account_type:
                query['entry_type'] = account_type
            
            # Get entries
            entries = CashEntry.objects.filter(**query).order_by('date')
            
            # Calculate running balance
            balance = 0
            ledger_entries = []
            
            for entry in entries:
                if entry.entry_type == 'income':
                    balance += entry.amount
                else:
                    balance -= entry.amount
                
                ledger_entries.append({
                    'entry_id': entry.id,
                    'date': entry.date.isoformat(),
                    'entry_type': entry.entry_type,
                    'amount': entry.amount,
                    'description': entry.description,
                    'category': entry.category,
                    'balance': balance
                })
            
            return {
                'success': True,
                'ledger_entries': ledger_entries,
                'total_entries': len(ledger_entries),
                'final_balance': balance
            }
            
        except Exception as e:
            logger.error(f"Error getting basic ledger: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_income_expense_record(self, record_type: str, amount: float, 
                                   description: str = '', category: str = '', 
                                   date: str = None, reference: str = '') -> Dict[str, Any]:
        """Create income or expense record"""
        try:
            from ..models import IncomeExpense
            
            if not date:
                date = timezone.now().date().isoformat()
            
            # Create income/expense record
            record = IncomeExpense.objects.create(
                solution_name=self.solution_name,
                record_type=record_type,  # 'income' or 'expense'
                amount=amount,
                description=description,
                category=category,
                date=date,
                reference=reference,
                created_at=timezone.now()
            )
            
            return {
                'success': True,
                'record_id': record.id,
                'record_type': record_type,
                'amount': amount,
                'description': description,
                'category': category,
                'date': date,
                'reference': reference,
                'message': f'{record_type.title()} record created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating income/expense record: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_income_expense_summary(self, period: str = 'month') -> Dict[str, Any]:
        """Get income and expense summary for a period"""
        try:
            from ..models import IncomeExpense
            
            # Calculate date range
            end_date = timezone.now().date()
            if period == 'week':
                start_date = end_date - timezone.timedelta(days=7)
            elif period == 'month':
                start_date = end_date.replace(day=1)
            elif period == 'quarter':
                quarter = (end_date.month - 1) // 3
                start_date = end_date.replace(month=quarter * 3 + 1, day=1)
            elif period == 'year':
                start_date = end_date.replace(month=1, day=1)
            else:
                start_date = end_date - timezone.timedelta(days=30)
            
            # Get income and expenses
            income_records = IncomeExpense.objects.filter(
                solution_name=self.solution_name,
                record_type='income',
                date__gte=start_date,
                date__lte=end_date
            )
            
            expense_records = IncomeExpense.objects.filter(
                solution_name=self.solution_name,
                record_type='expense',
                date__gte=start_date,
                date__lte=end_date
            )
            
            # Calculate totals
            total_income = sum(record.amount for record in income_records)
            total_expenses = sum(record.amount for record in expense_records)
            net_income = total_income - total_expenses
            
            # Get category breakdown
            income_by_category = {}
            for record in income_records:
                category = record.category or 'Uncategorized'
                if category not in income_by_category:
                    income_by_category[category] = 0
                income_by_category[category] += record.amount
            
            expense_by_category = {}
            for record in expense_records:
                category = record.category or 'Uncategorized'
                if category not in expense_by_category:
                    expense_by_category[category] = 0
                expense_by_category[category] += record.amount
            
            return {
                'success': True,
                'period': period,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'summary': {
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'net_income': net_income,
                    'profit_margin': (net_income / total_income * 100) if total_income > 0 else 0
                },
                'income_by_category': income_by_category,
                'expense_by_category': expense_by_category,
                'record_counts': {
                    'income_records': income_records.count(),
                    'expense_records': expense_records.count()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting income/expense summary: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_basic_ledger_entry(self, account: str, debit: float = 0, credit: float = 0,
                                 description: str = '', date: str = None) -> Dict[str, Any]:
        """Create basic ledger entry"""
        try:
            from ..models import BasicLedger
            
            if not date:
                date = timezone.now().date().isoformat()
            
            # Validate entry
            if debit > 0 and credit > 0:
                return {'success': False, 'error': 'Cannot have both debit and credit'}
            
            if debit == 0 and credit == 0:
                return {'success': False, 'error': 'Must have either debit or credit'}
            
            # Create ledger entry
            entry = BasicLedger.objects.create(
                solution_name=self.solution_name,
                account=account,
                debit=debit,
                credit=credit,
                description=description,
                date=date,
                created_at=timezone.now()
            )
            
            return {
                'success': True,
                'entry_id': entry.id,
                'account': account,
                'debit': debit,
                'credit': credit,
                'description': description,
                'date': date,
                'message': 'Ledger entry created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating ledger entry: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_account_balance(self, account: str) -> Dict[str, Any]:
        """Get account balance"""
        try:
            from ..models import BasicLedger
            
            # Get all entries for the account
            entries = BasicLedger.objects.filter(
                solution_name=self.solution_name,
                account=account
            )
            
            # Calculate balance
            total_debits = sum(entry.debit for entry in entries)
            total_credits = sum(entry.credit for entry in entries)
            balance = total_debits - total_credits
            
            return {
                'success': True,
                'account': account,
                'total_debits': total_debits,
                'total_credits': total_credits,
                'balance': balance,
                'entry_count': entries.count()
            }
            
        except Exception as e:
            logger.error(f"Error getting account balance: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def calculate_tax_liability(self, period: str = 'monthly') -> Dict[str, Any]:
        """Calculate basic tax liability"""
        try:
            from ..models import TaxCalculation
            
            # Get income for the period
            income_summary = self.get_income_expense_summary(period)
            
            if not income_summary['success']:
                return income_summary
            
            net_income = income_summary['summary']['net_income']
            
            # Simple tax calculation (this would be more complex in production)
            tax_rates = {
                'monthly': 0.05,  # 5% monthly
                'quarterly': 0.15,  # 15% quarterly
                'yearly': 0.30   # 30% yearly
            }
            
            tax_rate = tax_rates.get(period, 0.05)
            tax_liability = net_income * tax_rate
            
            # Create tax calculation record
            tax_record = TaxCalculation.objects.create(
                solution_name=self.solution_name,
                period=period,
                net_income=net_income,
                tax_rate=tax_rate,
                tax_liability=tax_liability,
                calculated_at=timezone.now()
            )
            
            return {
                'success': True,
                'tax_record_id': tax_record.id,
                'period': period,
                'net_income': net_income,
                'tax_rate': tax_rate,
                'tax_liability': tax_liability,
                'message': f'Tax liability calculated for {period} period'
            }
            
        except Exception as e:
            logger.error(f"Error calculating tax liability: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_financial_health_indicators(self) -> Dict[str, Any]:
        """Get basic financial health indicators"""
        try:
            # Get current month summary
            current_summary = self.get_income_expense_summary('month')
            
            if not current_summary['success']:
                return current_summary
            
            # Get previous month for comparison
            previous_summary = self.get_income_expense_summary('month')
            
            # Calculate indicators
            current_net = current_summary['summary']['net_income']
            current_income = current_summary['summary']['total_income']
            current_expenses = current_summary['summary']['total_expenses']
            
            # Profit margin
            profit_margin = (current_net / current_income * 100) if current_income > 0 else 0
            
            # Expense ratio
            expense_ratio = (current_expenses / current_income * 100) if current_income > 0 else 0
            
            # Cash flow indicator
            cash_flow_indicator = 'positive' if current_net > 0 else 'negative'
            
            # Health score (simplified)
            health_score = min(100, max(0, profit_margin + (100 - expense_ratio)))
            
            return {
                'success': True,
                'indicators': {
                    'profit_margin': profit_margin,
                    'expense_ratio': expense_ratio,
                    'cash_flow_indicator': cash_flow_indicator,
                    'health_score': health_score
                },
                'current_period': {
                    'net_income': current_net,
                    'total_income': current_income,
                    'total_expenses': current_expenses
                },
                'assessment_date': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting financial health indicators: {str(e)}")
            return {'success': False, 'error': str(e)}
