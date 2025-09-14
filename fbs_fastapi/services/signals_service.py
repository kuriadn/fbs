"""
FBS FastAPI Signals Service

PRESERVED from Django signals.py
Event-driven signals system for observability and automation.
"""

import logging
from typing import Dict, Any, List, Callable, Optional, Awaitable
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools

from .service_interfaces import BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class SignalManager:
    """Manages event-driven signals for FBS FastAPI - PRESERVED from Django"""

    def __init__(self):
        self._signals: Dict[str, List[Callable]] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)

    def register_signal(self, signal_name: str, handler: Callable) -> None:
        """Register a signal handler - PRESERVED from Django pattern"""
        if signal_name not in self._signals:
            self._signals[signal_name] = []
        self._signals[signal_name].append(handler)
        logger.debug(f"Registered signal handler for {signal_name}")

    def unregister_signal(self, signal_name: str, handler: Callable) -> None:
        """Unregister a signal handler"""
        if signal_name in self._signals and handler in self._signals[signal_name]:
            self._signals[signal_name].remove(handler)
            logger.debug(f"Unregistered signal handler for {signal_name}")

    async def send_signal(self, signal_name: str, **kwargs) -> List[Any]:
        """Send a signal to all registered handlers - PRESERVED from Django pattern"""
        if signal_name not in self._signals:
            return []

        results = []
        for handler in self._signals[signal_name]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(**kwargs)
                else:
                    # Run sync handler in thread pool
                    result = await asyncio.get_event_loop().run_in_executor(
                        self._executor, handler, **kwargs
                    )
                results.append(result)
            except Exception as e:
                logger.warning(f"Signal handler {handler.__name__} failed for {signal_name}: {e}")

        return results

    def get_registered_signals(self) -> Dict[str, int]:
        """Get information about registered signals"""
        return {signal: len(handlers) for signal, handlers in self._signals.items()}

    def cleanup(self) -> None:
        """Cleanup signal manager resources"""
        self._executor.shutdown(wait=True)
        self._signals.clear()


