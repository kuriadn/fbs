"""
FBS Token Authentication

Custom JWT-based authentication for FBS multi-tenant architecture.
Supports solution-scoped tokens and API key authentication.
"""
import jwt
import json
from datetime import datetime, timedelta
from typing import Optional, Tuple
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from ..models import FBSSolution, FBSAPIToken


User = get_user_model()


class FBSTokenAuthentication(BaseAuthentication):
    """
    Custom FBS token authentication.

    Supports both JWT tokens and API keys for multi-tenant authentication.
    """

    def authenticate(self, request) -> Optional[Tuple[User, None]]:
        """
        Authenticate the request using FBS token.

        Returns (user, None) if authentication succeeds, None otherwise.
        """
        token = self.get_token_from_request(request)
        if not token:
            return None

        try:
            # Try JWT token first
            payload = self.decode_jwt_token(token)
            if payload:
                return self.authenticate_jwt_payload(payload)

            # Try API key authentication
            return self.authenticate_api_key(token)

        except Exception as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')

    def get_token_from_request(self, request) -> Optional[str]:
        """Extract token from request headers or parameters"""
        # Check Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        elif auth_header.startswith('Token '):
            return auth_header[6:]

        # Check FBS-specific headers
        fbs_token = request.META.get('HTTP_X_FBS_TOKEN')
        if fbs_token:
            return fbs_token

        # Check query parameters (less secure, but useful for debugging)
        token_param = request.GET.get('token') or request.POST.get('token')
        if token_param and getattr(settings, 'DEBUG', False):
            return token_param

        return None

    def decode_jwt_token(self, token: str) -> Optional[dict]:
        """Decode and validate JWT token"""
        try:
            # Get JWT settings
            jwt_config = getattr(settings, 'FBS_CONFIG', {}).get('JWT', {})
            secret_key = jwt_config.get('SECRET_KEY') or getattr(settings, 'SECRET_KEY', 'fbs-jwt-secret')
            algorithm = jwt_config.get('ALGORITHM', 'HS256')

            # Decode token
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])

            # Validate expiration
            if payload.get('exp'):
                exp_timestamp = payload['exp']
                if isinstance(exp_timestamp, int):
                    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.get_current_timezone())
                    if timezone.now() > exp_datetime:
                        return None

            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

    def authenticate_jwt_payload(self, payload: dict) -> Tuple[User, None]:
        """Authenticate user from JWT payload"""
        user_id = payload.get('user_id')
        solution_id = payload.get('solution_id')

        if not user_id or not solution_id:
            raise AuthenticationFailed('Invalid token payload')

        try:
            # Get user and solution
            user = User.objects.select_related('solution').get(id=user_id)
            solution = FBSSolution.objects.get(id=solution_id)

            # Validate solution match
            if user.solution != solution:
                raise AuthenticationFailed('Token solution mismatch')

            # Check if user is active
            if not user.is_active:
                raise AuthenticationFailed('User account is disabled')

            # Check if solution is active
            if not solution.is_active:
                raise AuthenticationFailed('Solution is inactive')

            # Attach solution to request for middleware
            # This will be set by the authentication middleware

            return (user, None)

        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
        except FBSSolution.DoesNotExist:
            raise AuthenticationFailed('Solution not found')

    def authenticate_api_key(self, token: str) -> Optional[Tuple[User, None]]:
        """Authenticate using API key"""
        try:
            # Get API token from database
            api_token = FBSAPIToken.objects.select_related('user__solution').get(
                token=token,
                is_active=True
            )

            # Check expiration
            if api_token.is_expired():
                raise AuthenticationFailed('API token has expired')

            # Check user and solution status
            user = api_token.user
            if not user.is_active:
                raise AuthenticationFailed('User account is disabled')

            if not user.solution.is_active:
                raise AuthenticationFailed('Solution is inactive')

            # Update last used timestamp
            api_token.last_used_at = timezone.now()
            api_token.save(update_fields=['last_used_at'])

            return (user, None)

        except FBSAPIToken.DoesNotExist:
            return None

    @classmethod
    def generate_jwt_token(cls, user: User, solution: FBSSolution,
                          expires_in: Optional[timedelta] = None) -> str:
        """Generate a JWT token for the user"""
        if expires_in is None:
            # Default to 24 hours
            expires_in = timedelta(hours=24)

        # Get JWT settings
        jwt_config = getattr(settings, 'FBS_CONFIG', {}).get('JWT', {})
        secret_key = jwt_config.get('SECRET_KEY') or getattr(settings, 'SECRET_KEY', 'fbs-jwt-secret')
        algorithm = jwt_config.get('ALGORITHM', 'HS256')

        # Create payload
        now = timezone.now()
        payload = {
            'user_id': user.id,
            'username': user.username,
            'solution_id': solution.id,
            'solution_name': solution.name,
            'iat': int(now.timestamp()),
            'exp': int((now + expires_in).timestamp()),
            'iss': 'fbs-suite',
            'aud': 'fbs-api',
        }

        # Generate token
        token = jwt.encode(payload, secret_key, algorithm=algorithm)

        return token

    @classmethod
    def generate_api_key(cls, user: User, name: str, scopes: list = None,
                        expires_at: datetime = None) -> FBSAPIToken:
        """Generate a new API key for the user"""
        import secrets
        import hashlib

        # Generate secure token
        token_plain = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_plain.encode()).hexdigest()

        # Create API token
        api_token = FBSAPIToken.objects.create(
            user=user,
            name=name,
            token=token_hash,  # Store hash for security
            scopes=scopes or ['read'],
            expires_at=expires_at,
        )

        # Return the plain token (only shown once)
        api_token._plain_token = token_plain
        return api_token

    @classmethod
    def validate_token_format(cls, token: str) -> bool:
        """Basic token format validation"""
        if not token or len(token) < 10:
            return False

        # Check for JWT format (three parts separated by dots)
        if '.' in token:
            parts = token.split('.')
            if len(parts) == 3:
                return True

        # Check for API key format (URL-safe base64)
        import string
        allowed_chars = string.ascii_letters + string.digits + '-_'
        return all(c in allowed_chars for c in token)


class FBSHandshakeAuthentication(BaseAuthentication):
    """
    FBS Handshake Authentication for temporary sessions.

    Used during the initial authentication handshake process.
    """

    def authenticate(self, request):
        # Check for handshake token in session
        handshake_token = request.session.get('fbs_handshake_token')
        if not handshake_token:
            return None

        try:
            # Validate handshake token
            cache_key = f'handshake:{handshake_token}'
            user_data = cache.get(cache_key)

            if not user_data:
                return None

            # Get user
            user = User.objects.get(id=user_data['user_id'])

            # Extend handshake validity
            cache.set(cache_key, user_data, timeout=300)  # 5 minutes

            return (user, None)

        except Exception:
            return None


def create_user_session_token(user: User, solution: FBSSolution) -> str:
    """Create a session token for the user"""
    token = FBSTokenAuthentication.generate_jwt_token(user, solution)

    # Cache token for quick validation
    cache_key = f'user_session:{user.id}:{solution.id}'
    cache.set(cache_key, {
        'user_id': user.id,
        'solution_id': solution.id,
        'token': token,
    }, timeout=3600)  # 1 hour

    return token


def validate_session_token(token: str) -> Optional[dict]:
    """Validate a session token and return user info"""
    try:
        payload = FBSTokenAuthentication().decode_jwt_token(token)
        if payload:
            return {
                'user_id': payload['user_id'],
                'solution_id': payload['solution_id'],
                'username': payload['username'],
                'solution_name': payload['solution_name'],
            }
    except Exception:
        pass
    return None

