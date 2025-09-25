"""
FBS Request Logging Middleware

Comprehensive request logging for audit and monitoring purposes.
"""
import logging
import time
import json
from typing import Dict, Any
from django.conf import settings


logger = logging.getLogger('fbs.requests')


class RequestLoggingMiddleware:
    """
    Middleware for comprehensive request logging.

    Logs all requests with timing, user info, and response details
    for audit and monitoring purposes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timing
        start_time = time.time()

        # Extract request information
        request_info = self._extract_request_info(request)

        try:
            # Process the request
            response = self.get_response(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log successful request
            self._log_request(request_info, response, duration)

            return response

        except Exception as e:
            # Calculate duration for failed requests
            duration = time.time() - start_time

            # Log failed request
            self._log_error(request_info, e, duration)

            # Re-raise the exception
            raise

    def _extract_request_info(self, request) -> Dict[str, Any]:
        """Extract relevant information from the request"""
        info = {
            'method': request.method,
            'path': request.path,
            'query_string': request.META.get('QUERY_STRING', ''),
            'content_type': request.META.get('CONTENT_TYPE', ''),
            'content_length': request.META.get('CONTENT_LENGTH', 0),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'remote_addr': self._get_client_ip(request),
            'referer': request.META.get('HTTP_REFERER', ''),
        }

        # Add user information if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            info['user_id'] = request.user.id
            info['username'] = request.user.username
            if hasattr(request.user, 'solution'):
                info['solution_name'] = request.user.solution.name
        else:
            info['user_id'] = None
            info['username'] = 'anonymous'

        # Add solution context if available
        if hasattr(request, 'solution'):
            info['solution_name'] = request.solution.name

        return info

    def _get_client_ip(self, request) -> str:
        """Get the client's real IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP if there are multiple
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')

        return ip

    def _log_request(self, request_info: Dict[str, Any], response, duration: float):
        """Log a successful request"""
        log_data = {
            **request_info,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'response_content_type': getattr(response, 'get', lambda x: '')('Content-Type'),
            'response_content_length': len(getattr(response, 'content', b'')),
        }

        # Choose log level based on status code
        if 200 <= response.status_code < 400:
            logger.info(f"REQUEST {request_info['method']} {request_info['path']}", extra=log_data)
        elif 400 <= response.status_code < 500:
            logger.warning(f"CLIENT_ERROR {request_info['method']} {request_info['path']}", extra=log_data)
        else:
            logger.error(f"SERVER_ERROR {request_info['method']} {request_info['path']}", extra=log_data)

    def _log_error(self, request_info: Dict[str, Any], error: Exception, duration: float):
        """Log a failed request"""
        log_data = {
            **request_info,
            'duration_ms': round(duration * 1000, 2),
            'error_type': type(error).__name__,
            'error_message': str(error),
        }

        logger.error(f"REQUEST_ERROR {request_info['method']} {request_info['path']}", extra=log_data)


class PerformanceMonitoringMiddleware:
    """
    Middleware for monitoring request performance.

    Tracks slow requests and generates performance metrics.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.slow_request_threshold = getattr(settings, 'FBS_CONFIG', {}).get('SLOW_REQUEST_THRESHOLD', 1000)  # ms

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration_ms = (time.time() - start_time) * 1000

        # Log slow requests
        if duration_ms > self.slow_request_threshold:
            logger.warning(
                f"SLOW_REQUEST {request.method} {request.path} took {duration_ms:.2f}ms",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'duration_ms': duration_ms,
                    'user': getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'anonymous',
                    'solution': getattr(request, 'solution', {}).get('name', 'unknown') if hasattr(request, 'solution') else 'unknown',
                }
            )

        return response

