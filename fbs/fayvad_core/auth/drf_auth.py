from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser

class JWTAuthentication(BaseAuthentication):
    """DRF authentication class that works with our JWT middleware"""
    
    def authenticate(self, request):
        # Check if our middleware has already processed the JWT
        user_payload = getattr(request, 'user_payload', None)
        
        if not user_payload:
            # No JWT payload found - return None to allow anonymous access
            # The permission classes will handle whether authentication is required
            return None
            
        # Create a simple user object for DRF
        # We'll use a mock user since we don't need Django's user model
        user = type('User', (), {
            'is_authenticated': True,
            'is_anonymous': False,
            'id': user_payload.get('user_id'),
            'username': user_payload.get('client_id'),
        })()
        
        return (user, None)  # No credentials needed since JWT is already validated 