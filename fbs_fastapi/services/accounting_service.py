"""
FBS FastAPI Accounting Service

PRESERVED from Django simple_accounting_service.py
Service for simple MSME accounting and financial management.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, date

from .service_interfaces import BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class SimpleAccountingService(BaseService, AsyncServiceMixin):
    """Service for simple MSME accounting - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)

    async def create_cash_basis_entry(self, entry_type: str, amount: float, description: str = '',
                                    category: str = '', date: str = None) -> Dict[str, Any]:
        """Create cash basis accounting entry - PRESERVED from Django"""
        try:
            from ..models.models import CashEntry
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                entry_id = str(uuid.uuid4())

                if not date:
                    entry_date = datetime.now().date()
                else:
                    entry_date = datetime.fromisoformat(date).date()

                # Create cash entry
                entry = CashEntry(
                    business_id=self.solution_name,  # Use solution name as business ID
                    entry_date=entry_date,
                    entry_type=entry_type,  # 'income' or 'expense'
                    amount=amount,
                    description=description,
                    category=category,
                    subcategory='',
                    payment_method='cash',
                    reference_number=''
                )

                db.add(entry)
                await db.commit()
                await db.refresh(entry)

                return {
                    'success': True,
                    'entry_id': str(entry.id),
                    'entry_type': entry_type,
                    'amount': amount,
                    'description': description,
                    'category': category,
                    'date': entry_date.isoformat(),
                    'message': f'Cash basis entry created for {entry_type}'
                }

        except Exception as e:
            logger.error(f"Error creating cash basis entry: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_basic_ledger(self, start_date: str = None, end_date: str = None,
                            account_type: str = None) -> Dict[str, Any]:
        """Get simple general ledger - PRESERVED from Django"""
        try:
            from ..models.models import CashEntry
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                # Build query
                query = db.query(CashEntry)
                if start_date:
                    query = query.filter(CashEntry.entry_date >= datetime.fromisoformat(start_date).date())
                if end_date:
                    query = query.filter(CashEntry.entry_date <= datetime.fromisoformat(end_date).date())
                if account_type:
                    query = query.filter(CashEntry.entry_type == account_type)

                # Get entries
                entries = await query.order_by(CashEntry.entry_date).all()

                # Calculate running balance
                balance = 0
                ledger_entries = []

                for entry in entries:
                    if entry.entry_type == 'income':
                        balance += entry.amount
                    else:
                        balance -= entry.amount

                    ledger_entries.append({
                        'entry_id': str(entry.id),
                        'date': entry.entry_date.isoformat(),
                        'entry_type': entry.entry_type,
                        'amount': entry.amount,
                        'description': entry.description,
                        'category': entry.category,
                        'balance': balance
                    })

                return {
                    'success': True,
                    'entries': ledger_entries,
                    'total_entries': len(ledger_entries),
                    'current_balance': balance,
                    'period': {
                        'start_date': start_date,
                        'end_date': end_date
                    }
                }

        except Exception as e:
            logger.error(f"Error getting basic ledger: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def create_income_expense_record(self, record_type: str, amount: float, description: str = '',
                                         category: str = '', date: str = None) -> Dict[str, Any]:
        """Create income/expense record - PRESERVED from Django"""
        try:
            from ..models.models import IncomeExpense
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                if not date:
                    entry_date = datetime.now().date()
                else:
                    entry_date = datetime.fromisoformat(date).date()

                # Create income/expense record
                record = IncomeExpense(
                    business_id=self.solution_name,  # Use solution name as business ID
                    transaction_date=entry_date,
                    transaction_type=record_type,  # 'income' or 'expense'
                    amount=amount,
                    description=description,
                    category=category,
                    payment_method='cash'
                )

                db.add(record)
                await db.commit()
                await db.refresh(record)

                return {
                    'success': True,
                    'record_id': str(record.id),
                    'record_type': record_type,
                    'amount': amount,
                    'description': description,
                    'category': category,
                    'date': entry_date.isoformat(),
                    'message': f'Income/expense record created for {record_type}'
                }

        except Exception as e:
            logger.error(f"Error creating income/expense record: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_income_expense_summary(self, period: str = 'month') -> Dict[str, Any]:
        """Get income and expense summary - PRESERVED from Django"""
        try:
            from ..models.models import IncomeExpense
            from ..core.dependencies import get_db_session_for_request
            from sqlalchemy import func, extract
            async for db in get_db_session_for_request(None):

                # Calculate date range
                now = datetime.now()
                if period == 'month':
                    start_date = now.replace(day=1)
                    end_date = now
                elif period == 'quarter':
                    quarter = (now.month - 1) // 3 + 1
                    start_date = datetime(now.year, (quarter - 1) * 3 + 1, 1)
                    end_date = now
                elif period == 'year':
                    start_date = now.replace(month=1, day=1)
                    end_date = now
                else:
                    # Default to current month
                    start_date = now.replace(day=1)
                    end_date = now

                # Get summary
                result = await db.query(
                    func.sum(IncomeExpense.amount).label('total'),
                    IncomeExpense.transaction_type
                ).filter(
                    IncomeExpense.transaction_date >= start_date.date(),
                    IncomeExpense.transaction_date <= end_date.date()
                ).group_by(IncomeExpense.transaction_type).all()

                summary = {'income': 0, 'expense': 0}
                for total, transaction_type in result:
                    summary[transaction_type] = total or 0

                net_income = summary['income'] - summary['expense']

                return {
                    'success': True,
                    'period': period,
                    'date_range': {
                        'start': start_date.date().isoformat(),
                        'end': end_date.date().isoformat()
                    },
                    'summary': summary,
                    'net_income': net_income,
                    'message': f'Income/expense summary for {period}'
                }

        except Exception as e:
            logger.error(f"Error getting income/expense summary: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_financial_health_indicators(self) -> Dict[str, Any]:
        """Get basic financial health indicators - PRESERVED from Django"""
        try:
            # Get income/expense summary
            income_expense = await self.get_income_expense_summary('month')

            if not income_expense['success']:
                return income_expense

            summary = income_expense['summary']

            # Calculate basic health indicators
            total_income = summary.get('income', 0)
            total_expenses = summary.get('expense', 0)

            if total_income > 0:
                expense_ratio = (total_expenses / total_income) * 100
                savings_rate = ((total_income - total_expenses) / total_income) * 100
            else:
                expense_ratio = 0
                savings_rate = 0

            # Determine health status
            if expense_ratio < 50:
                health_status = 'excellent'
            elif expense_ratio < 70:
                health_status = 'good'
            elif expense_ratio < 90:
                health_status = 'fair'
            else:
                health_status = 'poor'

            return {
                'success': True,
                'indicators': {
                    'expense_ratio': round(expense_ratio, 2),
                    'savings_rate': round(savings_rate, 2),
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'net_income': total_income - total_expenses
                },
                'health_status': health_status,
                'recommendations': self._get_health_recommendations(health_status),
                'message': 'Financial health indicators calculated'
            }

        except Exception as e:
            logger.error(f"Error getting financial health indicators: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    def _get_health_recommendations(self, health_status: str) -> List[str]:
        """Get health recommendations based on status - PRESERVED from Django"""
        recommendations = {
            'excellent': [
                'Keep up the great financial management!',
                'Consider investing surplus funds wisely.'
            ],
            'good': [
                'Your finances are in good shape.',
                'Look for opportunities to reduce expenses.'
            ],
            'fair': [
                'Consider reviewing your expense categories.',
                'Look for ways to increase income or reduce costs.'
            ],
            'poor': [
                'Immediate attention needed to expense management.',
                'Consider consulting a financial advisor.',
                'Review all subscriptions and recurring expenses.'
            ]
        }
        return recommendations.get(health_status, [])

    async def calculate_tax(self, amount: float, tax_type: str = 'vat', tax_rate: Optional[float] = None) -> Dict[str, Any]:
        """Calculate tax amounts - PRESERVED from Django"""
        try:
            # Default tax rates (can be made configurable)
            default_rates = {
                'vat': 0.16,  # 16% VAT
                'income_tax': 0.30,  # 30% income tax
                'payroll_tax': 0.05,  # 5% payroll tax
                'withholding_tax': 0.10  # 10% withholding tax
            }

            rate = tax_rate if tax_rate is not None else default_rates.get(tax_type, 0.0)
            tax_amount = amount * rate

            return {
                'success': True,
                'amount': amount,
                'tax_type': tax_type,
                'tax_rate': rate,
                'tax_amount': round(tax_amount, 2),
                'net_amount': round(amount - tax_amount, 2),
                'calculation_date': datetime.now().isoformat(),
                'message': f'Tax calculated for {tax_type}'
            }

        except Exception as e:
            logger.error(f"Error calculating tax: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_cash_position(self, date: str = None) -> Dict[str, Any]:
        """Get current cash position - PRESERVED from Django"""
        try:
            from ..models.models import CashEntry
            from ..core.dependencies import get_db_session_for_request
            from sqlalchemy import func
            async for db in get_db_session_for_request(None):

                # Use provided date or current date
                if date:
                    target_date = datetime.fromisoformat(date).date()
                else:
                    target_date = datetime.now().date()

                # Calculate cash position up to target date
                income_result = await db.query(func.sum(CashEntry.amount)).filter(
                    CashEntry.entry_date <= target_date,
                    CashEntry.entry_type == 'income'
                ).first()

                expense_result = await db.query(func.sum(CashEntry.amount)).filter(
                    CashEntry.entry_date <= target_date,
                    CashEntry.entry_type == 'expense'
                ).first()

                total_income = income_result[0] or 0
                total_expenses = expense_result[0] or 0
                cash_position = total_income - total_expenses

                return {
                    'success': True,
                    'date': target_date.isoformat(),
                    'cash_position': cash_position,
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'message': f'Cash position as of {target_date.isoformat()}'
                }

        except Exception as e:
            logger.error(f"Error getting cash position: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'accounting',
            'status': 'healthy',
            'message': 'Simple accounting service operational'
        }
