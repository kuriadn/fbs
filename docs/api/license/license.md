# Fayvad License Manager - Generic API Integration 🔐

Complete integration guide for incorporating the Fayvad License Manager into the Generic Odoo API system, creating a unified licensing and API management solution.

## 🎯 Integration Overview

The License Manager will be integrated as a **core service** within the Generic Odoo API architecture, providing:

- **API Access Control**: License-based endpoint access
- **Feature Gating**: Domain-specific feature restrictions
- **Usage Monitoring**: API usage tracking and limits
- **Multi-Tenant Licensing**: Per-tenant license validation
- **Real-time License Enforcement**: Dynamic access control

## 🏗️ Updated Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Integrated Architecture                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Frontend    │  │ License     │  │ API Gateway │        │
│  │ (Vue/Nuxt)  │  │ Portal      │  │ + Auth      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ License     │  │ Business    │  │ WebSocket   │        │
│  │ Manager     │  │ API Layer   │  │ + Events    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Multi-      │  │ Odoo v17    │  │ License     │        │
│  │ Tenant      │  │ CE + DBs    │  │ Validation  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🔗 Core Integration Points

### **1. Authentication Enhancement**

Update the JWT token to include license information:

```json
{
  "user_id": 123,
  "client_id": "fayvad_production",
  "username": "admin",
  "email": "admin@fayvad.com",
  "role": "admin",
  "permissions": ["read", "create", "update", "delete", "admin"],
  "tenant_id": "fayvad_production",
  "license": {
    "key": "XXXX-XXXX-XXXX-XXXX-XXXX",
    "tier": "professional",
    "tier_name": "Professional",
    "expiry_date": "2024-12-31T23:59:59Z",
    "features": {
      "api_access": true,
      "sales_module": true,
      "hr_module": true,
      "inventory_module": true,
      "manufacturing_module": false,
      "advanced_reporting": true,
      "webhook_support": true,
      "real_time_sync": true
    },
    "limits": {
      "max_users": 50,
      "max_api_requests_per_hour": 5000,
      "max_concurrent_connections": 10
    },
    "status": "active"
  },
  "exp": 1640995200,
  "iat": 1640908800
}
```

### **2. Enhanced Login Endpoint**

```python
# Enhanced login with license validation
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    database = request.data.get('database')
    
    # Authenticate user
    user = authenticate_user(username, password, database)
    if not user:
        return Response({'success': False, 'error': 'Invalid credentials'}, 
                       status=401)
    
    # Validate license for this tenant
    license_validator = LicenseValidator(database)
    license_result = license_validator.validate_license()
    
    if not license_result['success']:
        return Response({
            'success': False,
            'error': 'License validation failed',
            'error_code': 'LICENSE_INVALID',
            'details': license_result
        }, status=403)
    
    # Generate JWT with license info
    token_payload = {
        'user_id': user.id,
        'username': user.username,
        'tenant_id': database,
        'license': license_result['data'],
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')
    
    return Response({
        'success': True,
        'data': {
            'token': token,
            'user': user_data,
            'license': license_result['data']
        }
    })
```

## 🔐 License Middleware Integration

### **License Validation Middleware**

```python
# middleware/license_middleware.py
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from functools import wraps
import jwt
import logging

logger = logging.getLogger(__name__)

class LicenseValidationMiddleware(MiddlewareMixin):
    """
    Middleware to validate license for all API requests
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        # Skip license check for public endpoints
        if self._is_public_endpoint(request.path):
            return None
        
        # Extract license info from JWT
        license_info = self._extract_license_from_token(request)
        if not license_info:
            return JsonResponse({
                'success': False,
                'error': 'License information not found',
                'error_code': 'LICENSE_MISSING'
            }, status=403)
        
        # Validate license
        validator = LicenseValidator(license_info['tenant_id'])
        validation_result = validator.validate_license()
        
        if not validation_result['success']:
            return JsonResponse({
                'success': False,
                'error': 'License validation failed',
                'error_code': 'LICENSE_INVALID',
                'details': validation_result
            }, status=403)
        
        # Check feature access for this endpoint
        if not self._check_feature_access(request.path, license_info):
            return JsonResponse({
                'success': False,
                'error': 'Feature not available in current license tier',
                'error_code': 'FEATURE_NOT_LICENSED',
                'details': {
                    'required_feature': self._get_required_feature(request.path),
                    'current_tier': license_info.get('tier'),
                    'upgrade_url': '/license/upgrade/'
                }
            }, status=403)
        
        # Check usage limits
        if not self._check_usage_limits(request, license_info):
            return JsonResponse({
                'success': False,
                'error': 'License usage limit exceeded',
                'error_code': 'USAGE_LIMIT_EXCEEDED',
                'details': {
                    'limit_type': 'api_requests_per_hour',
                    'current_usage': self._get_current_usage(license_info['tenant_id']),
                    'limit': license_info.get('limits', {}).get('max_api_requests_per_hour')
                }
            }, status=429)
        
        # Store license info in request for later use
        request.license_info = license_info
        return None
    
    def _is_public_endpoint(self, path):
        public_endpoints = [
            '/health/',
            '/api/auth/login/',
            '/api/auth/register/',
            '/license/portal/',
            '/license/activate/',
        ]
        return any(path.startswith(endpoint) for endpoint in public_endpoints)
    
    def _extract_license_from_token(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload.get('license')
        except jwt.InvalidTokenError:
            return None
    
    def _check_feature_access(self, path, license_info):
        feature_map = {
            '/api/sales/': 'sales_module',
            '/api/hr/': 'hr_module',
            '/api/inventory/': 'inventory_module',
            '/api/manufacturing/': 'manufacturing_module',
            '/api/purchasing/': 'purchasing_module',
            '/api/accounting/': 'accounting_module',
            '/ws/': 'real_time_sync',
            '/api/webhooks/': 'webhook_support',
        }
        
        for path_prefix, feature in feature_map.items():
            if path.startswith(path_prefix):
                return license_info.get('features', {}).get(feature, False)
        
        return True  # Allow access if no specific feature required
    
    def _get_required_feature(self, path):
        feature_map = {
            '/api/sales/': 'Sales Module',
            '/api/hr/': 'HR Module',
            '/api/inventory/': 'Inventory Module',
            '/api/manufacturing/': 'Manufacturing Module',
            '/api/purchasing/': 'Purchasing Module',
            '/api/accounting/': 'Accounting Module',
            '/ws/': 'Real-time Sync',
            '/api/webhooks/': 'Webhook Support',
        }
        
        for path_prefix, feature in feature_map.items():
            if path.startswith(path_prefix):
                return feature
                
        return 'Unknown Feature'
    
    def _check_usage_limits(self, request, license_info):
        limits = license_info.get('limits', {})
        tenant_id = license_info.get('tenant_id')
        
        # Check API request limits
        max_requests = limits.get('max_api_requests_per_hour', 0)
        if max_requests > 0:
            current_usage = self._get_current_usage(tenant_id)
            if current_usage >= max_requests:
                return False
        
        # Track this request
        self._track_api_usage(tenant_id)
        return True
    
    def _get_current_usage(self, tenant_id):
        # Implementation to get current API usage from Redis/database
        from django.core.cache import cache
        key = f"api_usage:{tenant_id}:{datetime.now().strftime('%Y%m%d%H')}"
        return cache.get(key, 0)
    
    def _track_api_usage(self, tenant_id):
        # Implementation to track API usage
        from django.core.cache import cache
        key = f"api_usage:{tenant_id}:{datetime.now().strftime('%Y%m%d%H')}"
        current = cache.get(key, 0)
        cache.set(key, current + 1, timeout=3600)  # 1 hour TTL
```

## 🎛️ License Management Endpoints

### **License Status Endpoint**

