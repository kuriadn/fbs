from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import RequestLog
from .services import AuthService
import time
import logging

logger = logging.getLogger('fayvad_core')


class DatabaseRoutingMiddleware(MiddlewareMixin):
    """Middleware to handle database routing based on headers or tokens"""
    
    def process_request(self, request):
        """Process incoming request to determine database routing"""
        # Get database name from header or token
        database_name = request.META.get('HTTP_X_DATABASE')
        
        if not database_name and request.user.is_authenticated:
            # Try to get from user's available databases
            databases = AuthService.get_user_databases(request.user)
            if databases:
                database_name = databases[0]['name']  # Use first available database
        
        # Store database name in request for later use
        request.database_name = database_name
        
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log API requests for monitoring"""
    
    def process_request(self, request):
        """Start timing the request"""
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log the completed request"""
        try:
            # Only log API requests
            if request.path.startswith('/api/'):
                response_time = time.time() - getattr(request, 'start_time', time.time())
                
                # Get database from request
                database_name = getattr(request, 'database_name', None)
                database = None
                
                if database_name:
                    from .models import OdooDatabase
                    try:
                        database = OdooDatabase.objects.get(name=database_name, active=True)
                    except OdooDatabase.DoesNotExist:
                        pass
                
                # Parse request data
                request_data = {}
                if hasattr(request, 'data'):
                    request_data = request.data
                elif request.method in ['POST', 'PUT', 'PATCH']:
                    try:
                        import json
                        request_data = json.loads(request.body.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_data = {}
                
                # Extract model name and record ID from URL
                model_name = ''
                record_id = None
                
                path_parts = request.path.split('/')
                if len(path_parts) >= 4 and path_parts[2] == 'v1':
                    model_name = path_parts[3]
                    if len(path_parts) >= 5 and path_parts[4].isdigit():
                        record_id = int(path_parts[4])
                
                # Create log entry
                RequestLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    database=database,
                    method=request.method,
                    endpoint=request.path,
                    model_name=model_name,
                    record_id=record_id,
                    request_data=request_data,
                    response_status=response.status_code,
                    response_time=response_time,
                    error_message=getattr(response, 'error_message', ''),
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
        except Exception as e:
            logger.error(f"Error logging request: {str(e)}")
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions"""
        try:
            if request.path.startswith('/api/'):
                response_time = time.time() - getattr(request, 'start_time', time.time())
                
                # Get database from request
                database_name = getattr(request, 'database_name', None)
                database = None
                
                if database_name:
                    from .models import OdooDatabase
                    try:
                        database = OdooDatabase.objects.get(name=database_name, active=True)
                    except OdooDatabase.DoesNotExist:
                        pass
                
                # Create log entry for exception
                RequestLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    database=database,
                    method=request.method,
                    endpoint=request.path,
                    response_status=500,
                    response_time=response_time,
                    error_message=str(exception),
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
        except Exception as e:
            logger.error(f"Error logging exception: {str(e)}")
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
