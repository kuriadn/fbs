# 07. Error Handling API ⚠️

## Overview

The FBS API uses standard HTTP status codes and provides detailed error responses to help developers understand and resolve issues. All error responses follow a consistent format and include helpful information for debugging and troubleshooting.

## 🔐 Authentication

All error handling endpoints require JWT authentication:

```http
Authorization: Bearer <your_jwt_token>
```

## 📋 Error Response Format

All error responses follow this standard format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error details",
      "suggestion": "Helpful suggestion for resolution"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/ERROR_CODE"
  }
}
```

## 🚨 HTTP Status Codes

### **2xx Success Codes**

| Code | Name | Description |
|------|------|-------------|
| `200` | OK | Request successful |
| `201` | Created | Resource created successfully |
| `202` | Accepted | Request accepted for processing |
| `204` | No Content | Request successful, no content to return |

### **4xx Client Error Codes**

| Code | Name | Description |
|------|------|-------------|
| `400` | Bad Request | Invalid request syntax or parameters |
| `401` | Unauthorized | Authentication required or failed |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource not found |
| `405` | Method Not Allowed | HTTP method not supported |
| `409` | Conflict | Resource conflict (e.g., duplicate) |
| `422` | Unprocessable Entity | Valid request but business logic failed |
| `429` | Too Many Requests | Rate limit exceeded |

### **5xx Server Error Codes**

| Code | Name | Description |
|------|------|-------------|
| `500` | Internal Server Error | Unexpected server error |
| `502` | Bad Gateway | Upstream service error |
| `503` | Service Unavailable | Service temporarily unavailable |
| `504` | Gateway Timeout | Request timeout |

## 🔍 Error Code Reference

### **Authentication Errors (AUTH_*)**

#### **AUTH_001 - Invalid Credentials**

**Status Code:** `401`

**Description:** Invalid username or password provided.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "AUTH_001",
    "message": "Invalid username or password",
    "details": {
      "attempts_remaining": 4,
      "lockout_time": "2024-01-15T11:30:00Z"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/AUTH_001"
  }
}
```

#### **AUTH_002 - Token Expired**

**Status Code:** `401`

**Description:** JWT token has expired.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "AUTH_002",
    "message": "Access token has expired",
    "details": {
      "expired_at": "2024-01-15T10:25:00Z",
      "suggestion": "Use refresh token to get new access token"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/AUTH_002"
  }
}
```

#### **AUTH_003 - Insufficient Permissions**

**Status Code:** `403`

**Description:** User lacks required permissions for the requested operation.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "AUTH_003",
    "message": "Insufficient permissions for this operation",
    "details": {
      "required_permissions": ["fbs.manage_database"],
      "user_permissions": ["fbs.view_database"],
      "suggestion": "Contact administrator to request additional permissions"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/AUTH_003"
  }
}
```

### **Validation Errors (VAL_*)**

#### **VAL_001 - Required Field Missing**

**Status Code:** `400`

**Description:** Required field is missing from request.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "VAL_001",
    "message": "Required field 'name' is missing",
    "details": {
      "field": "name",
      "type": "string",
      "suggestion": "Include the 'name' field in your request"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/VAL_001"
  }
}
```

#### **VAL_002 - Invalid Field Type**

**Status Code:** `400`

**Description:** Field value has incorrect data type.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "VAL_002",
    "message": "Field 'age' must be a number",
    "details": {
      "field": "age",
      "expected_type": "integer",
      "received_value": "twenty-five",
      "suggestion": "Provide age as a number (e.g., 25)"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/VAL_002"
  }
}
```

#### **VAL_003 - Field Value Out of Range**

**Status Code:** `400`

**Description:** Field value is outside acceptable range.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "VAL_003",
    "message": "Field 'price' must be between 0 and 10000",
    "details": {
      "field": "price",
      "min_value": 0,
      "max_value": 10000,
      "received_value": 15000,
      "suggestion": "Provide a price between 0 and 10000"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/VAL_003"
  }
}
```

#### **VAL_004 - Invalid Email Format**

**Status Code:** `400`

**Description:** Email address format is invalid.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "VAL_004",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "received_value": "invalid-email",
      "suggestion": "Provide a valid email address (e.g., user@example.com)"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/VAL_004"
  }
}
```

### **Resource Errors (RES_*)**

#### **RES_001 - Resource Not Found**

**Status Code:** `404`