```python
# views/license_views.py
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def license_status(request):
    """Get current license status and usage"""
    
    license_info = getattr(request, 'license_info', {})
    tenant_id = license_info.get('tenant_id')
    
    if not tenant_id:
        return Response({'success': False, 'error': 'Tenant not found'}, status=400)
    
    # Get detailed license information
    validator = LicenseValidator(tenant_id)
    license_data = validator.get_license_details()
    
    # Get usage statistics
    usage_stats = {
        'api_requests_this_hour': get_api_usage(tenant_id, 'hour'),
        'api_requests_today': get_api_usage(tenant_id, 'day'),
        'active_users': get_active_users_count(tenant_id),
        'concurrent_connections': get_concurrent_connections(tenant_id),
    }
    
    # Calculate days until expiry
    days_until_expiry = None
    if license_data.get('expiry_date'):
        expiry = datetime.fromisoformat(license_data['expiry_date'])
        days_until_expiry = (expiry - datetime.now()).days
    
    return Response({
        'success': True,
        'data': {
            'license': license_data,
            'usage': usage_stats,
            'status': {
                'is_valid': license_data.get('status') == 'active',
                'days_until_expiry': days_until_expiry,
                'usage_percentage': calculate_usage_percentage(usage_stats, license_data.get('limits', {}))
            },
            'alerts': get_license_alerts(license_data, usage_stats)
        }
    })

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def activate_license(request):
    """Activate a license key"""
    
    license_key = request.data.get('license_key')
    client_name = request.data.get('client_name')
    contact_email = request.data.get('contact_email')
    
    if not all([license_key, client_name, contact_email]):
        return Response({
            'success': False,
            'error': 'Missing required fields',
            'required_fields': ['license_key', 'client_name', 'contact_email']
        }, status=400)
    
    try:
        # Use the license activation wizard
        wizard = LicenseActivationWizard.create({
            'license_key': license_key,
            'client_name': client_name,
            'contact_email': contact_email,
            'domain': request.get_host()
        })
        
        # Validate and activate
        wizard.action_validate_key()
        if not wizard.is_valid:
            return Response({
                'success': False,
                'error': 'License validation failed',
                'details': wizard.validation_status
            }, status=400)
        
        wizard.action_activate_license()
        
        return Response({
            'success': True,
            'message': 'License activated successfully',
            'data': {
                'license_key': license_key,
                'tier': wizard.license_key.tier_id.name,
                'expiry_date': wizard.license_key.expiry_date.isoformat() if wizard.license_key.expiry_date else None
            }
        })
        
    except Exception as e:
        logger.error(f"License activation failed: {e}")
        return Response({
            'success': False,
            'error': 'License activation failed',
            'details': str(e)
        }, status=500)
```

## 🔄 WebSocket License Integration

### **Enhanced WebSocket Authentication**

```python
# websocket/license_consumer.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import jwt
from datetime import datetime

class LicenseAwareWebsocketConsumer(AsyncJsonWebsocketConsumer):
    
    async def connect(self):
        # Extract token and validate license
        token = self.scope['query_string'].decode().split('token=')[1].split('&')[0]
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            license_info = payload.get('license', {})
            
            # Check if real-time sync is enabled
            if not license_info.get('features', {}).get('real_time_sync', False):
                await self.close(code=4003)  # Feature not licensed
                return
            
            # Check concurrent connection limits
            max_connections = license_info.get('limits', {}).get('max_concurrent_connections', 0)
            current_connections = await self.get_concurrent_connections(license_info['tenant_id'])
            
            if max_connections > 0 and current_connections >= max_connections:
                await self.close(code=4005)  # Connection limit exceeded
                return
            
            self.license_info = license_info
            self.tenant_id = license_info['tenant_id']
            
            await self.accept()
            await self.track_connection()
            
        except jwt.InvalidTokenError:
            await self.close(code=4002)  # Invalid token
        except Exception as e:
            await self.close(code=4000)  # General error
    
    async def disconnect(self, close_code):
        await self.untrack_connection()
    
    async def receive_json(self, content):
        # Validate license before processing any messages
        if not await self.validate_license():
            await self.send_json({
                'type': 'error',
                'payload': {
                    'error_code': 'LICENSE_EXPIRED',
                    'message': 'License has expired'
                }
            })
            await self.close(code=4001)
            return
        
        # Process message based on license features
        await super().receive_json(content)
    
    @database_sync_to_async
    def validate_license(self):
        validator = LicenseValidator(self.tenant_id)
        result = validator.validate_license()
        return result['success']
    
    @database_sync_to_async
    def get_concurrent_connections(self, tenant_id):
        # Get current connection count from cache/database
        from django.core.cache import cache
        return cache.get(f'ws_connections:{tenant_id}', 0)
    
    @database_sync_to_async
    def track_connection(self):
        from django.core.cache import cache
        key = f'ws_connections:{self.tenant_id}'
        current = cache.get(key, 0)
        cache.set(key, current + 1, timeout=None)
    
    @database_sync_to_async
    def untrack_connection(self):
        from django.core.cache import cache
        key = f'ws_connections:{self.tenant_id}'
        current = cache.get(key, 0)
        cache.set(key, max(0, current - 1), timeout=None)
```

## 🎨 Frontend Integration

### **Enhanced Vue.js Composables**

```typescript
// composables/useLicense.ts
export const useLicense = () => {
  const license = ref(null)
  const isValidLicense = ref(false)
  const licenseAlerts = ref([])
  const usageStats = ref(null)

  const fetchLicenseStatus = async () => {
    try {
      const response = await $fetch('/api/license/status/')
      
      if (response.success) {
        license.value = response.data.license
        isValidLicense.value = response.data.status.is_valid
        licenseAlerts.value = response.data.alerts
        usageStats.value = response.data.usage
      }
    } catch (error) {
      console.error('Failed to fetch license status:', error)
      isValidLicense.value = false
    }
  }

  const activateLicense = async (licenseData) => {
    try {
      const response = await $fetch('/api/license/activate/', {
        method: 'POST',
        body: licenseData
      })

      if (response.success) {
        await fetchLicenseStatus()
        return response
      } else {
        throw new Error(response.error)
      }
    } catch (error) {
      throw error
    }
  }

  const isFeatureEnabled = (feature: string) => {
    return license.value?.features?.[feature] || false
  }

  const getUsagePercentage = (limit: string) => {
    if (!usageStats.value || !license.value?.limits) return 0
    
    const current = usageStats.value[limit] || 0
    const max = license.value.limits[limit] || 0
    
    return max > 0 ? (current / max) * 100 : 0
  }

  return {
    license: readonly(license),
    isValidLicense: readonly(isValidLicense),
    licenseAlerts: readonly(licenseAlerts),
    usageStats: readonly(usageStats),
    fetchLicenseStatus,
    activateLicense,
    isFeatureEnabled,
    getUsagePercentage
  }
}

// composables/useFeatureGate.ts
export const useFeatureGate = () => {
  const { license, isFeatureEnabled } = useLicense()
  const router = useRouter()

  const requireFeature = (feature: string, redirectTo = '/license/upgrade') => {
    if (!isFeatureEnabled(feature)) {
      router.push(redirectTo)
      return false
    }
    return true
  }

  const withFeatureCheck = (feature: string, callback: Function) => {
    if (isFeatureEnabled(feature)) {
      return callback()
    } else {
      throw new Error(`Feature '${feature}' is not available in your current license tier`)
    }
  }

  return {
    requireFeature,
    withFeatureCheck,
    isFeatureEnabled
  }
}
```

### **License-Aware API Client**

