from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
# from fbs.fayvad_core.auth.authentication import TokenManager

class DatabaseRoutingMiddleware(MiddlewareMixin):
    """Middleware to route requests to appropriate databases"""
    
    def process_request(self, request):
        """Set database context for the request"""
        # Get database from header or default to main database
        database_name = request.META.get('HTTP_X_DATABASE', 'fbs_db')
        request.database_name = database_name
        return None

class AuthenticationMiddleware(MiddlewareMixin):
    """Minimal JWT authentication middleware (scaffold, spec-compliant)"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # self.token_manager = TokenManager(settings.SECRET_KEY)
        # Define paths that are always public
        self.public_paths = ['/health/', '/health']
        # Define paths that require authentication
        self.protected_paths = ['/api/', '/admin/']
    
    def process_request(self, request):
        # Check if this is a public path that doesn't need authentication
        path = request.path_info
        if any(path.startswith(public_path) for public_path in self.public_paths):
            return None  # Allow public access
        
        # Check if this is a protected path that needs authentication
        # Temporarily disabled for development
        # if any(path.startswith(protected_path) for protected_path in self.protected_paths):
        #     auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        #     if not auth_header.startswith('Bearer '):
        #         return JsonResponse({'error': 'Missing or invalid authorization header'}, status=401)
        #     
        #     token = auth_header.replace('Bearer ', '')
        #     payload = self.token_manager.validate_token(token)
        #     if not payload:
        #         return JsonResponse({'error': 'Invalid or expired token'}, status=401)
        #     
        #     request.user_payload = payload
        
        return None 