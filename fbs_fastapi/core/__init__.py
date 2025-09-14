"""
FBS FastAPI Core Package

Core components for FBS FastAPI application including configuration,
database connectivity, middleware, and dependencies.
"""

from .config import FBSConfig, config
from .database import Base, get_db_session
from .middleware import DatabaseRoutingMiddleware, RequestLoggingMiddleware
from .dependencies import get_current_user, get_db_session_for_request

__all__ = [
    'FBSConfig',
    'config',
    'Base',
    'get_db_session',
    'DatabaseRoutingMiddleware',
    'RequestLoggingMiddleware',
    'get_current_user',
    'get_db_session_for_request'
]