```typescript
// sdk/license-aware-api.ts
export class LicenseAwareFayvadAPI extends FayvadAPI {
  private licenseInfo: any = null

  async request<T = any>(endpoint: string, options: RequestInit = {}): Promise<APIResponse<T>> {
    try {
      return await super.request(endpoint, options)
    } catch (error) {
      if (error instanceof FayvadAPIError) {
        // Handle license-specific errors
        switch (error.errorCode) {
          case 'LICENSE_INVALID':
            this.handleLicenseInvalid(error)
            break
          case 'FEATURE_NOT_LICENSED':
            this.handleFeatureNotLicensed(error)
            break
          case 'USAGE_LIMIT_EXCEEDED':
            this.handleUsageLimitExceeded(error)
            break
        }
      }
      throw error
    }
  }

  private handleLicenseInvalid(error: FayvadAPIError) {
    // Redirect to license activation or renewal
    this.emit('license_invalid', error.details)
  }

  private handleFeatureNotLicensed(error: FayvadAPIError) {
    // Show upgrade modal or redirect to upgrade page
    this.emit('feature_not_licensed', {
      feature: error.details.required_feature,
      currentTier: error.details.current_tier,
      upgradeUrl: error.details.upgrade_url
    })
  }

  private handleUsageLimitExceeded(error: FayvadAPIError) {
    // Show usage limit warning
    this.emit('usage_limit_exceeded', {
      limitType: error.details.limit_type,
      currentUsage: error.details.current_usage,
      limit: error.details.limit
    })
  }

  // Enhanced business domain methods with license checks
  get sales() {
    return new LicenseAwareSalesAPI(this)
  }

  get manufacturing() {
    return new LicenseAwareManufacturingAPI(this)
  }

  // License management methods
  async getLicenseStatus() {
    return this.request('/api/license/status/')
  }

  async activateLicense(licenseData: any) {
    return this.request('/api/license/activate/', {
      method: 'POST',
      body: JSON.stringify(licenseData)
    })
  }
}

class LicenseAwareSalesAPI extends SalesAPI {
  async getOrders(filters: SalesOrderFilters = {}): Promise<APIResponse<SalesOrder[]>> {
    // This will automatically handle license validation via middleware
    return super.getOrders(filters)
  }

  async getAdvancedAnalytics(): Promise<APIResponse> {
    // This method requires advanced_reporting feature
    return this.api.request('/api/sales/analytics/advanced/')
  }
}

class LicenseAwareManufacturingAPI {
  constructor(private api: LicenseAwareFayvadAPI) {}

  async getOrders(): Promise<APIResponse> {
    // This will fail if manufacturing_module is not licensed
    return this.api.request('/api/manufacturing/orders/')
  }
}
```

## 🎛️ License Management Dashboard

### **Vue Component for License Dashboard**

```vue
<!-- components/License/LicenseDashboard.vue -->
<template>
  <div class="license-dashboard">
    <div class="license-header">
      <div class="license-info">
        <h2>{{ license?.tier_name || 'Free' }} License</h2>
        <div class="license-status" :class="statusClass">
          {{ licenseStatusText }}
        </div>
      </div>
      <div class="license-actions">
        <Button 
          v-if="!isValidLicense"
          @click="showActivationModal = true"
          severity="success"
        >
          Activate License
        </Button>
        <Button 
          v-else-if="needsUpgrade"
          @click="navigateToUpgrade"
          severity="info"
        >
          Upgrade License
        </Button>
      </div>
    </div>

    <!-- License Details -->
    <div class="license-details" v-if="license">
      <div class="detail-card">
        <h3>License Information</h3>
        <div class="detail-row">
          <span>License Key:</span>
          <code>{{ license.key }}</code>
        </div>
        <div class="detail-row">
          <span>Tier:</span>
          <Tag :value="license.tier_name" :severity="getTierSeverity(license.tier)" />
        </div>
        <div class="detail-row" v-if="license.expiry_date">
          <span>Expires:</span>
          <span>{{ formatDate(license.expiry_date) }}</span>
        </div>
      </div>

      <!-- Usage Statistics -->
      <div class="detail-card">
        <h3>Usage Statistics</h3>
        <div class="usage-item" v-for="(limit, key) in license.limits" :key="key">
          <div class="usage-label">{{ formatLimitLabel(key) }}</div>
          <ProgressBar 
            :value="getUsagePercentage(key)" 
            :showValue="true"
            :class="getUsageClass(key)"
          />
          <div class="usage-text">
            {{ getCurrentUsage(key) }} / {{ limit || 'Unlimited' }}
          </div>
        </div>
      </div>

      <!-- Features -->
      <div class="detail-card">
        <h3>Available Features</h3>
        <div class="features-grid">
          <div 
            v-for="(enabled, feature) in license.features" 
            :key="feature"
            class="feature-item"
            :class="{ enabled, disabled: !enabled }"
          >
            <i :class="enabled ? 'pi pi-check' : 'pi pi-times'"></i>
            {{ formatFeatureName(feature) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Alerts -->
    <div class="license-alerts" v-if="licenseAlerts.length">
      <Message 
        v-for="alert in licenseAlerts" 
        :key="alert.id"
        :severity="alert.severity"
        :closable="true"
      >
        <strong>{{ alert.title }}</strong>
        <p>{{ alert.message }}</p>
      </Message>
    </div>

    <!-- Activation Modal -->
    <Dialog 
      v-model:visible="showActivationModal"
      header="Activate License"
      :modal="true"
      :closable="true"
    >
      <LicenseActivationForm 
        @activated="handleLicenseActivated"
        @cancel="showActivationModal = false"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
const { 
  license, 
  isValidLicense, 
  licenseAlerts, 
  usageStats,
  fetchLicenseStatus,
  getUsagePercentage 
} = useLicense()

const showActivationModal = ref(false)

// Fetch license status on mount
onMounted(() => {
  fetchLicenseStatus()
})

const licenseStatusText = computed(() => {
  if (!license.value) return 'No License'
  if (!isValidLicense.value) return 'Invalid/Expired'
  return 'Active'
})

const statusClass = computed(() => {
  if (!license.value) return 'no-license'
  if (!isValidLicense.value) return 'invalid'
  return 'active'
})

const needsUpgrade = computed(() => {
  return license.value?.tier === 'free' || licenseAlerts.value.some(alert => alert.type === 'upgrade_recommended')
})

const handleLicenseActivated = async () => {
  showActivationModal.value = false
  await fetchLicenseStatus()
}

const navigateToUpgrade = () => {
  navigateTo('/license/upgrade')
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}

const formatLimitLabel = (key: string) => {
  const labels = {
    'max_users': 'Users',
    'max_api_requests_per_hour': 'API Requests/Hour',
    'max_concurrent_connections': 'Concurrent Connections'
  }
  return labels[key] || key
}

const getCurrentUsage = (key: string) => {
  const usageMap = {
    'max_users': 'active_users',
    'max_api_requests_per_hour': 'api_requests_this_hour',
    'max_concurrent_connections': 'concurrent_connections'
  }
  return usageStats.value?.[usageMap[key]] || 0
}

const getUsageClass = (key: string) => {
  const percentage = getUsagePercentage(key)
  if (percentage >= 90) return 'usage-critical'
  if (percentage >= 75) return 'usage-warning'
  return 'usage-normal'
}

const formatFeatureName = (feature: string) => {
  return feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getTierSeverity = (tier: string) => {
  const severities = {
    'free': 'secondary',
    'basic': 'info',
    'professional': 'success',
    'enterprise': 'warning'
  }
  return severities[tier] || 'secondary'
}
</script>

<style scoped>
.license-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.license-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: var(--surface-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.license-info h2 {
  margin: 0 0 8px 0;
  color: var(--text-color);
}

.license-status {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.license-status.active {
  background: var(--green-100);
  color: var(--green-800);
}

.license-status.invalid {
  background: var(--red-100);
  color: var(--red-800);
}

.license-status.no-license {
  background: var(--gray-100);
  color: var(--gray-800);
}

.license-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.detail-card {
  background: var(--surface-card);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.detail-card h3 {
  margin: 0 0 16px 0;
  color: var(--text-color);
  border-bottom: 1px solid var(--surface-border);
  padding-bottom: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.detail-row:not(:last-child) {
  border-bottom: 1px solid var(--surface-border);
}

.usage-item {
  margin-bottom: 16px;
}

.usage-label {
  margin-bottom: 4px;
  font-weight: 500;
  color: var(--text-color);
}

.usage-text {
  margin-top: 4px;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 0.875rem;
}

.feature-item.enabled {
  background: var(--green-50);
  color: var(--green-800);
}

.feature-item.disabled {
  background: var(--gray-50);
  color: var(--gray-600);
}

.feature-item i {
  margin-right: 8px;
}

.license-alerts {
  margin-top: 20px;
}

:deep(.usage-critical .p-progressbar-value) {
  background: var(--red-500);
}

:deep(.usage-warning .p-progressbar-value) {
  background: var(--orange-500);
}

:deep(.usage-normal .p-progressbar-value) {
  background: var(--green-500);
}
</style>
```

