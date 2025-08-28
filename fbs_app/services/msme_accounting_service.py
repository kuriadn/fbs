"""
MSME Accounting Service

Comprehensive service for MSME accounting management including:
- Cash flow management
- Income and expense tracking
- Basic ledger operations
- Tax calculations
- Financial reporting
"""

import logging
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal
import json
from django.db.models import Sum

from ..models.accounting import (
    CashEntry, IncomeExpense, BasicLedger, TaxCalculation,
    ChartOfAccounts, FinancialPeriod
)
from ..models.msme import MSMEAnalytics

logger = logging.getLogger(__name__)


class MSMEAccountingService:
    """Service for MSME accounting operations"""
    
    def __init__(self, user: User):
        self.user = user
        self.logger = logging.getLogger(f"{__name__}.{user.username}")
    
    def create_cash_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new cash entry
        
        Args:
            entry_data: Cash entry information
            
        Returns:
            Dict containing creation result
        """
        try:
            with transaction.atomic():
                entry = CashEntry.objects.create(
                    user=self.user,
                    entry_type=entry_data.get('entry_type'),
                    amount=entry_data.get('amount'),
                    currency=entry_data.get('currency', 'USD'),
                    description=entry_data.get('description'),
                    reference_number=entry_data.get('reference_number'),
                    entry_date=entry_data.get('entry_date', timezone.now().date()),
                    entry_data=entry_data.get('additional_data', {})
                )
                
                # Update analytics
                self._update_cash_analytics(entry)
                
                self.logger.info(f"Cash entry created: {entry.entry_type} - {entry.amount}")
                
                return {
                    'success': True,
                    'entry_id': entry.id,
                    'message': 'Cash entry created successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create cash entry: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create cash entry'
            }
    
    def create_income_expense(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new income or expense transaction
        
        Args:
            transaction_data: Transaction information
            
        Returns:
            Dict containing creation result
        """
        try:
            with transaction.atomic():
                transaction = IncomeExpense.objects.create(
                    user=self.user,
                    transaction_type=transaction_data.get('transaction_type'),
                    category=transaction_data.get('category'),
                    subcategory=transaction_data.get('subcategory'),
                    amount=transaction_data.get('amount'),
                    currency=transaction_data.get('currency', 'USD'),
                    description=transaction_data.get('description'),
                    transaction_date=transaction_data.get('transaction_date', timezone.now().date()),
                    due_date=transaction_data.get('due_date'),
                    status=transaction_data.get('status', 'pending'),
                    payment_method=transaction_data.get('payment_method'),
                    transaction_data=transaction_data.get('additional_data', {})
                )
                
                # Update analytics
                self._update_income_expense_analytics(transaction)
                
                self.logger.info(f"Transaction created: {transaction.transaction_type} - {transaction.amount}")
                
                return {
                    'success': True,
                    'transaction_id': transaction.id,
                    'message': 'Transaction created successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create transaction: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create transaction'
            }
    
    def create_ledger_entry(self, ledger_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new ledger entry
        
        Args:
            ledger_data: Ledger entry information
            
        Returns:
            Dict containing creation result
        """
        try:
            with transaction.atomic():
                # Calculate balance
                debit_amount = ledger_data.get('debit_amount', Decimal('0'))
                credit_amount = ledger_data.get('credit_amount', Decimal('0'))
                balance = debit_amount - credit_amount
                
                entry = BasicLedger.objects.create(
                    user=self.user,
                    account=ledger_data.get('account'),
                    account_type=ledger_data.get('account_type'),
                    description=ledger_data.get('description'),
                    debit_amount=debit_amount,
                    credit_amount=credit_amount,
                    balance=balance,
                    currency=ledger_data.get('currency', 'USD'),
                    entry_date=ledger_data.get('entry_date', timezone.now().date()),
                    reference=ledger_data.get('reference'),
                    ledger_data=ledger_data.get('additional_data', {})
                )
                
                self.logger.info(f"Ledger entry created: {entry.account} - {entry.balance}")
                
                return {
                    'success': True,
                    'entry_id': entry.id,
                    'message': 'Ledger entry created successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create ledger entry: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create ledger entry'
            }
    
    def get_cash_flow_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Get cash flow summary for specified period
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dict containing cash flow summary
        """
        try:
            # Get cash entries in the period
            cash_entries = CashEntry.objects.filter(
                user=self.user,
                entry_date__range=[start_date.date(), end_date.date()]
            )
            
            # Calculate totals by type
            receipts = cash_entries.filter(entry_type='receipt').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            payments = cash_entries.filter(entry_type='payment').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            transfers = cash_entries.filter(entry_type='transfer').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            adjustments = cash_entries.filter(entry_type='adjustment').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            net_cash_flow = receipts - payments + transfers + adjustments
            
            # Get daily cash flow
            daily_cash_flow = []
            current_date = start_date.date()
            while current_date <= end_date.date():
                day_entries = cash_entries.filter(entry_date=current_date)
                day_receipts = day_entries.filter(entry_type='receipt').aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0')
                day_payments = day_entries.filter(entry_type='payment').aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0')
                
                daily_cash_flow.append({
                    'date': current_date,
                    'receipts': float(day_receipts),
                    'payments': float(day_payments),
                    'net_flow': float(day_receipts - day_payments)
                })
                
                current_date += timedelta(days=1)
            
            return {
                'success': True,
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'summary': {
                    'total_receipts': float(receipts),
                    'total_payments': float(payments),
                    'total_transfers': float(transfers),
                    'total_adjustments': float(adjustments),
                    'net_cash_flow': float(net_cash_flow)
                },
                'daily_cash_flow': daily_cash_flow
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cash flow summary: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get cash flow summary'
            }
    
    def get_income_expense_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Get income and expense summary for specified period
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dict containing income/expense summary
        """
        try:
            # Get transactions in the period
            transactions = IncomeExpense.objects.filter(
                user=self.user,
                transaction_date__range=[start_date.date(), end_date.date()]
            )
            
            # Calculate totals by type
            income = transactions.filter(transaction_type='income').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            expenses = transactions.filter(transaction_type='expense').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            net_profit = income - expenses
            
            # Get income by category
            income_by_category = {}
            income_transactions = transactions.filter(transaction_type='income')
            for transaction in income_transactions:
                category = transaction.category
                if category not in income_by_category:
                    income_by_category[category] = Decimal('0')
                income_by_category[category] += transaction.amount
            
            # Get expenses by category
            expenses_by_category = {}
            expense_transactions = transactions.filter(transaction_type='expense')
            for transaction in expense_transactions:
                category = transaction.category
                if category not in expenses_by_category:
                    expenses_by_category[category] = Decimal('0')
                expenses_by_category[category] += transaction.amount
            
            # Calculate profit margin
            profit_margin = 0
            if income > 0:
                profit_margin = (net_profit / income) * 100
            
            return {
                'success': True,
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'summary': {
                    'total_income': float(income),
                    'total_expenses': float(expenses),
                    'net_profit': float(net_profit),
                    'profit_margin': round(profit_margin, 2)
                },
                'income_by_category': {k: float(v) for k, v in income_by_category.items()},
                'expenses_by_category': {k: float(v) for k, v in expenses_by_category.items()}
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get income/expense summary: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get income/expense summary'
            }
    
    def get_ledger_summary(self, account: str = None, start_date: datetime = None, 
                          end_date: datetime = None) -> Dict[str, Any]:
        """
        Get ledger summary for specified account and period
        
        Args:
            account: Account name (optional)
            start_date: Start date for analysis (optional)
            end_date: End date for analysis (optional)
            
        Returns:
            Dict containing ledger summary
        """
        try:
            # Build query
            query = {'user': self.user}
            if account:
                query['account'] = account
            if start_date:
                query['entry_date__gte'] = start_date.date()
            if end_date:
                query['entry_date__lte'] = end_date.date()
            
            ledger_entries = BasicLedger.objects.filter(**query).order_by('entry_date')
            
            if not ledger_entries.exists():
                return {
                    'success': True,
                    'account': account,
                    'period': {
                        'start': start_date,
                        'end': end_date
                    },
                    'summary': {
                        'total_debits': 0,
                        'total_credits': 0,
                        'net_balance': 0,
                        'entry_count': 0
                    },
                    'entries': []
                }
            
            # Calculate totals
            total_debits = ledger_entries.aggregate(total=Sum('debit_amount'))['total'] or Decimal('0')
            total_credits = ledger_entries.aggregate(total=Sum('credit_amount'))['total'] or Decimal('0')
            net_balance = total_debits - total_credits
            entry_count = ledger_entries.count()
            
            # Get entries
            entries = []
            for entry in ledger_entries:
                entries.append({
                    'id': entry.id,
                    'account': entry.account,
                    'account_type': entry.account_type,
                    'description': entry.description,
                    'debit_amount': float(entry.debit_amount),
                    'credit_amount': float(entry.credit_amount),
                    'balance': float(entry.balance),
                    'entry_date': entry.entry_date,
                    'reference': entry.reference
                })
            
            return {
                'success': True,
                'account': account,
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'summary': {
                    'total_debits': float(total_debits),
                    'total_credits': float(total_credits),
                    'net_balance': float(net_balance),
                    'entry_count': entry_count
                },
                'entries': entries
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get ledger summary: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get ledger summary'
            }
    
    def create_tax_calculation(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new tax calculation
        
        Args:
            tax_data: Tax calculation information
            
        Returns:
            Dict containing creation result
        """
        try:
            with transaction.atomic():
                # Calculate tax amounts
                gross_amount = Decimal(str(tax_data.get('gross_amount', 0)))
                tax_rate = Decimal(str(tax_data.get('tax_rate', 0)))
                
                tax_amount = gross_amount * (tax_rate / 100)
                net_tax_amount = tax_amount  # Can be adjusted for deductions
                
                tax_calc = TaxCalculation.objects.create(
                    user=self.user,
                    tax_type=tax_data.get('tax_type'),
                    tax_period=tax_data.get('tax_period'),
                    period_start=tax_data.get('period_start'),
                    period_end=tax_data.get('period_end'),
                    gross_amount=gross_amount,
                    tax_rate=tax_rate,
                    tax_amount=tax_amount,
                    net_tax_amount=net_tax_amount,
                    currency=tax_data.get('currency', 'USD'),
                    calculation_date=tax_data.get('calculation_date', timezone.now().date()),
                    due_date=tax_data.get('due_date'),
                    calculation_data=tax_data.get('additional_data', {})
                )
                
                self.logger.info(f"Tax calculation created: {tax_calc.tax_type} - {tax_calc.tax_amount}")
                
                return {
                    'success': True,
                    'tax_id': tax_calc.id,
                    'message': 'Tax calculation created successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create tax calculation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create tax calculation'
            }
    
    def get_financial_periods(self) -> Dict[str, Any]:
        """Get all financial periods"""
        try:
            periods = FinancialPeriod.objects.filter(
                user=self.user
            ).order_by('-start_date')
            
            period_list = []
            for period in periods:
                period_list.append({
                    'id': period.id,
                    'name': period.period_name,
                    'type': period.period_type,
                    'start_date': period.start_date,
                    'end_date': period.end_date,
                    'is_closed': period.is_closed,
                    'closing_date': period.closing_date
                })
            
            return {
                'success': True,
                'periods': period_list,
                'total_periods': len(period_list)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get financial periods: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get financial periods'
            }
    
    def close_financial_period(self, period_id: int, closing_notes: str = None) -> Dict[str, Any]:
        """
        Close a financial period
        
        Args:
            period_id: Financial period ID
            closing_notes: Notes about the closing
            
        Returns:
            Dict containing closing result
        """
        try:
            with transaction.atomic():
                period = FinancialPeriod.objects.get(id=period_id, user=self.user)
                
                if period.is_closed:
                    return {
                        'success': False,
                        'error': 'Period already closed',
                        'message': 'Financial period is already closed'
                    }
                
                # Close the period
                period.is_closed = True
                period.closing_date = timezone.now()
                period.closing_notes = closing_notes
                period.save()
                
                self.logger.info(f"Financial period closed: {period.period_name}")
                
                return {
                    'success': True,
                    'period_id': period_id,
                    'message': 'Financial period closed successfully'
                }
                
        except FinancialPeriod.DoesNotExist:
            return {
                'success': False,
                'error': 'Financial period not found',
                'message': 'Financial period not found'
            }
        except Exception as e:
            self.logger.error(f"Failed to close financial period: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to close financial period'
            }
    
    def _update_cash_analytics(self, entry: CashEntry):
        """Update cash flow analytics"""
        try:
            # Update MSME analytics for cash flow
            analytics, created = MSMEAnalytics.objects.get_or_create(
                user=self.user,
                metric_name='Cash Flow',
                metric_date=entry.entry_date,
                defaults={
                    'metric_value': 0,
                    'metric_type': 'cash_flow'
                }
            )
            
            # Update metric value based on entry type
            if entry.entry_type == 'receipt':
                analytics.metric_value += entry.amount
            elif entry.entry_type == 'payment':
                analytics.metric_value -= entry.amount
            
            analytics.save()
            
        except Exception as e:
            self.logger.warning(f"Failed to update cash analytics: {str(e)}")
    
    def _update_income_expense_analytics(self, transaction: IncomeExpense):
        """Update income/expense analytics"""
        try:
            # Update MSME analytics for income/expense
            metric_name = f"{transaction.transaction_type.title()} - {transaction.category}"
            analytics, created = MSMEAnalytics.objects.get_or_create(
                user=self.user,
                metric_name=metric_name,
                metric_date=transaction.transaction_date,
                defaults={
                    'metric_value': 0,
                    'metric_type': transaction.transaction_type
                }
            )
            
            analytics.metric_value += transaction.amount
            analytics.save()
            
        except Exception as e:
            self.logger.warning(f"Failed to update income/expense analytics: {str(e)}")
    
    def get_account_balance(self, account: str) -> Dict[str, Any]:
        """
        Get current balance for a specific account
        
        Args:
            account: Account name
            
        Returns:
            Dict containing account balance
        """
        try:
            # Get latest ledger entry for the account
            latest_entry = BasicLedger.objects.filter(
                user=self.user,
                account=account
            ).order_by('-entry_date').first()
            
            if not latest_entry:
                return {
                    'success': True,
                    'account': account,
                    'balance': 0,
                    'last_updated': None,
                    'message': 'No entries found for account'
                }
            
            return {
                'success': True,
                'account': account,
                'balance': float(latest_entry.balance),
                'last_updated': latest_entry.entry_date,
                'currency': latest_entry.currency
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get account balance: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get account balance'
            }
    
    def reconcile_account(self, account: str, reconciliation_date: datetime.date) -> Dict[str, Any]:
        """
        Reconcile an account as of a specific date
        
        Args:
            account: Account name
            reconciliation_date: Date for reconciliation
            
        Returns:
            Dict containing reconciliation result
        """
        try:
            with transaction.atomic():
                # Get all ledger entries up to reconciliation date
                entries = BasicLedger.objects.filter(
                    user=self.user,
                    account=account,
                    entry_date__lte=reconciliation_date
                ).order_by('entry_date')
                
                if not entries.exists():
                    return {
                        'success': False,
                        'error': 'No entries found',
                        'message': f'No ledger entries found for account {account}'
                    }
                
                # Calculate running balance
                running_balance = Decimal('0')
                for entry in entries:
                    running_balance += entry.debit_amount - entry.credit_amount
                
                # Update the latest entry as reconciled
                latest_entry = entries.last()
                latest_entry.is_reconciled = True
                latest_entry.reconciliation_date = reconciliation_date
                latest_entry.save()
                
                return {
                    'success': True,
                    'account': account,
                    'reconciliation_date': reconciliation_date,
                    'reconciled_balance': float(running_balance),
                    'entries_reconciled': entries.count(),
                    'message': 'Account reconciled successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to reconcile account: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to reconcile account'
            }