**Description:** Requested resource does not exist.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "RES_001",
    "message": "Database 'test_db' not found",
    "details": {
      "resource_type": "database",
      "resource_id": "test_db",
      "suggestion": "Check the database name or create the database first"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/RES_001"
  }
}
```

#### **RES_002 - Resource Already Exists**

**Status Code:** `409`

**Description:** Resource already exists and cannot be created.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "RES_002",
    "message": "Database 'test_db' already exists",
    "details": {
      "resource_type": "database",
      "resource_id": "test_db",
      "existing_id": 123,
      "suggestion": "Use a different name or update the existing resource"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/RES_002"
  }
}
```

#### **RES_003 - Resource In Use**

**Status Code:** `409`

**Description:** Resource is currently in use and cannot be modified.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "RES_003",
    "message": "Database 'test_db' is currently in use",
    "details": {
      "resource_type": "database",
      "resource_id": "test_db",
      "active_connections": 5,
      "suggestion": "Wait for active operations to complete or force disconnect"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/RES_003"
  }
}
```

### **Business Logic Errors (BUS_*)**

#### **BUS_001 - Invalid State Transition**

**Status Code:** `422`

**Description:** Invalid workflow state transition.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "BUS_001",
    "message": "Cannot transition from 'draft' to 'completed'",
    "details": {
      "current_state": "draft",
      "requested_state": "completed",
      "allowed_transitions": ["submitted", "cancelled"],
      "suggestion": "Transition to 'submitted' first, then to 'completed'"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/BUS_001"
  }
}
```

#### **BUS_002 - Insufficient Balance**

**Status Code:** `422`

**Description:** Insufficient balance for operation.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "BUS_002",
    "message": "Insufficient balance for this operation",
    "details": {
      "required_amount": 1000,
      "available_balance": 500,
      "shortfall": 500,
      "suggestion": "Add funds to your account or reduce the amount"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/BUS_002"
  }
}
```

#### **BUS_003 - Business Rule Violation**

**Status Code:** `422`

**Description:** Operation violates business rules.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "BUS_003",
    "message": "Cannot delete database with active tenants",
    "details": {
      "rule": "no_active_tenants_on_delete",
      "active_tenants": 3,
      "suggestion": "Migrate or remove active tenants before deletion"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/BUS_003"
  }
}
```

### **System Errors (SYS_*)**

#### **SYS_001 - Database Connection Error**

**Status Code:** `503`

**Description:** Unable to connect to database.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "SYS_001",
    "message": "Database connection failed",
    "details": {
      "database": "test_db",
      "error": "Connection timeout",
      "retry_after": 30,
      "suggestion": "Retry the request after 30 seconds"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/SYS_001"
  }
}
```

#### **SYS_002 - External Service Error**

**Status Code:** `502`

**Description:** External service is unavailable.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "SYS_002",
    "message": "Odoo service is unavailable",
    "details": {
      "service": "odoo",
      "endpoint": "http://localhost:8069",
      "error": "Connection refused",
      "retry_after": 60,
      "suggestion": "Check Odoo service status and retry"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/SYS_002"
  }
}
```

#### **SYS_003 - Rate Limit Exceeded**

**Status Code:** `429`

**Description:** Rate limit exceeded for the API endpoint.

**Example Response:**

```json
{
  "success": false,
  "error": {
    "code": "SYS_003",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 1000,
      "used": 1000,
      "reset_time": "2024-01-15T11:00:00Z",
      "suggestion": "Wait until reset time or upgrade your plan"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "documentation_url": "https://docs.fbs.com/errors/SYS_003"
  }
}
```

## 🔧 Error Handling Best Practices

### **Client-Side Error Handling**

#### **JavaScript Example**

```javascript
async function makeApiRequest(url, options) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    if (!response.ok) {
      // Handle specific error codes
      switch (data.error.code) {
        case 'AUTH_001':
          // Handle invalid credentials
          console.error('Invalid credentials:', data.error.message);
          // Redirect to login
          window.location.href = '/login';
          break;
          
        case 'AUTH_002':
          // Handle expired token
          console.error('Token expired:', data.error.message);
          // Refresh token
          await refreshToken();
          // Retry original request
          return makeApiRequest(url, options);
          
        case 'VAL_001':
          // Handle validation errors
          console.error('Validation error:', data.error.details);
          // Show field-specific error messages
          showFieldError(data.error.details.field, data.error.message);
          break;
          
        case 'SYS_003':
          // Handle rate limiting
          console.error('Rate limited:', data.error.message);
          // Show user-friendly message
          showRateLimitMessage(data.error.details.reset_time);
          break;
          
        default:
          // Handle generic errors
          console.error('API Error:', data.error);
          showGenericError(data.error.message);
      }
      
      throw new Error(data.error.message);
    }
    
    return data;
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
}
```

#### **Python Example**