## 🔄 Real-time License Updates

### **WebSocket License Events**

```typescript
// Enhanced WebSocket client for license events
class LicensedWebSocketClient extends FayvadWebSocket {
  
  constructor(baseUrl: string, token: string, tenantId: string) {
    super(baseUrl, token, tenantId)
    this.setupLicenseEventHandlers()
  }

  private setupLicenseEventHandlers() {
    // Listen for license events
    this.on('license:expired', this.handleLicenseExpired.bind(this))
    this.on('license:updated', this.handleLicenseUpdated.bind(this))
    this.on('license:limit_exceeded', this.handleLimitExceeded.bind(this))
    this.on('license:feature_disabled', this.handleFeatureDisabled.bind(this))
  }

  private handleLicenseExpired(payload: any) {
    console.warn('License expired:', payload)
    
    // Show expiration modal
    this.emit('show_license_modal', {
      type: 'expired',
      message: 'Your license has expired. Please renew to continue using the service.',
      action: 'renew'
    })
    
    // Optionally disconnect or limit functionality
    this.emit('license_status_changed', { status: 'expired' })
  }

  private handleLicenseUpdated(payload: any) {
    console.log('License updated:', payload)
    
    // Refresh license information
    this.emit('license_refresh_required')
    
    // Show update notification
    this.emit('show_notification', {
      type: 'success',
      message: `License updated to ${payload.new_tier}`
    })
  }

  private handleLimitExceeded(payload: any) {
    console.warn('License limit exceeded:', payload)
    
    // Show limit exceeded warning
    this.emit('show_license_modal', {
      type: 'limit_exceeded',
      message: `${payload.limit_type} limit exceeded (${payload.current}/${payload.max})`,
      action: 'upgrade'
    })
  }

  private handleFeatureDisabled(payload: any) {
    console.warn('Feature disabled:', payload)
    
    // Redirect user away from disabled feature
    this.emit('feature_disabled', {
      feature: payload.feature,
      redirect_to: payload.fallback_url || '/dashboard'
    })
  }
}
```

## 🎛️ Advanced License Features

### **Usage Analytics and Reporting**

```python
# views/license_analytics.py
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def license_analytics(request):
    """Get detailed license usage analytics"""
    
    tenant_id = request.license_info.get('tenant_id')
    timeframe = request.GET.get('timeframe', '30d')  # 24h, 7d, 30d, 90d
    
    analytics_data = {
        'api_usage': get_api_usage_analytics(tenant_id, timeframe),
        'feature_usage': get_feature_usage_analytics(tenant_id, timeframe),
        'user_activity': get_user_activity_analytics(tenant_id, timeframe),
        'peak_usage_times': get_peak_usage_times(tenant_id, timeframe),
        'license_efficiency': calculate_license_efficiency(tenant_id, timeframe)
    }
    
    return Response({
        'success': True,
        'data': analytics_data,
        'timeframe': timeframe
    })

def get_api_usage_analytics(tenant_id, timeframe):
    """Get API usage patterns"""
    from django.core.cache import cache
    import json
    from datetime import datetime, timedelta
    
    # Calculate time range
    end_date = datetime.now()
    if timeframe == '24h':
        start_date = end_date - timedelta(hours=24)
        interval = 'hour'
    elif timeframe == '7d':
        start_date = end_date - timedelta(days=7)
        interval = 'day'
    elif timeframe == '30d':
        start_date = end_date - timedelta(days=30)
        interval = 'day'
    else:  # 90d
        start_date = end_date - timedelta(days=90)
        interval = 'week'
    
    usage_data = []
    current = start_date
    
    while current <= end_date:
        if interval == 'hour':
            key = f"api_usage:{tenant_id}:{current.strftime('%Y%m%d%H')}"
            current += timedelta(hours=1)
        elif interval == 'day':
            key = f"api_usage_daily:{tenant_id}:{current.strftime('%Y%m%d')}"
            current += timedelta(days=1)
        else:  # week
            key = f"api_usage_weekly:{tenant_id}:{current.strftime('%Y%W')}"
            current += timedelta(weeks=1)
        
        usage = cache.get(key, 0)
        usage_data.append({
            'timestamp': current.isoformat(),
            'requests': usage
        })
    
    return {
        'timeline': usage_data,
        'total_requests': sum(item['requests'] for item in usage_data),
        'average_per_period': sum(item['requests'] for item in usage_data) / len(usage_data) if usage_data else 0,
        'peak_usage': max(item['requests'] for item in usage_data) if usage_data else 0
    }

def get_feature_usage_analytics(tenant_id, timeframe):
    """Get feature usage statistics"""
    # Track which API endpoints/features are used most
    feature_usage = cache.get(f"feature_usage:{tenant_id}", {})
    
    return {
        'most_used_features': sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)[:10],
        'total_features_used': len(feature_usage),
        'usage_distribution': feature_usage
    }

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def license_recommendations(request):
    """Get license optimization recommendations"""
    
    tenant_id = request.license_info.get('tenant_id')
    current_license = request.license_info
    
    # Analyze usage patterns
    usage_analytics = get_api_usage_analytics(tenant_id, '30d')
    feature_analytics = get_feature_usage_analytics(tenant_id, '30d')
    
    recommendations = []
    
    # Check if user is over-licensed
    current_tier = current_license.get('tier')
    if current_tier in ['professional', 'enterprise']:
        if usage_analytics['average_per_period'] < 100:  # Low API usage
            recommendations.append({
                'type': 'downgrade',
                'title': 'Consider Downgrading',
                'message': 'Your API usage is low. You might save costs with a lower tier.',
                'potential_savings': calculate_potential_savings(current_tier, 'basic')
            })
    
    # Check if user needs upgrade
    limits = current_license.get('limits', {})
    if limits.get('max_api_requests_per_hour', 0) > 0:
        if usage_analytics['peak_usage'] > limits['max_api_requests_per_hour'] * 0.8:
            recommendations.append({
                'type': 'upgrade',
                'title': 'Consider Upgrading',
                'message': 'You\'re approaching your API limits. Upgrade for better performance.',
                'suggested_tier': get_suggested_upgrade_tier(current_tier)
            })
    
    # Feature-based recommendations
    unused_features = get_unused_features(current_license, feature_analytics)
    if unused_features:
        recommendations.append({
            'type': 'optimization',
            'title': 'Unused Features',
            'message': f'You have {len(unused_features)} unused features in your current plan.',
            'unused_features': unused_features
        })
    
    return Response({
        'success': True,
        'data': {
            'recommendations': recommendations,
            'current_tier': current_tier,
            'usage_summary': {
                'api_usage': usage_analytics,
                'feature_usage': feature_analytics
            }
        }
    })
```

### **License Enforcement Decorators**

