import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('fayvad_core')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and responses
    """
    
    def process_request(self, request):
        """Log the incoming request"""
        request.start_time = time.time()
        
        # Log request details
        logger.info(f"Request: {request.method} {request.path} - User: {getattr(request.user, 'username', 'Anonymous')}")
        
        return None
    
    def process_response(self, request, response):
        """Log the response"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f"Response: {request.method} {request.path} - Status: {response.status_code} - Duration: {duration:.3f}s")
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions"""
        logger.error(f"Exception: {request.method} {request.path} - Error: {str(exception)}")
        return None 