class SignalsService(BaseService, AsyncServiceMixin):
    """Service for managing event-driven signals and automation - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)
        self.signal_manager = SignalManager()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Setup all signal handlers - PRESERVED from Django signals.py"""

        # Core model signals
        self.signal_manager.register_signal('odoo_database_post_save', self._odoo_database_post_save)
        self.signal_manager.register_signal('token_mapping_post_save', self._token_mapping_post_save)
        self.signal_manager.register_signal('request_log_post_save', self._request_log_post_save)
        self.signal_manager.register_signal('business_rule_post_save', self._business_rule_post_save)
        self.signal_manager.register_signal('cache_entry_post_save', self._cache_entry_post_save)
        self.signal_manager.register_signal('handshake_post_save', self._handshake_post_save)
        self.signal_manager.register_signal('notification_post_save', self._notification_post_save)

        # MSME model signals
        self.signal_manager.register_signal('msme_setup_wizard_post_save', self._msme_setup_wizard_post_save)
        self.signal_manager.register_signal('msme_kpi_post_save', self._msme_kpi_post_save)

        # Workflow signals
        self.signal_manager.register_signal('workflow_definition_post_save', self._workflow_definition_post_save)
        self.signal_manager.register_signal('workflow_instance_post_save', self._workflow_instance_post_save)

        # BI signals
        self.signal_manager.register_signal('dashboard_post_save', self._dashboard_post_save)
        self.signal_manager.register_signal('report_post_save', self._report_post_save)

        # Compliance signals
        self.signal_manager.register_signal('compliance_rule_post_save', self._compliance_rule_post_save)
        self.signal_manager.register_signal('audit_trail_post_save', self._audit_trail_post_save)

        # Accounting signals
        self.signal_manager.register_signal('cash_entry_post_save', self._cash_entry_post_save)
        self.signal_manager.register_signal('income_expense_post_save', self._income_expense_post_save)

        # Delete signals
        self.signal_manager.register_signal('cache_entry_post_delete', self._cache_entry_post_delete)
        self.signal_manager.register_signal('request_log_post_delete', self._request_log_post_delete)

    @staticmethod
    def safe_signal_execution(func: Callable) -> Callable:
        """Decorator to safely execute FBS signals without breaking host operations - PRESERVED from Django"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"FBS signal {func.__name__} failed: {e}")
                # Log the error but don't break the main operation
                return None
        return wrapper

    @safe_signal_execution
    async def _odoo_database_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for OdooDatabase - PRESERVED from Django"""
        if created:
            logger.info(f"New Odoo database created: {getattr(instance, 'name', 'unknown')}")
            # Trigger database setup workflows
            await self.signal_manager.send_signal('database_created', instance=instance)
        else:
            logger.info(f"Odoo database updated: {getattr(instance, 'name', 'unknown')}")

    @safe_signal_execution
    async def _token_mapping_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for TokenMapping - PRESERVED from Django"""
        if created:
            logger.info(f"New token mapping created for user: {getattr(instance, 'user_id', 'unknown')}")
            # Trigger authentication setup
            await self.signal_manager.send_signal('token_mapping_created', instance=instance)
        else:
            logger.info(f"Token mapping updated for user: {getattr(instance, 'user_id', 'unknown')}")

    @safe_signal_execution
    async def _request_log_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for RequestLog - PRESERVED from Django"""
        if created:
            logger.debug(f"Request logged: {getattr(instance, 'method', 'unknown')} {getattr(instance, 'path', 'unknown')}")

    @safe_signal_execution
    async def _business_rule_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for BusinessRule - PRESERVED from Django"""
        if created:
            logger.info(f"New business rule created: {getattr(instance, 'name', 'unknown')}")
            # Trigger rule validation and deployment
            await self.signal_manager.send_signal('business_rule_created', instance=instance)
        else:
            logger.info(f"Business rule updated: {getattr(instance, 'name', 'unknown')}")
            # Trigger rule update workflows
            await self.signal_manager.send_signal('business_rule_updated', instance=instance)

    @safe_signal_execution
    async def _cache_entry_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for CacheEntry - PRESERVED from Django"""
        if created:
            logger.debug(f"New cache entry created: {getattr(instance, 'key', 'unknown')}")
        else:
            logger.debug(f"Cache entry updated: {getattr(instance, 'key', 'unknown')}")

    @safe_signal_execution
    async def _handshake_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for Handshake - PRESERVED from Django"""
        if created:
            logger.info(f"New handshake created for solution: {getattr(instance, 'solution_name', 'unknown')}")
            # Trigger security monitoring
            await self.signal_manager.send_signal('handshake_created', instance=instance)
        else:
            logger.info(f"Handshake updated for solution: {getattr(instance, 'solution_name', 'unknown')}")

    @safe_signal_execution
    async def _notification_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for Notification - PRESERVED from Django"""
        if created:
            logger.info(f"New notification created for user: {getattr(instance, 'user_id', 'unknown')}")
            # Trigger notification delivery
            await self.signal_manager.send_signal('notification_created', instance=instance)
        else:
            logger.debug(f"Notification updated for user: {getattr(instance, 'user_id', 'unknown')}")

    @safe_signal_execution
    async def _msme_setup_wizard_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for MSMESetupWizard - PRESERVED from Django"""
        if created:
            logger.info(f"New MSME setup wizard created for business type: {getattr(instance, 'business_type', 'unknown')}")
            # Trigger business setup workflows
            await self.signal_manager.send_signal('msme_setup_started', instance=instance)
        else:
            logger.info(f"MSME setup wizard updated for business type: {getattr(instance, 'business_type', 'unknown')}")

    @safe_signal_execution
    async def _msme_kpi_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for MSMEKPI - PRESERVED from Django"""
        if created:
            logger.info(f"New MSME KPI created: {getattr(instance, 'name', 'unknown')}")
        else:
            logger.debug(f"MSME KPI updated: {getattr(instance, 'name', 'unknown')}")

    @safe_signal_execution
    async def _workflow_definition_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for WorkflowDefinition - PRESERVED from Django"""
        if created:
            logger.info(f"New workflow definition created: {getattr(instance, 'name', 'unknown')}")
            # Trigger workflow deployment
            await self.signal_manager.send_signal('workflow_definition_created', instance=instance)
        else:
            logger.info(f"Workflow definition updated: {getattr(instance, 'name', 'unknown')}")

    @safe_signal_execution
    async def _workflow_instance_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for WorkflowInstance - PRESERVED from Django"""
        if created:
            logger.info(f"New workflow instance created: {getattr(instance, 'workflow_definition', {}).get('name', 'unknown')}")
        else:
            logger.debug(f"Workflow instance updated: {getattr(instance, 'workflow_definition', {}).get('name', 'unknown')}")

    @safe_signal_execution
    async def _dashboard_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for Dashboard - PRESERVED from Django"""
        if created:
            logger.info(f"New dashboard created: {getattr(instance, 'name', 'unknown')}")
            # Trigger dashboard cache invalidation
            await self.signal_manager.send_signal('dashboard_created', instance=instance)
        else:
            logger.info(f"Dashboard updated: {getattr(instance, 'name', 'unknown')}")

    @safe_signal_execution
    async def _report_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for Report - PRESERVED from Django"""
        if created:
            logger.info(f"New report created: {getattr(instance, 'name', 'unknown')}")
        else:
            logger.info(f"Report updated: {getattr(instance, 'name', 'unknown')}")

    @safe_signal_execution
    async def _compliance_rule_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for ComplianceRule - PRESERVED from Django"""
        if created:
            logger.info(f"New compliance rule created: {getattr(instance, 'name', 'unknown')}")
        else:
            logger.info(f"Compliance rule updated: {getattr(instance, 'name', 'unknown')}")

    @safe_signal_execution
    async def _audit_trail_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for AuditTrail - PRESERVED from Django"""
        if created:
            logger.info(f"New audit trail entry created: {getattr(instance, 'action', 'unknown')}")
        else:
            logger.debug(f"Audit trail entry updated: {getattr(instance, 'action', 'unknown')}")

    @safe_signal_execution
    async def _cash_entry_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for CashEntry - PRESERVED from Django"""
        if created:
            logger.info(f"New cash entry created: {getattr(instance, 'entry_type', 'unknown')} - {getattr(instance, 'amount', 0)}")
            # Trigger financial calculations
            await self.signal_manager.send_signal('cash_entry_created', instance=instance)
        else:
            logger.debug(f"Cash entry updated: {getattr(instance, 'entry_type', 'unknown')} - {getattr(instance, 'amount', 0)}")

    @safe_signal_execution
    async def _income_expense_post_save(self, instance, created: bool, **kwargs) -> None:
        """Handle post-save for IncomeExpense - PRESERVED from Django"""
        if created:
            logger.info(f"New income/expense record created: {getattr(instance, 'transaction_type', 'unknown')} - {getattr(instance, 'amount', 0)}")
            # Trigger financial reporting updates
            await self.signal_manager.send_signal('income_expense_created', instance=instance)
        else:
            logger.debug(f"Income/expense record updated: {getattr(instance, 'transaction_type', 'unknown')} - {getattr(instance, 'amount', 0)}")

    @safe_signal_execution
    async def _cache_entry_post_delete(self, instance, **kwargs) -> None:
        """Handle post-delete for CacheEntry - PRESERVED from Django"""
        try:
            logger.debug(f"Cache entry deleted: {getattr(instance, 'key', 'unknown')}")
        except Exception as e:
            logger.warning(f"Error in cache_entry_post_delete signal: {e}")

    @safe_signal_execution
    async def _request_log_post_delete(self, instance, **kwargs) -> None:
        """Handle post-delete for RequestLog - PRESERVED from Django"""
        try:
            logger.debug(f"Request log deleted: {getattr(instance, 'method', 'unknown')} {getattr(instance, 'path', 'unknown')}")
        except Exception as e:
            logger.warning(f"Error in request_log_post_delete signal: {e}")

    async def register_custom_signal(self, signal_name: str, handler: Callable) -> Dict[str, Any]:
        """Register a custom signal handler"""
        try:
            self.signal_manager.register_signal(signal_name, handler)
            return {
                'success': True,
                'message': f'Custom signal {signal_name} registered successfully'
            }
        except Exception as e:
            logger.error(f"Error registering custom signal {signal_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def send_custom_signal(self, signal_name: str, **kwargs) -> Dict[str, Any]:
        """Send a custom signal"""
        try:
            results = await self.signal_manager.send_signal(signal_name, **kwargs)
            return {
                'success': True,
                'signal_name': signal_name,
                'handlers_called': len(results),
                'results': results
            }
        except Exception as e:
            logger.error(f"Error sending custom signal {signal_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_signal_stats(self) -> Dict[str, Any]:
        """Get statistics about registered signals"""
        try:
            registered_signals = self.signal_manager.get_registered_signals()
            return {
                'success': True,
                'total_signals': len(registered_signals),
                'signal_details': registered_signals,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting signal stats: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def trigger_model_signal(self, model_name: str, operation: str, instance, **kwargs) -> Dict[str, Any]:
        """Trigger a signal for a specific model operation"""
        try:
            signal_name = f"{model_name.lower()}_{operation}"
            results = await self.signal_manager.send_signal(signal_name, instance=instance, **kwargs)

            # Also trigger generic post_save signal
            if operation == 'post_save':
                await self.signal_manager.send_signal('post_save', model=model_name, instance=instance, **kwargs)

            return {
                'success': True,
                'signal_name': signal_name,
                'handlers_called': len(results),
                'model_name': model_name,
                'operation': operation
            }
        except Exception as e:
            logger.error(f"Error triggering model signal {model_name}.{operation}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        signal_stats = self.signal_manager.get_registered_signals()
        return {
            'service': 'signals',
            'status': 'healthy',
            'registered_signals': len(signal_stats),
            'signal_types': list(signal_stats.keys()),
            'timestamp': datetime.now().isoformat()
        }