```python
# decorators/license_decorators.py
from functools import wraps
from django.http import JsonResponse
from .utils import get_license_info_from_request

def require_license_feature(feature_key):
    """Decorator to require a specific license feature"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            license_info = get_license_info_from_request(request)
            
            if not license_info:
                return JsonResponse({
                    'success': False,
                    'error': 'License information not found',
                    'error_code': 'LICENSE_MISSING'
                }, status=403)
            
            features = license_info.get('features', {})
            if not features.get(feature_key, False):
                return JsonResponse({
                    'success': False,
                    'error': f'Feature "{feature_key}" not available in current license',
                    'error_code': 'FEATURE_NOT_LICENSED',
                    'details': {
                        'required_feature': feature_key,
                        'current_tier': license_info.get('tier'),
                        'upgrade_url': '/license/upgrade/'
                    }
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

def require_license_tier(min_tier):
    """Decorator to require a minimum license tier"""
    tier_hierarchy = {'free': 0, 'basic': 1, 'professional': 2, 'enterprise': 3}
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            license_info = get_license_info_from_request(request)
            
            if not license_info:
                return JsonResponse({
                    'success': False,
                    'error': 'License information not found',
                    'error_code': 'LICENSE_MISSING'
                }, status=403)
            
            current_tier = license_info.get('tier', 'free')
            current_level = tier_hierarchy.get(current_tier, 0)
            required_level = tier_hierarchy.get(min_tier, 0)
            
            if current_level < required_level:
                return JsonResponse({
                    'success': False,
                    'error': f'This endpoint requires {min_tier} tier or higher',
                    'error_code': 'INSUFFICIENT_LICENSE_TIER',
                    'details': {
                        'current_tier': current_tier,
                        'required_tier': min_tier,
                        'upgrade_url': '/license/upgrade/'
                    }
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

def track_api_usage(endpoint_name=None):
    """Decorator to track API usage for license monitoring"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            license_info = get_license_info_from_request(request)
            
            if license_info:
                tenant_id = license_info.get('tenant_id')
                endpoint = endpoint_name or f"{request.method} {request.path}"
                
                # Track usage
                track_endpoint_usage(tenant_id, endpoint)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

# Usage examples:
@api_view(['GET'])
@require_license_feature('advanced_reporting')
@track_api_usage('sales_advanced_analytics')
def sales_advanced_analytics(request):
    """Advanced sales analytics - requires professional+ license"""
    # This endpoint is only accessible with advanced_reporting feature
    return Response({'data': 'advanced analytics data'})

@api_view(['POST'])
@require_license_tier('professional')
@track_api_usage('bulk_operations')
def bulk_operations(request):
    """Bulk operations - requires professional+ license"""
    # This endpoint requires at least professional tier
    return Response({'success': True})
```

## 🎨 License Portal Integration

### **Public License Portal**

```python
# views/license_portal.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def license_portal_home(request):
    """Public license portal homepage"""
    # Get available license tiers from database
    tiers = LicenseTier.objects.filter(active=True).order_by('sequence')
    
    tier_data = []
    for tier in tiers:
        tier_data.append({
            'id': tier.id,
            'code': tier.code,
            'name': tier.name,
            'description': tier.description,
            'price_monthly': float(tier.price_monthly),
            'price_yearly': float(tier.price_yearly),
            'features': tier.get_feature_config(),
            'max_users': tier.max_users,
            'color': tier.color,
            'icon': tier.icon,
            'is_popular': tier.code == 'professional'  # Mark professional as popular
        })
    
    return render(request, 'license_portal/home.html', {
        'tiers': tier_data,
        'api_base_url': settings.API_BASE_URL
    })

@csrf_exempt
@require_http_methods(["POST"])
def license_portal_activate(request):
    """Handle license activation from portal"""
    try:
        data = json.loads(request.body)
        license_key = data.get('license_key', '').strip()
        client_name = data.get('client_name', '').strip()
        client_email = data.get('client_email', '').strip()
        domain = data.get('domain', '').strip()
        
        if not all([license_key, client_name, client_email]):
            return JsonResponse({
                'success': False,
                'error': 'All fields are required',
                'missing_fields': [
                    field for field, value in {
                        'license_key': license_key,
                        'client_name': client_name,
                        'client_email': client_email
                    }.items() if not value
                ]
            }, status=400)
        
        # Create activation wizard
        env = Environment(cr, SUPERUSER_ID, {})
        wizard = env['license.activation.wizard'].create({
            'license_key': license_key,
            'client_name': client_name,
            'contact_email': client_email,
            'domain': domain or request.get_host(),
        })
        
        # Validate and activate
        wizard.action_validate_key()
        if not wizard.is_valid:
            return JsonResponse({
                'success': False,
                'error': 'License validation failed',
                'details': wizard.validation_status
            }, status=400)
        
        wizard.action_activate_license()
        
        return JsonResponse({
            'success': True,
            'message': 'License activated successfully!',
            'data': {
                'license_key': license_key,
                'tier': wizard.license_key.tier_id.name,
                'expiry_date': wizard.license_key.expiry_date.isoformat() if wizard.license_key.expiry_date else None,
                'client_name': client_name,
                'features': wizard.license_key.tier_id.get_feature_config()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"License portal activation failed: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Activation failed',
            'details': str(e)
        }, status=500)

def license_portal_check(request):
    """Check license status from portal"""
    if request.method == 'GET':
        return render(request, 'license_portal/check.html')
    
    elif request.method == 'POST':
        license_key = request.POST.get('license_key', '').strip()
        
        if not license_key:
            return render(request, 'license_portal/check.html', {
                'error': 'License key is required'
            })
        
        try:
            # Find license in database
            env = Environment(cr, SUPERUSER_ID, {})
            license_record = env['license.key'].search([
                ('license_key', '=', license_key)
            ], limit=1)
            
            if not license_record:
                return render(request, 'license_portal/check.html', {
                    'error': 'License key not found'
                })
            
            # Validate license
            validator = LicenseValidator(env)
            # Set context for this specific license
            env.context = dict(env.context, current_license_id=license_record.id)
            result = validator.validate_license()
            
            return render(request, 'license_portal/check_result.html', {
                'license': license_record,
                'validation_result': result,
                'is_valid': result['success']
            })
            
        except Exception as e:
            logger.error(f"License check failed: {e}")
            return render(request, 'license_portal/check.html', {
                'error': f'Check failed: {str(e)}'
            })
```

## 🔧 Testing and Quality Assurance

### **License Integration Tests**

