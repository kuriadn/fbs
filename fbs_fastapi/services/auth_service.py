"""
FBS FastAPI Authentication Service

PRESERVED from Django auth_service.py
Service for managing handshake authentication and user sessions.
"""

import secrets
import logging
from datetime import timedelta, datetime
from typing import Optional, Dict, Any, List
import uuid

from .service_interfaces import BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class AuthService(BaseService, AsyncServiceMixin):
    """Service for managing authentication and handshakes - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)
        # Get from FastAPI config
        from ..core.config import config
        self.handshake_expiry_hours = getattr(config, 'fbs_handshake_expiry_hours', 24)

    async def create_handshake(self, secret_key: Optional[str] = None,
                              expiry_hours: Optional[int] = None) -> Dict[str, Any]:
        """Create a new handshake for system authentication - PRESERVED from Django"""
        try:
            from ..models.models import Handshake

            # Generate secure handshake ID and secret key
            handshake_id = secrets.token_urlsafe(32)
            if not secret_key:
                secret_key = secrets.token_urlsafe(32)

            # Set expiry time
            expiry_hours = expiry_hours or self.handshake_expiry_hours
            expires_at = datetime.now() + timedelta(hours=expiry_hours)

            # Create handshake
            handshake = Handshake(
                handshake_id=handshake_id,
                solution_name=self.solution_name,
                secret_key=secret_key,
                status='pending',
                expires_at=expires_at
            )

            # Save to database
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):
                db.add(handshake)
                await db.commit()
                await db.refresh(handshake)

            logger.info(f"Created handshake for {self.solution_name}")

            return {
                'success': True,
                'data': {
                    'handshake_id': handshake_id,
                    'secret_key': secret_key,
                    'expires_at': expires_at.isoformat(),
                    'id': str(handshake.id)
                },
                'message': 'Handshake created successfully'
            }

        except Exception as e:
            logger.error(f"Error creating handshake: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def validate_handshake(self, handshake_id: str, secret_key: str) -> Dict[str, Any]:
        """Validate a handshake ID and secret key - PRESERVED from Django"""
        try:
            from ..models.models import Handshake
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Find handshake for this solution
                handshake = await db.query(Handshake).filter(
                    Handshake.handshake_id == handshake_id,
                    Handshake.status == 'active',
                    Handshake.solution_name == self.solution_name
                ).first()

                if not handshake:
                    return {
                        'success': False,
                        'error': 'Invalid token',
                        'message': 'Handshake token not found'
                    }

                # Validate secret key
                if handshake.secret_key != secret_key:
                    return {
                        'success': False,
                        'error': 'Invalid secret key',
                        'message': 'Handshake secret key is invalid'
                    }

                # Check expiry
                if datetime.now() > handshake.expires_at:
                    # Mark as expired
                    handshake.status = 'expired'
                    await db.commit()

                    return {
                        'success': False,
                        'error': 'Expired handshake',
                        'message': 'Handshake has expired'
                    }

                # Update last used
                handshake.last_used = datetime.now()
                await db.commit()

                return {
                    'success': True,
                    'data': {
                        'handshake': handshake,
                        'user': handshake.user,
                        'database': handshake.database,
                        'system_name': handshake.system_name,
                        'permissions': handshake.permissions,
                        'expires_at': handshake.expires_at.isoformat()
                    },
                    'message': 'Handshake validated successfully'
                }

        except Exception as e:
            logger.error(f"Error validating handshake: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def revoke_handshake(self, handshake_id: str) -> Dict[str, Any]:
        """Revoke a handshake - PRESERVED from Django"""
        try:
            from ..models.models import Handshake
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Find and revoke handshake
                handshake = await db.query(Handshake).filter(
                    Handshake.handshake_id == handshake_id,
                    Handshake.status == 'active'
                ).first()

                if not handshake:
                    return {
                        'success': False,
                        'error': 'Handshake not found',
                        'message': 'Handshake not found'
                    }

                handshake.status = 'revoked'
                await db.commit()

                logger.info(f"Revoked handshake for {handshake.solution_name}")

                return {
                    'success': True,
                    'message': 'Handshake revoked successfully'
                }

        except Exception as e:
            logger.error(f"Error revoking handshake: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_active_handshakes(self, solution_name: Optional[str] = None) -> Dict[str, Any]:
        """Get active handshakes for a solution - PRESERVED from Django"""
        try:
            from ..models.models import Handshake
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Build query
                query = db.query(Handshake).filter(Handshake.status == 'active')
                if solution_name:
                    query = query.filter(Handshake.solution_name == solution_name)

                # Get handshakes
                handshakes = await query.all()

                # Filter out expired handshakes
                active_handshakes = []
                for handshake in handshakes:
                    if datetime.now() <= handshake.expires_at:
                        active_handshakes.append(handshake)
                    else:
                        # Mark expired handshakes as expired
                        handshake.status = 'expired'

                await db.commit()

                return {
                    'success': True,
                    'data': {
                        'handshakes': active_handshakes,
                        'count': len(active_handshakes)
                    },
                    'message': f'Found {len(active_handshakes)} active handshakes'
                }

        except Exception as e:
            logger.error(f"Error getting active handshakes: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def cleanup_expired_handshakes(self) -> Dict[str, Any]:
        """Clean up expired handshakes - PRESERVED from Django"""
        try:
            from ..models.models import Handshake
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Find expired handshakes
                expired_handshakes = await db.query(Handshake).filter(
                    Handshake.status == 'active',
                    Handshake.expires_at < datetime.now()
                ).all()

                count = len(expired_handshakes)

                # Mark expired handshakes as expired
                for handshake in expired_handshakes:
                    handshake.status = 'expired'

                await db.commit()

                logger.info(f"Cleaned up {count} expired handshakes")

                return {
                    'success': True,
                    'data': {'cleaned_count': count},
                    'message': f'Cleaned up {count} expired handshakes'
                }

        except Exception as e:
            logger.error(f"Error cleaning up expired handshakes: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def create_token_mapping(self, user_id: str, database_name: str,
                                  odoo_token: str, odoo_user_id: int,
                                  expiry_hours: Optional[int] = None) -> Dict[str, Any]:
        """Create token mapping for Odoo integration - PRESERVED from Django"""
        try:
            from ..models.models import TokenMapping, OdooDatabase
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get or create database
                database = await db.query(OdooDatabase).filter(
                    OdooDatabase.name == database_name
                ).first()

                if not database:
                    # Get from FastAPI config
                    from ..core.config import config
                    database = OdooDatabase(
                        name=database_name,
                        display_name=database_name.replace('_', ' ').title(),
                        odoo_db_name=database_name,
                        base_url=config.odoo_base_url,
                        active=True
                    )
                    db.add(database)

                # Set expiry time
                expiry_hours = expiry_hours or self.handshake_expiry_hours
                expires_at = datetime.now() + timedelta(hours=expiry_hours) if expiry_hours > 0 else None

                # Create token mapping
                token_mapping = TokenMapping(
                    user_id=user_id,
                    database=database,
                    token=odoo_token,
                    odoo_user_id=odoo_user_id,
                    expires_at=expires_at,
                    is_active=True
                )

                db.add(token_mapping)
                await db.commit()
                await db.refresh(token_mapping)

                logger.info(f"Created token mapping for {user_id} -> {database_name}")

                return {
                    'success': True,
                    'data': {
                        'token_mapping_id': str(token_mapping.id),
                        'expires_at': expires_at.isoformat() if expires_at else None
                    },
                    'message': 'Token mapping created successfully'
                }

        except Exception as e:
            logger.error(f"Error creating token mapping: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def create_jwt_token(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a JWT token for user authentication"""
        try:
            import jwt
            from datetime import datetime, timedelta
            from ..core.config import config

            # Prepare token payload
            now = datetime.utcnow()
            expiry = now + timedelta(hours=config.jwt_expiry_hours)

            payload = {
                'user_id': user_data.get('user_id'),
                'username': user_data.get('username', user_data.get('user_id')),
                'email': user_data.get('email'),
                'role': user_data.get('role', 'user'),
                'permissions': user_data.get('permissions', ['read']),
                'iat': now.timestamp(),
                'exp': expiry.timestamp(),
                'iss': 'fbs-api',
                'aud': 'fbs-client'
            }

            # Generate JWT token
            token = jwt.encode(payload, config.jwt_secret_key, algorithm=config.jwt_algorithm)

            return {
                'success': True,
                'token': token,
                'token_type': 'bearer',
                'expires_in': config.jwt_expiry_hours * 3600,  # seconds
                'expires_at': expiry.isoformat(),
                'user': {
                    'user_id': payload['user_id'],
                    'username': payload['username'],
                    'role': payload['role']
                }
            }

        except ImportError:
            logger.error("PyJWT not installed, cannot create JWT tokens")
            return {
                'success': False,
                'error': 'JWT library not available',
                'message': 'PyJWT must be installed to use JWT authentication'
            }
        except Exception as e:
            logger.error(f"Error creating JWT token: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token"""
        try:
            import jwt
            from datetime import datetime
            from ..core.config import config

            # Decode and validate token
            payload = jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])

            # Check expiration
            exp = payload.get('exp')
            if exp and datetime.utcnow().timestamp() > exp:
                return {
                    'success': False,
                    'error': 'Token expired',
                    'message': 'JWT token has expired'
                }

            return {
                'success': True,
                'payload': payload,
                'user': {
                    'user_id': payload.get('user_id'),
                    'username': payload.get('username'),
                    'role': payload.get('role', 'user'),
                    'permissions': payload.get('permissions', ['read'])
                }
            }

        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'Token expired',
                'message': 'JWT token has expired'
            }
        except jwt.InvalidSignatureError:
            return {
                'success': False,
                'error': 'Invalid signature',
                'message': 'JWT token signature is invalid'
            }
        except jwt.DecodeError:
            return {
                'success': False,
                'error': 'Invalid token',
                'message': 'JWT token is malformed or invalid'
            }
        except Exception as e:
            logger.error(f"Error validating JWT token: {str(e)}")
            return {
                'success': False,
                'error': 'Validation error',
                'message': str(e)
            }

    async def validate_token_mapping(self, token: str, database_name: str) -> Dict[str, Any]:
        """Validate token mapping - PRESERVED from Django"""
        try:
            from ..models.models import TokenMapping
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Find active token mapping
                token_mapping = await db.query(TokenMapping).filter(
                    TokenMapping.token == token,
                    TokenMapping.is_active == True,
                    TokenMapping.database.has(name=database_name)
                ).first()

                if not token_mapping:
                    return {
                        'success': False,
                        'error': 'Invalid token',
                        'message': 'Token mapping not found'
                    }

                # Check expiry
                if token_mapping.expires_at and datetime.now() > token_mapping.expires_at:
                    # Mark as inactive
                    token_mapping.is_active = False
                    await db.commit()

                    return {
                        'success': False,
                        'error': 'Expired token',
                        'message': 'Token mapping has expired'
                    }

                return {
                    'success': True,
                    'data': {
                        'user_id': token_mapping.user_id,
                        'database': token_mapping.database,
                        'odoo_user_id': token_mapping.odoo_user_id,
                        'expires_at': token_mapping.expires_at.isoformat() if token_mapping.expires_at else None
                    },
                    'message': 'Token mapping validated successfully'
                }

        except Exception as e:
            logger.error(f"Error validating token mapping: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def revoke_token_mapping(self, token_mapping_id: str) -> Dict[str, Any]:
        """Revoke token mapping - PRESERVED from Django"""
        try:
            from ..models.models import TokenMapping
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Find and revoke token mapping
                token_mapping = await db.query(TokenMapping).filter(
                    TokenMapping.id == token_mapping_id,
                    TokenMapping.is_active == True
                ).first()

                if not token_mapping:
                    return {
                        'success': False,
                        'error': 'Token mapping not found',
                        'message': 'Token mapping not found'
                    }

                token_mapping.is_active = False
                await db.commit()

                logger.info(f"Revoked token mapping {token_mapping_id}")

                return {
                    'success': True,
                    'message': 'Token mapping revoked successfully'
                }

        except Exception as e:
            logger.error(f"Error revoking token mapping: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_user_token_mappings(self, user_id: str) -> Dict[str, Any]:
        """Get all token mappings for a user - PRESERVED from Django"""
        try:
            from ..models.models import TokenMapping
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get active token mappings
                token_mappings = await db.query(TokenMapping).filter(
                    TokenMapping.user_id == user_id,
                    TokenMapping.is_active == True
                ).all()

                # Filter out expired mappings
                active_mappings = []
                for mapping in token_mappings:
                    if not mapping.expires_at or datetime.now() <= mapping.expires_at:
                        active_mappings.append(mapping)
                    else:
                        # Mark expired mappings as inactive
                        mapping.is_active = False

                await db.commit()

                return {
                    'success': True,
                    'data': {
                        'token_mappings': active_mappings,
                        'count': len(active_mappings)
                    },
                    'message': f'Found {len(active_mappings)} active token mappings'
                }

        except Exception as e:
            logger.error(f"Error getting user token mappings: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'auth',
            'status': 'healthy',
            'handshake_expiry_hours': self.handshake_expiry_hours,
            'timestamp': datetime.now().isoformat()
        }
