"""
FBS FastAPI Dependencies

Dependency injection system for services, database sessions, and authentication.
FastAPI equivalent of Django's service instantiation.
"""

from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, AsyncGenerator
import logging

from .database import get_db_session
from .config import config

logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE DEPENDENCIES
# ============================================================================

def get_current_solution(request: Request) -> str:
    """
    Extract current solution name from request state.

    Args:
        request: FastAPI request object

    Returns:
        Solution name string
    """
    return getattr(request.state, 'solution_name', 'system')

def get_current_database(request: Request) -> str:
    """
    Extract current database name from request state.

    Args:
        request: FastAPI request object

    Returns:
        Database name string
    """
    return getattr(request.state, 'database_name', 'fbs_system_db')

async def get_db_session_for_request(
    request: Request
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for current request's solution.

    Args:
        request: FastAPI request object

    Yields:
        AsyncSession: Database session for current solution
    """
    solution_name = get_current_solution(request)
    database_name = get_current_database(request)

    # Map solution to database
    if solution_name == 'system':
        db_name = 'fbs_system_db'
    else:
        db_name = f"fbs_{solution_name}_db"

    async for session in get_db_session(db_name):
        yield session

# Alias for backward compatibility
get_db_session_for_solution = get_db_session_for_request

# ============================================================================
# SERVICE DEPENDENCIES
# ============================================================================

def get_odoo_client(request: Request = None):
    """
    Get Odoo client for current solution.

    Args:
        request: FastAPI request object (optional for backward compatibility)

    Returns:
        OdooClient instance
    """
    try:
        from ..services.odoo_client import OdooClient

        solution_name = None
        if request:
            solution_name = get_current_solution(request)

        return OdooClient(
            solution_name=solution_name,
            base_url=config.odoo_base_url,
            timeout=config.odoo_timeout
        )
    except ImportError:
        logger.warning("OdooClient not yet implemented")
        return None

# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db_session_for_request)
) -> Optional[dict]:
    """
    Get current authenticated user (optional).

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        User info dict or None if not authenticated
    """
    # Extract token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.replace('Bearer ', '').strip()
    if not token:
        return None

    # Implement token validation
    # Check for handshake token first, then JWT if available
    try:
        # Check for handshake token
        if token.startswith("handshake_"):
            handshake_token = token.replace("handshake_", "")
            from ..services.auth_service import AuthService
            auth_service = AuthService("system")
            result = await auth_service.validate_handshake(handshake_token, "")
            if result['success']:
                return {
                    "user_id": result['data']['handshake'].solution_name,
                    "username": result['data']['handshake'].solution_name,
                    "permissions": ["read", "write"],
                    "auth_type": "handshake",
                    "handshake_id": handshake_token
                }

        # Check for JWT token implementation
        try:
            import jwt
            from datetime import datetime, timedelta

            # Get JWT secret from config
            from ..core.config import config
            jwt_secret = config.jwt_secret_key

            # Decode and validate JWT token
            try:
                payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])

                # Check if token is expired
                exp = payload.get('exp')
                if exp and datetime.utcnow().timestamp() > exp:
                    logger.warning("JWT token has expired")
                    return None

                # Extract user information from payload
                user_id = payload.get('user_id')
                username = payload.get('username', user_id)
                permissions = payload.get('permissions', ['read'])
                role = payload.get('role', 'user')

                logger.debug(f"JWT token validated for user: {username}")

                return {
                    "user_id": user_id,
                    "username": username,
                    "permissions": permissions,
                    "auth_type": "jwt",
                    "role": role,
                    "token_payload": payload
                }

            except jwt.ExpiredSignatureError:
                logger.warning("JWT token signature has expired")
                return None
            except jwt.InvalidSignatureError:
                logger.warning("JWT token has invalid signature")
                return None
            except jwt.DecodeError as e:
                logger.warning(f"JWT token decode error: {str(e)}")
                return None

        except ImportError:
            logger.warning("PyJWT not installed, JWT validation disabled")
            return None
        except Exception as e:
            logger.error(f"JWT validation error: {str(e)}")
            return None

    except Exception as e:
        logger.warning(f"Token validation error: {e}")
        return None

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session_for_request)
) -> dict:
    """
    Get current authenticated user (required).

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        User info dict

    Raises:
        HTTPException: If user is not authenticated
    """
    user = await get_current_user_optional(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_user_with_permissions(
    request: Request,
    required_permissions: Optional[list] = None,
    db: AsyncSession = Depends(get_db_session_for_request)
) -> dict:
    """
    Get current authenticated user with permission check.

    Args:
        request: FastAPI request object
        required_permissions: List of required permissions
        db: Database session

    Returns:
        User info dict

    Raises:
        HTTPException: If user lacks required permissions
    """
    user = await get_current_user(request, db)

    if required_permissions:
        # Implement permission checking
        # Check if user has required permissions
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )

        user_permissions = user.get('permissions', [])

        # Check if user has all required permissions
        missing_permissions = [perm for perm in required_permissions if perm not in user_permissions]

        if missing_permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Missing: {', '.join(missing_permissions)}"
            )

    return user

# ============================================================================
# UTILITY DEPENDENCIES
# ============================================================================

def get_request_id(request: Request) -> str:
    """
    Get or generate request ID for tracing.

    Args:
        request: FastAPI request object

    Returns:
        Request ID string
    """
    # Check if request ID already exists
    request_id = getattr(request.state, 'request_id', None)
    if request_id:
        return request_id

    # Generate new request ID
    import uuid
    request_id = str(uuid.uuid4())

    # Store in request state
    request.state.request_id = request_id
    return request_id

# ============================================================================
# CONDITIONAL DEPENDENCIES
# ============================================================================

def get_auth_service(request: Request = None):
    """Get authentication service for current solution"""
    try:
        from ..services.auth_service import AuthService

        solution_name = None
        if request:
            solution_name = get_current_solution(request)

        return AuthService(solution_name=solution_name)
    except ImportError:
        logger.warning("AuthService not yet implemented")
        return None

def get_workflow_service(request: Request = None, odoo_client = Depends(get_odoo_client)):
    """Get workflow service with Odoo integration"""
    try:
        from ..services.workflow_service import WorkflowService
        return WorkflowService(odoo_client=odoo_client)
    except ImportError:
        logger.warning("WorkflowService not yet implemented")
        return None

def get_business_intelligence_service(request: Request = None):
    """Get business intelligence service"""
    try:
        from ..services.bi_service import BusinessIntelligenceService

        solution_name = None
        if request:
            solution_name = get_current_solution(request)

        return BusinessIntelligenceService(solution_name=solution_name)
    except ImportError:
        logger.warning("BusinessIntelligenceService not yet implemented")
        return None

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Database
    'get_current_solution',
    'get_current_database',
    'get_db_session_for_request',
    'get_db_session_for_solution',

    # Services
    'get_odoo_client',
    'get_auth_service',
    'get_workflow_service',
    'get_business_intelligence_service',

    # Authentication
    'get_current_user_optional',
    'get_current_user',
    'get_current_user_with_permissions',

    # Utilities
    'get_request_id',
]