```python
# tests/test_license_integration.py
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta

class LicenseIntegrationTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com'
        )
        
        # Mock license data
        self.license_data = {
            'key': 'TEST-XXXX-XXXX-XXXX-XXXX',
            'tier': 'professional',
            'tier_name': 'Professional',
            'expiry_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'features': {
                'api_access': True,
                'sales_module': True,
                'hr_module': True,
                'inventory_module': True,
                'manufacturing_module': False,
                'advanced_reporting': True,
                'webhook_support': True,
                'real_time_sync': True
            },
            'limits': {
                'max_users': 50,
                'max_api_requests_per_hour': 5000,
                'max_concurrent_connections': 10
            },
            'status': 'active'
        }
    
    def create_jwt_token(self, license_data=None):
        """Create JWT token with license information"""
        payload = {
            'user_id': self.user.id,
            'username': self.user.username,
            'tenant_id': 'test_tenant',
            'license': license_data or self.license_data,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, 'test-secret', algorithm='HS256')
    
    @patch('middleware.license_middleware.LicenseValidator')
    def test_api_access_with_valid_license(self, mock_validator):
        """Test API access with valid license"""
        # Mock license validation
        mock_validator.return_value.validate_license.return_value = {
            'success': True,
            'data': self.license_data
        }
        
        token = self.create_jwt_token()
        response = self.client.get('/api/sales/orders/', 
                                 HTTP_AUTHORIZATION=f'Bearer {token}')
        
        self.assertEqual(response.status_code, 200)
    
    def test_api_access_without_license(self):
        """Test API access without license information"""
        # Create token without license data
        payload = {
            'user_id': self.user.id,
            'username': self.user.username,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, 'test-secret', algorithm='HS256')
        
        response = self.client.get('/api/sales/orders/', 
                                 HTTP_AUTHORIZATION=f'Bearer {token}')
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('LICENSE_MISSING', response.json()['error_code'])
    
    @patch('middleware.license_middleware.LicenseValidator')
    def test_feature_not_licensed(self, mock_validator):
        """Test access to feature not included in license"""
        # Create license without manufacturing module
        limited_license = self.license_data.copy()
        limited_license['features']['manufacturing_module'] = False
        
        mock_validator.return_value.validate_license.return_value = {
            'success': True,
            'data': limited_license
        }
        
        token = self.create_jwt_token(limited_license)
        response = self.client.get('/api/manufacturing/orders/', 
                                 HTTP_AUTHORIZATION=f'Bearer {token}')
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('FEATURE_NOT_LICENSED', response.json()['error_code'])
    
    @patch('middleware.license_middleware.LicenseValidator')
    def test_usage_limit_exceeded(self, mock_validator):
        """Test API usage limit enforcement"""
        # Mock current usage to exceed limit
        with patch('middleware.license_middleware.LicenseValidationMiddleware._get_current_usage') as mock_usage:
            mock_usage.return_value = 5001  # Exceeds limit of 5000
            
            mock_validator.return_value.validate_license.return_value = {
                'success': True,
                'data': self.license_data
            }
            
            token = self.create_jwt_token()
            response = self.client.get('/api/sales/orders/', 
                                     HTTP_AUTHORIZATION=f'Bearer {token}')
            
            self.assertEqual(response.status_code, 429)
            self.assertIn('USAGE_LIMIT_EXCEEDED', response.json()['error_code'])
    
    def test_license_activation_endpoint(self):
        """Test license activation via API"""
        activation_data = {
            'license_key': 'TEST-XXXX-XXXX-XXXX-XXXX',
            'client_name': 'Test Client',
            'contact_email': 'client@test.com'
        }
        
        with patch('views.license_views.LicenseActivationWizard') as mock_wizard:
            mock_wizard_instance = MagicMock()
            mock_wizard_instance.is_valid = True
            mock_wizard_instance.license_key.tier_id.name = 'Professional'
            mock_wizard_instance.license_key.expiry_date = datetime.now() + timedelta(days=365)
            
            mock_wizard.create.return_value = mock_wizard_instance
            
            # Create authenticated request
            token = self.create_jwt_token()
            response = self.client.post('/api/license/activate/',
                                      data=activation_data,
                                      content_type='application/json',
                                      HTTP_AUTHORIZATION=f'Bearer {token}')
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()['success'])
    
    def test_websocket_license_validation(self):
        """Test WebSocket connection with license validation"""
        from channels.testing import WebsocketCommunicator
        from websocket.license_consumer import LicenseAwareWebsocketConsumer
        
        # Create token with real-time sync feature
        token = self.create_jwt_token()
        
        communicator = WebsocketCommunicator(
            LicenseAwareWebsocketConsumer.as_asgi(),
            f"/ws/?token={token}&tenant_id=test_tenant"
        )
        
        connected, subprotocol = communicator.connect()
        self.assertTrue(connected)
        
        communicator.disconnect()
    
    def test_websocket_license_feature_denied(self):
        """Test WebSocket connection denied for missing feature"""
        # Create license without real-time sync
        limited_license = self.license_data.copy()
        limited_license['features']['real_time_sync'] = False
        
        token = self.create_jwt_token(limited_license)
        
        communicator = WebsocketCommunicator(
            LicenseAwareWebsocketConsumer.as_asgi(),
            f"/ws/?token={token}&tenant_id=test_tenant"
        )
        
        connected, subprotocol = communicator.connect()
        self.assertFalse(connected)  # Should be denied

class LicensePortalTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def test_license_portal_home(self):
        """Test license portal homepage"""
        response = self.client.get('/license/portal/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Professional')  # Should show tiers
    
    def test_license_activation_via_portal(self):
        """Test license activation through portal"""
        activation_data = {
            'license_key': 'TEST-XXXX-XXXX-XXXX-XXXX',
            'client_name': 'Test Client',
            'client_email': 'client@test.com',
            'domain': 'test.com'
        }
        
        with patch('views.license_portal.Environment') as mock_env:
            mock_wizard = MagicMock()
            mock_wizard.is_valid = True
            mock_wizard.license_key.tier_id.name = 'Professional'
            
            mock_env.return_value.__getitem__.return_value.create.return_value = mock_wizard
            
            response = self.client.post('/license/portal/activate/',
                                      data=activation_data,
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()['success'])

# Performance tests
class LicensePerformanceTestCase(TestCase):
    
    def test_license_validation_performance(self):
        """Test license validation performance under load"""
        import time
        
        token = self.create_jwt_token()
        
        # Measure time for 100 license validations
        start_time = time.time()
        
        for _ in range(100):
            response = self.client.get('/api/sales/orders/',
                                     HTTP_AUTHORIZATION=f'Bearer {token}')
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 100 validations in under 1 second
        self.assertLess(total_time, 1.0)
        print(f"100 license validations completed in {total_time:.3f} seconds")

# Run tests
if __name__ == '__main__':
    pytest.main([__file__])
```

## 🚀 Deployment and Configuration

### **Docker Integration**

```dockerfile
# Dockerfile.license-integrated-api
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY requirements-license.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-license.txt

# Copy application code
COPY . .

# Copy license module
COPY fayvad_license/ ./fayvad_license/

# Set environment variables
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]
```

```yaml
# docker-compose.license-integrated.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.license-integrated-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://fayvad:password@postgres:5432/fayvad_api
      - REDIS_URL=redis://redis:6379/0
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - LICENSE_VALIDATION_URL=https://license.digital.fayvad.com/api/validate
      - LICENSE_RSA_PUBLIC_KEY=${LICENSE_RSA_PUBLIC_KEY}
      - LICENSE_RSA_PRIVATE_KEY=${LICENSE_RSA_PRIVATE_KEY}
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=fayvad_api
      - POSTGRES_USER=fayvad
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init-license-tables.sql:/docker-entrypoint-initdb.d/init-license-tables.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fayvad"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  license-portal:
    build:
      context: .
      dockerfile: Dockerfile.license-portal
    ports:
      - "3000:3000"
    environment:
      - NUXT_API_BASE_URL=http://api:8000
      - NUXT_LICENSE_PORTAL_URL=http://localhost:3000
    depends_on:
      - api

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
      - license-portal

volumes:
  postgres_data:
  redis_data:
```

### **Environment Configuration**

```python
# config/settings/license.py
"""License-specific settings"""

import os
from cryptography.hazmat.primitives import serialization

# License Management Settings
LICENSE_VALIDATION_ENABLED = os.getenv('LICENSE_VALIDATION_ENABLED', 'true').lower() == 'true'
LICENSE_VALIDATION_URL = os.getenv('LICENSE_VALIDATION_URL', 'https://license.digital.fayvad.com/api/validate')
LICENSE_GRACE_PERIOD_HOURS = int(os.getenv('LICENSE_GRACE_PERIOD_HOURS', '48'))

# Cryptographic Keys for License Validation
LICENSE_RSA_PUBLIC_KEY = os.getenv('LICENSE_RSA_PUBLIC_KEY')
LICENSE_RSA_PRIVATE_KEY = os.getenv('LICENSE_RSA_PRIVATE_KEY')

if LICENSE_RSA_PUBLIC_KEY:
    try:
        LICENSE_PUBLIC_KEY_OBJ = serialization.load_pem_public_key(
            LICENSE_RSA_PUBLIC_KEY.encode(),
            backend=default_backend()
        )
    except Exception as e:
        raise ValueError(f"Invalid LICENSE_RSA_PUBLIC_KEY: {e}")
else:
    LICENSE_PUBLIC_KEY_OBJ = None

# License Tiers Configuration
LICENSE_TIERS = {
    'free': {
        'name': 'Free',
        'max_users': 1,
        'max_api_requests_per_hour': 100,
        'max_concurrent_connections': 1,
        'features': {
            'api_access': True,
            'sales_module': True,
            'hr_module': False,
            'inventory_module': False,
            'manufacturing_module': False,
            'purchasing_module': False,
            'accounting_module': False,
            'advanced_reporting': False,
            'webhook_support': False,
            'real_time_sync': False,
        }
    },
    'basic': {
        'name': 'Basic',
        'max_users': 5,
        'max_api_requests_per_hour': 1000,
        'max_concurrent_connections': 3,
        'features': {
            'api_access': True,
            'sales_module': True,
            'hr_module': True,
            'inventory_module': True,
            'manufacturing_module': False,
            'purchasing_module': True,
            'accounting_module': True,
            'advanced_reporting': False,
            'webhook_support': False,
            'real_time_sync': True,
        }
    },
    'professional': {
        'name': 'Professional',
        'max_users': 50,
        'max_api_requests_per_hour': 5000,
        'max_concurrent_connections': 10,
        'features': {
            'api_access': True,
            'sales_module': True,
            'hr_module': True,
            'inventory_module': True,
            'manufacturing_module': True,
            'purchasing_module': True,
            'accounting_module': True,
            'advanced_reporting': True,
            'webhook_support': True,
            'real_time_sync': True,
        }
    },
    'enterprise': {
        'name': 'Enterprise',
        'max_users': 0,  # Unlimited
        'max_api_requests_per_hour': 0,  # Unlimited
        'max_concurrent_connections': 0,  # Unlimited
        'features': {
            'api_access': True,
            'sales_module': True,
            'hr_module': True,
            'inventory_module': True,
            'manufacturing_module': True,
            'purchasing_module': True,
            'accounting_module': True,
            'advanced_reporting': True,
            'webhook_support': True,
            'real_time_sync': True,
        }
    }
}

# License Usage Tracking
LICENSE_USAGE_TRACKING = {
    'enabled': True,
    'storage_backend': 'redis',  # redis, database, memory
    'retention_days': 90,
    'aggregation_intervals': ['hour', 'day', 'week', 'month']
}

# Error Handling
LICENSE_ERROR_RESPONSES = {
    'LICENSE_MISSING': {
        'message': 'License information not found',
        'suggestion': 'Please ensure you have a valid license activated',
        'action_url': '/license/activate/'
    },
    'LICENSE_INVALID': {
        'message': 'License validation failed',
        'suggestion': 'Your license may be expired or invalid',
        'action_url': '/license/renew/'
    },
    'FEATURE_NOT_LICENSED': {
        'message': 'Feature not available in current license tier',
        'suggestion': 'Upgrade your license to access this feature',
        'action_url': '/license/upgrade/'
    },
    'USAGE_LIMIT_EXCEEDED': {
        'message': 'License usage limit exceeded',
        'suggestion': 'Upgrade your license for higher limits',
        'action_url': '/license/upgrade/'
    }
}
```

