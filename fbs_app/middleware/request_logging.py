"""
FBS App Request Logging Middleware

Middleware to log requests for monitoring and debugging.
"""

from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
import time
import logging

logger = logging.getLogger('fbs_app')


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log requests for monitoring"""
    
    def process_request(self, request):
        """Log the start of the request"""
        request.start_time = time.time()
        
        # Log request details
        logger.debug(f"Request started: {request.method} {request.path}")
        
        return None
    
    def process_response(self, request, response):
        """Log the completion of the request"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Get user info
            user = getattr(request, 'user', None)
            user_id = user.id if user and user.is_authenticated else None
            username = user.username if user and user.is_authenticated else 'anonymous'
            
            # Get database info
            database_name = getattr(request, 'database_name', None)
            solution_name = getattr(request, 'solution_name', None)
            
            # Log response details
            logger.info(
                f"Request completed: {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s - "
                f"User: {username} - "
                f"Database: {database_name} - "
                f"Solution: {solution_name}"
            )
            
            # Log to database if RequestLog model is available
            try:
                from ..models.core import RequestLog
                
                # Only log if we have a user or database context
                if user_id or database_name:
                    RequestLog.objects.create(
                        user_id=user_id,
                        database_name=database_name,
                        method=request.method,
                        endpoint=request.path,
                        response_status=response.status_code,
                        response_time=duration,
                        ip_address=self._get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    )
            except Exception as e:
                # Don't fail the request if logging fails
                logger.warning(f"Failed to log request to database: {str(e)}")
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Get user info
            user = getattr(request, 'user', None)
            username = user.username if user and user.is_authenticated else 'anonymous'
            
            # Get database info
            database_name = getattr(request, 'database_name', None)
            
            # Log exception details
            logger.error(
                f"Request failed: {request.method} {request.path} - "
                f"Exception: {str(exception)} - "
                f"Duration: {duration:.3f}s - "
                f"User: {username} - "
                f"Database: {database_name}"
            )
            
            # Log to database if RequestLog model is available
            try:
                from ..models.core import RequestLog
                
                # Only log if we have a user or database context
                if (user and user.is_authenticated) or database_name:
                    RequestLog.objects.create(
                        user_id=user.id if user and user.is_authenticated else None,
                        database_name=database_name,
                        method=request.method,
                        endpoint=request.path,
                        response_status=500,
                        response_time=duration,
                        error_message=str(exception),
                        ip_address=self._get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    )
            except Exception as e:
                # Don't fail the request if logging fails
                logger.warning(f"Failed to log exception to database: {str(e)}")
        
        return None
    
    def _get_client_ip(self, request):
        """Get the client IP address from the request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
