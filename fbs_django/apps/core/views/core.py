"""
FBS Core API ViewSets

REST API endpoints for core FBS functionality - headless implementation.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.conf import settings
from ..models import FBSSolution, FBSUser, FBSAuditLog, FBSAPIToken, FBSSystemSettings
from ..serializers import (
    FBSSolutionSerializer, FBSUserSerializer, FBSAuditLogSerializer,
    FBSAPITokenSerializer, FBSSystemSettingsSerializer,
    LoginSerializer, TokenRefreshSerializer
)
from ..permissions import IsSolutionAdmin, IsSystemAdmin


class SolutionViewSet(viewsets.ModelViewSet):
    """API for FBS solutions management"""

    queryset = FBSSolution.objects.all()
    serializer_class = FBSSolutionSerializer
    permission_classes = [IsAuthenticated, IsSystemAdmin]
    filterset_fields = ['is_active', 'created_at']
    search_fields = ['name', 'display_name']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter solutions based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user

        # System admins can see all solutions
        if user.is_superuser:
            return queryset

        # Solution admins can only see their own solution
        if hasattr(user, 'is_solution_admin') and user.is_solution_admin:
            return queryset.filter(name=user.solution.name)

        return queryset.none()

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a solution"""
        solution = self.get_object()
        solution.is_active = True
        solution.save()

        # Log audit event
        self._audit_log('activate', 'solution', str(solution.id), {
            'solution_name': solution.name
        })

        return Response({'status': 'activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a solution"""
        solution = self.get_object()
        solution.is_active = False
        solution.save()

        # Log audit event
        self._audit_log('deactivate', 'solution', str(solution.id), {
            'solution_name': solution.name
        })

        return Response({'status': 'deactivated'})

    def _audit_log(self, action, resource_type, resource_id, details=None):
        """Helper method for audit logging"""
        from ..utils.audit import log_audit_event
        log_audit_event(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            solution=getattr(self.request, 'solution', None),
            user=self.request.user,
            details=details or {},
        )


class FBSUserViewSet(viewsets.ModelViewSet):
    """API for FBS user management"""

    queryset = FBSUser.objects.select_related('solution')
    serializer_class = FBSUserSerializer
    permission_classes = [IsAuthenticated, IsSolutionAdmin]
    filterset_fields = ['is_active', 'is_solution_admin', 'solution', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']

    def get_queryset(self):
        """Filter users based on permissions"""
        queryset = super().get_queryset()

        # System admins can see all users
        if self.request.user.is_superuser:
            return queryset

        # Solution admins can only see users in their solution
        return queryset.filter(solution=self.request.user.solution)

    def perform_create(self, serializer):
        """Set solution when creating user"""
        if not self.request.user.is_superuser:
            # Non-superusers can only create users in their solution
            serializer.validated_data['solution'] = self.request.user.solution

        super().perform_create(serializer)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API for viewing audit logs"""

    queryset = FBSAuditLog.objects.select_related('user', 'solution')
    serializer_class = FBSAuditLogSerializer
    permission_classes = [IsAuthenticated, IsSolutionAdmin]
    filterset_fields = ['action', 'resource_type', 'solution', 'timestamp']
    search_fields = ['user__username', 'resource_id', 'details']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Filter audit logs based on permissions"""
        queryset = super().get_queryset()

        # System admins can see all audit logs
        if self.request.user.is_superuser:
            return queryset

        # Solution admins can only see logs for their solution
        return queryset.filter(solution=self.request.user.solution)


class APITokenViewSet(viewsets.ModelViewSet):
    """API for managing API tokens"""

    queryset = FBSAPIToken.objects.select_related('user__solution')
    serializer_class = FBSAPITokenSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'created_at', 'expires_at']
    search_fields = ['name', 'user__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Users can only manage their own tokens"""
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        """Associate token with current user"""
        serializer.save(user=self.request.user)


class SystemSettingsViewSet(viewsets.ModelViewSet):
    """API for system settings management"""

    queryset = FBSSystemSettings.objects.all()
    serializer_class = FBSSystemSettingsSerializer
    permission_classes = [IsAuthenticated, IsSystemAdmin]
    filterset_fields = ['setting_type', 'is_system_setting']
    search_fields = ['key', 'description']
    ordering = ['key']

    def get_queryset(self):
        """Only system admins can access system settings"""
        return super().get_queryset()


class LoginView(APIView):
    """Authentication endpoint"""

    permission_classes = []

    def post(self, request):
        """Authenticate user and return token"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT token
        from ..authentication.token_auth import FBSTokenAuthentication
        token = FBSTokenAuthentication.generate_jwt_token(
            user, user.solution
        )

        # Log successful login
        from ..utils.audit import log_audit_event
        log_audit_event(
            action='login',
            resource_type='user',
            resource_id=str(user.id),
            solution=user.solution,
            user=user,
            details={'method': 'api'}
        )

        return Response({
            'token': token,
            'user': FBSUserSerializer(user).data,
            'solution': FBSSolutionSerializer(user.solution).data,
        })


class LogoutView(APIView):
    """Logout endpoint"""

    def post(self, request):
        """Log user out"""
        if request.user.is_authenticated:
            # Log logout event
            from ..utils.audit import log_audit_event
            log_audit_event(
                action='logout',
                resource_type='user',
                resource_id=str(request.user.id),
                solution=request.user.solution,
                user=request.user,
                details={'method': 'api'}
            )

        return Response({'message': 'Logged out successfully'})


class TokenRefreshView(APIView):
    """Token refresh endpoint"""

    def post(self, request):
        """Refresh JWT token"""
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate current token
        from ..authentication.token_auth import FBSTokenAuthentication
        auth = FBSTokenAuthentication()
        payload = auth.decode_jwt_token(serializer.validated_data['token'])

        if not payload:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate new token
        from ..models import FBSUser, FBSSolution
        user = FBSUser.objects.get(id=payload['user_id'])
        solution = FBSSolution.objects.get(id=payload['solution_id'])

        new_token = FBSTokenAuthentication.generate_jwt_token(user, solution)

        return Response({'token': new_token})


class SystemInfoView(APIView):
    """System information endpoint"""

    def get(self, request):
        """Get system information"""
        return Response({
            'fbs_version': '4.0.0',
            'django_version': '4.2.7',
            'python_version': '3.11',
            'timestamp': timezone.now().isoformat(),
            'environment': 'development' if settings.DEBUG else 'production',
            'features': {
                'multi_tenant': True,
                'odoo_integration': True,
                'module_generation': True,
                'dms': True,
                'workflows': True,
                'bi': True,
                'compliance': True,
                'accounting': True,
                'notifications': True,
            }
        })