### **Nginx Configuration**

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream license_portal {
        server license-portal:3000;
    }

    # Rate limiting for license endpoints
    limit_req_zone $binary_remote_addr zone=license_activate:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=license_check:10m rate=10r/m;

    server {
        listen 80;
        server_name api.fayvad.com;

        # API endpoints
        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeout settings for license validation
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # WebSocket endpoints
        location /ws/ {
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health/ {
            proxy_pass http://api;
            access_log off;
        }

        # License portal
        location /license/ {
            limit_req zone=license_activate burst=10 nodelay;
            proxy_pass http://license_portal/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## 📊 Monitoring and Analytics Dashboard

### **License Management Dashboard**

```python
# views/license_dashboard.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
import json

@staff_member_required
def license_dashboard(request):
    """Administrative dashboard for license management"""
    return render(request, 'admin/license_dashboard.html')

@staff_member_required
def license_dashboard_data(request):
    """API endpoint for dashboard data"""
    
    # Get overall statistics
    total_licenses = env['license.key'].search_count([])
    active_licenses = env['license.key'].search_count([('state', '=', 'active')])
    expired_licenses = env['license.key'].search_count([('state', '=', 'expired')])
    
    # License distribution by tier
    tier_distribution = {}
    for tier in env['license.tier'].search([]):
        count = env['license.key'].search_count([('tier_id', '=', tier.id)])
        tier_distribution[tier.code] = {
            'name': tier.name,
            'count': count,
            'revenue': count * tier.price_monthly
        }
    
    # Recent activations
    recent_activations = env['license.validation'].search([
        ('event_type', '=', 'activation'),
        ('status', '=', 'success')
    ], limit=10, order='create_date desc')
    
    # Usage analytics
    usage_stats = get_usage_analytics_summary()
    
    # Alerts and warnings
    alerts = []
    
    # Check for licenses expiring soon
    expiring_soon = env['license.key'].search([
        ('state', '=', 'active'),
        ('is_perpetual', '=', False),
        ('expiry_date', '<=', fields.Datetime.now() + timedelta(days=30)),
        ('expiry_date', '>', fields.Datetime.now())
    ])
    
    if expiring_soon:
        alerts.append({
            'type': 'warning',
            'title': 'Licenses Expiring Soon',
            'message': f'{len(expiring_soon)} licenses will expire within 30 days',
            'count': len(expiring_soon)
        })
    
    # Check for high usage clients
    high_usage_clients = get_high_usage_clients()
    if high_usage_clients:
        alerts.append({
            'type': 'info',
            'title': 'High Usage Clients',
            'message': f'{len(high_usage_clients)} clients are using >80% of their limits',
            'count': len(high_usage_clients)
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'overview': {
                'total_licenses': total_licenses,
                'active_licenses': active_licenses,
                'expired_licenses': expired_licenses,
                'activation_rate': (active_licenses / total_licenses * 100) if total_licenses > 0 else 0
            },
            'tier_distribution': tier_distribution,
            'recent_activations': [
                {
                    'license_key': activation.license_key_id.key_display,
                    'client': activation.license_key_id.client_id.client_name,
                    'tier': activation.license_key_id.tier_id.name,
                    'date': activation.create_date.isoformat()
                }
                for activation in recent_activations
            ],
            'usage_stats': usage_stats,
            'alerts': alerts
        }
    })

def get_usage_analytics_summary():
    """Get summary of usage analytics across all tenants"""
    from django.core.cache import cache
    
    total_api_calls_today = 0
    total_active_users = 0
    total_concurrent_connections = 0
    
    # Get all active tenants
    active_clients = env['license.client'].search([('active', '=', True)])
    
    for client in active_clients:
        # API calls today
        api_key = f"api_usage_daily:{client.client_uuid}:{datetime.now().strftime('%Y%m%d')}"
        total_api_calls_today += cache.get(api_key, 0)
        
        # Active users
        users_key = f"active_users:{client.client_uuid}"
        total_active_users += cache.get(users_key, 0)
        
        # Concurrent connections
        ws_key = f"ws_connections:{client.client_uuid}"
        total_concurrent_connections += cache.get(ws_key, 0)
    
    return {
        'api_calls_today': total_api_calls_today,
        'active_users': total_active_users,
        'concurrent_connections': total_concurrent_connections,
        'total_tenants': len(active_clients)
    }

def get_high_usage_clients():
    """Identify clients with high usage compared to their limits"""
    high_usage = []
    
    active_licenses = env['license.key'].search([
        ('state', '=', 'active'),
        ('client_id', '!=', False)
    ])
    
    for license_key in active_licenses:
        client_id = license_key.client_id.client_uuid
        limits = license_key.tier_id.get_feature_config()
        
        # Check API usage
        api_limit = limits.get('max_api_requests_per_hour', 0)
        if api_limit > 0:
            current_usage = cache.get(f"api_usage:{client_id}:{datetime.now().strftime('%Y%m%d%H')}", 0)
            usage_percentage = (current_usage / api_limit) * 100
            
            if usage_percentage > 80:
                high_usage.append({
                    'client': license_key.client_id.client_name,
                    'license_key': license_key.key_display,
                    'usage_type': 'API Requests',
                    'usage_percentage': usage_percentage,
                    'current': current_usage,
                    'limit': api_limit
                })
    
    return high_usage
```

## 🎯 Migration Strategy

### **Step-by-Step Integration Plan**

```python
# management/commands/integrate_license_system.py
from django.core.management.base import BaseCommand
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Integrate license system with existing Generic Odoo API'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without making changes')
        parser.add_argument('--skip-validation', action='store_true', help='Skip license validation during migration')
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.skip_validation = options['skip_validation']
        
        self.stdout.write(self.style.SUCCESS('Starting license system integration...'))
        
        try:
            with transaction.atomic():
                # Step 1: Install license module in all Odoo databases
                self.install_license_module()
                
                # Step 2: Create default license tiers
                self.create_default_license_tiers()
                
                # Step 3: Migrate existing tenants to free licenses
                self.migrate_existing_tenants()
                
                # Step 4: Update middleware configuration
                self.update_middleware_config()
                
                # Step 5: Initialize license validation
                if not self.skip_validation:
                    self.initialize_license_validation()
                
                # Step 6: Create admin interface
                self.setup_admin_interface()
                
                if self.dry_run:
                    self.stdout.write(self.style.WARNING('DRY RUN: Rolling back all changes'))
                    transaction.set_rollback(True)
                else:
                    self.stdout.write(self.style.SUCCESS('License system integration completed successfully!'))
                    
        except Exception as e:
            logger.error(f"License integration failed: {e}")
            self.stdout.write(self.style.ERROR(f'Integration failed: {e}'))
            raise
    
    def install_license_module(self):
        """Install license module in all Odoo databases"""
        self.stdout.write('Installing license module in Odoo databases...')
        
        # Get all registered databases
        databases = get_registered_databases()
        
        for db_name in databases:
            try:
                with odoo_environment(db_name) as env:
                    # Install fayvad_license module
                    module = env['ir.module.module'].search([('name', '=', 'fayvad_license')])
                    if module and module.state != 'installed':
                        module.button_immediate_install()
                        self.stdout.write(f'  ✓ Installed in {db_name}')
                    else:
                        self.stdout.write(f'  - Already installed in {db_name}')
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Failed to install in {db_name}: {e}'))
    
    def create_default_license_tiers(self):
        """Create default license tiers"""
        self.stdout.write('Creating default license tiers...')
        
        from config.settings.license import LICENSE_TIERS
        
        # Use first available database for tier creation
        with odoo_environment(get_registered_databases()[0]) as env:
            for tier_code, tier_config in LICENSE_TIERS.items():
                existing = env['license.tier'].search([('code', '=', tier_code)])
                
                if not existing:
                    tier_data = {
                        'name': tier_config['name'],
                        'code': tier_code,
                        'max_users': tier_config['max_users'],
                        'max_companies': 1,
                        'max_databases': 1,
                        'feature_config': json.dumps(tier_config['features']),
                        'allows_api_access': True,
                        'allows_custom_modules': tier_code in ['professional', 'enterprise'],
                        'active': True,
                    }
                    
                    # Set pricing for paid tiers
                    if tier_code == 'basic':
                        tier_data.update({'price_monthly': 29.00, 'price_yearly': 290.00})
                    elif tier_code == 'professional':
                        tier_data.update({'price_monthly': 99.00, 'price_yearly': 990.00})
                    elif tier_code == 'enterprise':
                        tier_data.update({'price_monthly': 199.00, 'price_yearly': 1990.00})
                    
                    env['license.tier'].create(tier_data)
                    self.stdout.write(f'  ✓ Created {tier_config["name"]} tier')
                else:
                    self.stdout.write(f'  - {tier_config["name"]} tier already exists')
    
    def migrate_existing_tenants(self):
        """Migrate existing tenants to free licenses"""
        self.stdout.write('Migrating existing tenants to free licenses...')
        
        databases = get_registered_databases()
        
        for db_name in databases:
            try:
                with odoo_environment(db_name) as env:
                    # Get free tier
                    free_tier = env['license.tier'].search([('code', '=', 'free')], limit=1)
                    if not free_tier:
                        continue
                    
                    # Check if client already exists
                    existing_client = env['license.client'].search([], limit=1)
                    if existing_client:
                        continue
                    
                    # Create client for this database
                    client = env['license.client'].create({
                        'client_name': f'Migrated Client - {db_name}',
                        'hostname': f'{db_name}.local',
                        'domain': f'{db_name}.local',
                    })
                    
                    # Create free license
                    license_key = env['license.key'].create({
                        'tier_id': free_tier.id,
                        'client_id': client.id,
                        'is_perpetual': True,
                        'notes': 'Auto-generated during migration to license system',
                    })
                    
                    # Activate the license
                    license_key.activate()
                    
                    self.stdout.write(f'  ✓ Migrated {db_name} to free license')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Failed to migrate {db_name}: {e}'))
    
    def update_middleware_config(self):
        """Update Django middleware configuration"""
        self.stdout.write('Updating middleware configuration...')
        
        # This would typically update settings or configuration files
        # In practice, this might require manual configuration changes
        
        self.stdout.write('  ⚠ Manual step required: Add LicenseValidationMiddleware to MIDDLEWARE setting')
        self.stdout.write('    Add: "middleware.license_middleware.LicenseValidationMiddleware"')
    
    def initialize_license_validation(self):
        """Initialize license validation for all tenants"""
        self.stdout.write('Initializing license validation...')
        
        databases = get_registered_databases()
        failed_validations = []
        
        for db_name in databases:
            try:
                with odoo_environment(db_name) as env:
                    validator = LicenseValidator(env)
                    result = validator.validate_license()
                    
                    if result['success']:
                        self.stdout.write(f'  ✓ Validation successful for {db_name}')
                    else:
                        failed_validations.append(db_name)
                        self.stdout.write(f'  ⚠ Validation warning for {db_name}: {result["message"]}')
                        
            except Exception as e:
                failed_validations.append(db_name)
                self.stdout.write(self.style.ERROR(f'  ✗ Validation failed for {db_name}: {e}'))
        
        if failed_validations:
            self.stdout.write(f'License validation issues in {len(failed_validations)} databases')
    
    def setup_admin_interface(self):
        """Setup admin interface for license management"""
        self.stdout.write('Setting up admin interface...')
        
        # Create admin URLs and views
        admin_config = {
            'license_dashboard_url': '/admin/license/dashboard/',
            'license_analytics_url': '/admin/license/analytics/',
            'license_management_url': '/admin/license/management/',
        }
        
        self.stdout.write('  ✓ Admin interface configuration ready')
        self.stdout.write(f'  Dashboard will be available at: {admin_config["license_dashboard_url"]}')
```

## 📋 Final Integration Checklist

### **Pre-Integration Checklist**

- [ ] **Database Setup**
  - [ ] License tables created in all Odoo databases
  - [ ] RSA key pairs generated and stored securely
  - [ ] Default license tiers configured
  - [ ] Migration scripts prepared

- [ ] **API Configuration**
  - [ ] License middleware configured in Django settings
  - [ ] JWT token structure updated to include license data
  - [ ] License validation endpoints implemented
  - [ ] Error handling for license-specific errors

- [ ] **WebSocket Integration**
  - [ ] License validation in WebSocket consumer
  - [ ] Connection limits enforcement
  - [ ] Real-time license event handling
  - [ ] Graceful degradation for license issues

- [ ] **Frontend Integration**
  - [ ] Vue.js composables for license management
  - [ ] License dashboard components
  - [ ] Feature gating implementation
  - [ ] Error handling and user feedback

- [ ] **Security & Performance**
  - [ ] License validation performance optimized
  - [ ] Caching strategy implemented
  - [ ] Rate limiting configured
  - [ ] Security audit completed

### **Post-Integration Checklist**

- [ ] **Testing**
  - [ ] Unit tests for license validation
  - [ ] Integration tests for API endpoints
  - [ ] Performance tests under load
  - [ ] End-to-end testing of license flows

- [ ] **Monitoring**
  - [ ] License usage analytics implemented
  - [ ] Alerting for license issues configured
  - [ ] Performance monitoring enabled
  - [ ] Error tracking and logging

- [ ] **Documentation**
  - [ ] API documentation updated with license info
  - [ ] User guides for license management
  - [ ] Admin documentation for license system
  - [ ] Troubleshooting guides prepared

- [ ] **Deployment**
  - [ ] Production deployment tested
  - [ ] Rollback procedures documented
  - [ ] Monitoring and alerting verified
  - [ ] Support team trained on license system

## 🎯 Summary

This integration creates a **unified, enterprise-grade system** that combines:

1. **Seamless License Validation**: Every API request validates license automatically
2. **Feature-Based Access Control**: Dynamic feature gating based on license tier
3. **Real-time Usage Monitoring**: Live tracking of API usage and limits
4. **Multi-tenant License Management**: Isolated license validation per tenant
5. **WebSocket License Enforcement**: Real-time connection limits and feature control
6. **Comprehensive Analytics**: Usage analytics and optimization recommendations
7. **Self-service Portal**: Public portal for license activation and management
8. **Admin Dashboard**: Complete license management interface for administrators

The result is a **production-ready, scalable licensing system** that enhances the Generic Odoo API with powerful monetization and access control capabilities while maintaining the excellent developer experience and architectural principles of the original system.