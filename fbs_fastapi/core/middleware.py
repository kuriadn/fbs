"""
FBS FastAPI Middleware

Custom middleware for database routing, request logging, and authentication.
FastAPI equivalents of Django middleware.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
import logging
import time
import json
from typing import Optional, Dict, Any, List

from .config import config

logger = logging.getLogger(__name__)

class DatabaseRoutingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle database routing based on request context.

    PRESERVES Django's sophisticated multi-database routing system.
    Routes requests to appropriate databases based on solution context.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and determine database routing.

        Priority order (preserved from Django):
        1. Solution-specific database hints (highest priority)
        2. Company ID-based routing
        3. License manager isolation
        4. FBS app models to system database
        5. DMS models to solution or default
        6. Default fallback
        """
        try:
            # Extract solution and database information
            solution_name, database_name = await self._extract_routing_info(request)

            # Add to request state for dependency injection
            request.state.solution_name = solution_name
            request.state.database_name = database_name

            # Log routing decision (preserved from Django)
            logger.debug(f"Database routing: solution={solution_name}, db={database_name}")

        except Exception as e:
            logger.warning(f"Database routing error: {e}")
            # Fallback to default (preserved from Django)
            request.state.solution_name = 'system'
            request.state.database_name = 'fbs_system_db'

        # Continue processing
        response = await call_next(request)
        return response

    async def _extract_routing_info(self, request: Request) -> tuple[str, str]:
        """
        Extract solution and database information from request.

        PRESERVES Django's sophisticated routing logic with priorities.
        """
        # PRIORITY 1: Check for solution-specific database hints (highest priority)
        solution_db = getattr(request.state, 'solution_db', None) or request.headers.get('X-Solution-DB')
        if solution_db and solution_db in await self._get_available_databases():
            logger.debug(f"Routing to solution database: {solution_db}")
            solution_name = solution_db.replace('fbs_', '').replace('_db', '') if solution_db.startswith('fbs_') else 'system'
            return solution_name, solution_db

        # PRIORITY 2: Check for company_id-based routing (only if database exists)
        company_id = request.headers.get('X-Company-ID') or request.query_params.get('company_id')
        if company_id:
            solution_db = f"djo_{company_id}_db"
            if solution_db in await self._get_available_databases():
                logger.debug(f"Routing to company database: {solution_db}")
                return company_id, solution_db

        # PRIORITY 3: License manager models go to default database (embedded licensing)
        if request.url.path.startswith('/api/licensing/') or 'license' in request.url.path:
            return 'system', 'fbs_system_db'

        # PRIORITY 4: FBS app models go to system database (default)
        if request.url.path.startswith('/api/fbs/'):
            return 'system', 'fbs_system_db'

        # PRIORITY 5: DMS models can go to solution databases if specified
        if request.url.path.startswith('/api/dms/'):
            company_id = request.headers.get('X-Company-ID') or request.query_params.get('company_id')
            if company_id:
                solution_db = f"djo_{company_id}_db"
                if solution_db in await self._get_available_databases():
                    return company_id, solution_db
            # Default to system database if no specific routing
            return 'system', 'fbs_system_db'

        # PRIORITY 6: Check handshake authentication context
        handshake_token = request.headers.get('X-Handshake-Token')
        if handshake_token:
            solution_name = await self._validate_handshake_token(handshake_token)
            if solution_name:
                return solution_name, f"fbs_{solution_name}_db"

        # PRIORITY 7: Explicit solution header
        solution_name = request.headers.get('X-Solution')
        if solution_name:
            database_type = request.headers.get('X-Database-Type', 'fbs')
            if database_type == 'fbs':
                return solution_name, f"fbs_{solution_name}_db"
            elif database_type == 'system':
                return solution_name, 'fbs_system_db'
            else:
                return solution_name, f"{database_type}_{solution_name}_db"

        # PRIORITY 8: Query parameters
        solution_name = request.query_params.get('solution')
        if solution_name:
            return solution_name, f"fbs_{solution_name}_db"

        database_name = request.query_params.get('db')
        if database_name:
            if database_name.startswith('fbs_') and database_name.endswith('_db'):
                solution_name = database_name[4:-3]  # Remove 'fbs_' and '_db'
                return solution_name, database_name
            else:
                return 'system', database_name

        # DEFAULT: Fallback to system database
        return 'system', 'fbs_system_db'

    async def _validate_handshake_token(self, token: str) -> Optional[str]:
        """
        Validate handshake token and extract solution name.

        PRESERVED from Django implementation.
        """
        # Implement handshake token validation
        # Check against stored handshake records in database
        try:
            from ..models.models import Handshake
            from .dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                handshake = await db.query(Handshake).filter(
                    Handshake.handshake_id == token,
                    Handshake.status == 'active'
                ).first()

                if handshake and handshake.solution_name:
                    return handshake.solution_name

        except Exception as e:
            logger.warning(f"Error validating handshake token: {e}")

        return None

    async def _get_available_databases(self) -> List[str]:
        """
        Get list of available solution databases.

        PRESERVED from Django router implementation.
        """
        # Query database for available solution databases
        try:
            from ..models.models import OdooDatabase
            from .dependencies import get_db_session_for_request

            databases = []
            async for db in get_db_session_for_request(None):
                odoo_dbs = await db.query(OdooDatabase).filter(
                    OdooDatabase.active == True
                ).all()

                for odoo_db in odoo_dbs:
                    databases.append(odoo_db.name)

            # Also include system database
            if 'fbs_system_db' not in databases:
                databases.append('fbs_system_db')

            return databases

        except Exception as e:
            logger.warning(f"Error getting available databases: {e}")
            # Fallback to common patterns
            return [
                'fbs_system_db',
            'fbs_rental_db',
            'fbs_retail_db',
            'fbs_manufacturing_db',
            'fbs_consulting_db',
            'fbs_ecommerce_db'
        ]

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging.

    Similar to Django's request logging but adapted for FastAPI.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response details"""
        start_time = time.time()

        # Log request
        if config.log_requests:
            await self._log_request(request)

        try:
            # Process request
            response = await call_next(request)

            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Log response
            if config.log_responses:
                await self._log_response(request, response, response_time)

            # Add response time header
            response.headers['X-Response-Time'] = f"{response_time:.2f}ms"

            return response

        except Exception as e:
            # Log error
            response_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request error: {request.method} {request.url.path} "
                f"({response_time:.2f}ms) - Error: {str(e)}"
            )
            raise

    async def _log_request(self, request: Request):
        """Log incoming request details"""
        try:
            # Extract request data
            request_data = {
                'method': request.method,
                'path': request.url.path,
                'query_params': dict(request.query_params),
                'headers': dict(request.headers),
                'client_ip': self._get_client_ip(request),
                'user_agent': request.headers.get('user-agent', ''),
            }

            # Log based on path patterns
            if any(pattern in request.url.path for pattern in ['/auth/', '/health/']):
                # Less detailed logging for auth/health endpoints
                logger.info(
                    f"Request: {request.method} {request.url.path} "
                    f"from {request_data['client_ip']}"
                )
            else:
                # Full logging for business endpoints
                logger.info(
                    f"Request: {request.method} {request.url.path} "
                    f"from {request_data['client_ip']} - "
                    f"Query: {request_data['query_params']}"
                )

        except Exception as e:
            logger.warning(f"Error logging request: {e}")

    async def _log_response(self, request: Request, response: Response, response_time: float):
        """Log response details"""
        try:
            # Determine log level based on status code
            if response.status_code >= 500:
                log_level = logging.ERROR
            elif response.status_code >= 400:
                log_level = logging.WARNING
            else:
                log_level = logging.INFO

            logger.log(
                log_level,
                f"Response: {request.method} {request.url.path} "
                f"-> {response.status_code} ({response_time:.2f}ms)"
            )

        except Exception as e:
            logger.warning(f"Error logging response: {e}")

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check forwarded headers first (for proxy/load balancer)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()

        # Check real IP header
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip

        # Fallback to client host
        client_host = getattr(request.client, 'host', '') if request.client else ''
        return client_host or 'unknown'

def create_cors_middleware() -> CORSMiddleware:
    """
    Create CORS middleware with FBS configuration.

    Returns:
        Configured CORSMiddleware instance
    """
    return CORSMiddleware(
        allow_origins=config.cors_origins,
        allow_credentials=config.cors_allow_credentials,
        allow_methods=config.cors_allow_methods,
        allow_headers=config.cors_allow_headers,
    )

# Export middleware classes
__all__ = [
    'DatabaseRoutingMiddleware',
    'RequestLoggingMiddleware',
    'create_cors_middleware'
]