```python
import requests
from typing import Dict, Any

class FBSAPIError(Exception):
    def __init__(self, error_data: Dict[str, Any]):
        self.code = error_data.get('code')
        self.message = error_data.get('message')
        self.details = error_data.get('details', {})
        self.timestamp = error_data.get('timestamp')
        self.request_id = error_data.get('request_id')
        super().__init__(self.message)

def make_api_request(url: str, headers: Dict[str, str], data: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        
        if not response.ok:
            error_data = response_data.get('error', {})
            
            # Handle specific error codes
            if error_data.get('code') == 'AUTH_002':
                # Token expired, refresh and retry
                refresh_token()
                return make_api_request(url, headers, data)
            
            elif error_data.get('code') == 'VAL_001':
                # Validation error
                field = error_data.get('details', {}).get('field')
                raise ValidationError(f"Field '{field}' is required")
            
            elif error_data.get('code') == 'SYS_003':
                # Rate limited
                reset_time = error_data.get('details', {}).get('reset_time')
                raise RateLimitError(f"Rate limit exceeded. Reset at {reset_time}")
            
            else:
                # Generic error
                raise FBSAPIError(error_data)
        
        return response_data
    
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error: {str(e)}")
```

### **Retry Logic**

#### **Exponential Backoff**

```javascript
async function retryWithBackoff(fn, maxRetries = 3, baseDelay = 1000) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Check if error is retryable
      if (error.code && ['SYS_001', 'SYS_002', 'SYS_003'].includes(error.code)) {
        const delay = baseDelay * Math.pow(2, attempt - 1);
        console.log(`Retry attempt ${attempt} in ${delay}ms`);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
}
```

### **Error Logging**

#### **Structured Error Logging**

```javascript
function logError(error, context = {}) {
  const errorLog = {
    timestamp: new Date().toISOString(),
    error_code: error.code,
    error_message: error.message,
    request_id: error.request_id,
    user_id: context.userId,
    endpoint: context.endpoint,
    request_data: context.requestData,
    stack_trace: error.stack
  };
  
  // Send to error tracking service
  console.error('API Error:', errorLog);
  
  // Store locally for debugging
  localStorage.setItem('last_error', JSON.stringify(errorLog));
}
```

## 📊 Error Monitoring

### **Get Error Statistics**

Retrieve error statistics and trends.

```http
GET /api/errors/stats/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | No | - | Start date (ISO format) |
| `end_date` | string | No | - | End date (ISO format) |
| `error_code` | string | No | - | Filter by error code |
| `endpoint` | string | No | - | Filter by endpoint |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "summary": {
      "total_errors": 1250,
      "unique_errors": 15,
      "error_rate": 2.5,
      "most_common_error": "AUTH_002"
    },
    "errors_by_code": [
      {
        "code": "AUTH_002",
        "count": 450,
        "percentage": 36.0,
        "trend": "decreasing"
      },
      {
        "code": "VAL_001",
        "count": 300,
        "percentage": 24.0,
        "trend": "stable"
      }
    ],
    "errors_by_endpoint": [
      {
        "endpoint": "/api/auth/login",
        "count": 200,
        "error_rate": 5.2
      },
      {
        "endpoint": "/api/core/models",
        "count": 150,
        "error_rate": 1.8
      }
    ],
    "time_series": [
      {
        "date": "2024-01-15",
        "total_errors": 45,
        "unique_errors": 8
      }
    ]
  }
}
```

### **Get Error Details**

Get detailed information about a specific error.

```http
GET /api/errors/{request_id}/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "error": {
      "request_id": "req_123456789",
      "code": "AUTH_002",
      "message": "Access token has expired",
      "timestamp": "2024-01-15T10:30:00Z",
      "endpoint": "/api/core/models",
      "method": "GET",
      "user_agent": "Mozilla/5.0...",
      "ip_address": "192.168.1.100",
      "request_data": {
        "headers": {
          "Authorization": "Bearer expired_token"
        },
        "params": {
          "limit": 50
        }
      },
      "stack_trace": "...",
      "resolution": "Token refreshed successfully",
      "resolution_time": "2024-01-15T10:30:15Z"
    }
  }
}
```

## 🔗 Related Documentation

- **[01. API Overview](./01_overview.md)** - Introduction and architecture
- **[02. Core Operations](./02_core_operations.md)** - Basic CRUD operations
- **[03. Discovery & Profiling](./03_discovery_profiling.md)** - Model discovery
- **[04. Authentication](./04_authentication.md)** - Security and authentication
- **[05. Business Endpoints](./05_business_endpoints.md)** - Domain-specific APIs
- **[06. Business Intelligence](./06_business_intelligence.md)** - Analytics and reporting 