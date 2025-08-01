# Services module (scaffold)
from .auth_service import AuthService
from .odoo_client import odoo_client, OdooClientError
from .cache_service import CacheService
from .business_logic import BusinessLogicService

__all__ = [
    'AuthService',
    'odoo_client',
    'OdooClientError', 
    'CacheService',
    'BusinessLogicService'
]
