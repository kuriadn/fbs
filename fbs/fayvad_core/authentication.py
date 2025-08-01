from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from .services import AuthService
import logging

logger = logging.getLogger('fayvad_core')


class OdooTokenAuthentication(BaseAuthentication):
    """
    Custom authentication class that validates Odoo tokens
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Odoo token
        """
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Get database name from header or request
        database_name = request.META.get('HTTP_X_DATABASE')
        if not database_name:
            database_name = getattr(request, 'database_name', None)
        
        if not database_name:
            raise AuthenticationFailed('Database name not specified')
        
        # Try to find user with this token and database combination
        try:
            from .models import ApiTokenMapping, OdooDatabase
            
            database = OdooDatabase.objects.get(name=database_name, active=True)
            token_mapping = ApiTokenMapping.objects.select_related('user').get(
                odoo_token=token,
                database=database,
                active=True
            )
            
            if token_mapping.is_expired():
                raise AuthenticationFailed('Token has expired')
            
            # Update last used timestamp
            token_mapping.update_last_used()
            
            # Store database name in request for later use
            request.database_name = database_name
            
            return (token_mapping.user, token)
            
        except (OdooDatabase.DoesNotExist, ApiTokenMapping.DoesNotExist):
            raise AuthenticationFailed('Invalid token or database')
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationFailed('Authentication failed')
    
    def authenticate_header(self, request):
        """
        Return string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return 'Bearer'
