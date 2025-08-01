# 04. Authentication & Security API 🔐

## Overview

The Authentication & Security API provides comprehensive security features including JWT authentication, role-based access control, API key management, and advanced security measures. This API ensures secure access to all FBS functionality while maintaining flexibility for different integration scenarios.

## 🔐 Authentication Methods

### **JWT Authentication (Primary)**

JWT (JSON Web Token) is the primary authentication method for FBS API. It provides secure, stateless authentication with built-in expiration and refresh capabilities.

#### **Login**

Authenticate with username and password to receive a JWT token.

```http
POST /api/auth/login/
```

#### **Request Body**

```json
{
  "username": "admin",
  "password": "secure_password",
  "remember_me": false,
  "device_info": {
    "device_type": "web",
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.100"
  }
}
```

#### **Example Request**

```bash
curl -X POST "http://localhost:8001/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure_password",
    "remember_me": false
  }'
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_expires_in": 86400,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@company.com",
      "first_name": "Admin",
      "last_name": "User",
      "is_active": true,
      "is_staff": true,
      "is_superuser": true,
      "permissions": [
        "auth.view_user",
        "auth.add_user",
        "auth.change_user",
        "auth.delete_user",
        "fbs.view_database",
        "fbs.manage_database"
      ],
      "groups": [
        "Administrators",
        "API Users"
      ],
      "last_login": "2024-01-15T10:30:00Z",
      "date_joined": "2024-01-01T00:00:00Z"
    }
  },
  "message": "Authentication successful"
}
```

#### **Token Usage**

Include the JWT token in the Authorization header for all subsequent requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Refresh Token**

Refresh an expired access token using the refresh token.

```http
POST /api/auth/refresh/
```

#### **Request Body**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **Example Request**

```bash
curl -X POST "http://localhost:8001/api/auth/refresh/" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  },
  "message": "Token refreshed successfully"
}
```

### **Logout**

Invalidate the current session and tokens.

```http
POST /api/auth/logout/
```

#### **Example Request**

```bash
curl -X POST "http://localhost:8001/api/auth/logout/" \
  -H "Authorization: Bearer <your_token>"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "logged_out": true
  },
  "message": "Successfully logged out"
}
```

## 🔑 API Key Authentication

### **Create API Key**

Generate a new API key for programmatic access.

```http
POST /api/auth/api-keys/
```

#### **Request Body**

```json
{
  "name": "Mobile App Integration",
  "description": "API key for mobile application",
  "permissions": [
    "fbs.view_database",
    "fbs.read_models",
    "fbs.create_records"
  ],
  "expires_at": "2024-12-31T23:59:59Z",
  "allowed_ips": ["192.168.1.0/24", "10.0.0.0/8"],
  "rate_limit": 1000,
  "is_active": true
}
```

#### **Example Request**

```bash
curl -X POST "http://localhost:8001/api/auth/api-keys/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile App Integration",
    "description": "API key for mobile application",
    "permissions": ["fbs.view_database", "fbs.read_models"],
    "expires_at": "2024-12-31T23:59:59Z"
  }'
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Mobile App Integration",
    "key": "fbs_live_1234567890abcdef",
    "description": "API key for mobile application",
    "permissions": [
      "fbs.view_database",
      "fbs.read_models"
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-12-31T23:59:59Z",
    "last_used": null,
    "is_active": true,
    "rate_limit": 1000,
    "allowed_ips": ["192.168.1.0/24", "10.0.0.0/8"]
  },
  "message": "API key created successfully"
}
```

### **List API Keys**

Get all API keys for the authenticated user.

```http
GET /api/auth/api-keys/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "api_keys": [
      {
        "id": 1,
        "name": "Mobile App Integration",
        "key": "fbs_****_****_****_****",
        "description": "API key for mobile application",
        "permissions": [
          "fbs.view_database",
          "fbs.read_models"
        ],
        "created_at": "2024-01-15T10:30:00Z",
        "last_used": "2024-01-15T10:35:00Z",
        "expires_at": "2024-12-31T23:59:59Z",
        "is_active": true,
        "rate_limit": 1000,
        "usage_count": 15
      },
      {
        "id": 2,
        "name": "Webhook Integration",
        "key": "fbs_****_****_****_****",
        "description": "API key for webhook notifications",
        "permissions": [
          "fbs.webhook_send"
        ],
        "created_at": "2024-01-10T00:00:00Z",
        "last_used": "2024-01-15T09:45:00Z",
        "expires_at": "2025-01-10T00:00:00Z",
        "is_active": true,
        "rate_limit": 100,
        "usage_count": 45
      }
    ],
    "total": 2,
    "active": 2,
    "expired": 0
  }
}
```

### **Revoke API Key**

Revoke an existing API key.

```http
DELETE /api/auth/api-keys/{key_id}/
```

#### **Example Request**

```bash
curl -X DELETE "http://localhost:8001/api/auth/api-keys/1/" \
  -H "Authorization: Bearer <your_token>"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "revoked": true,
    "revoked_at": "2024-01-15T10:40:00Z"
  },
  "message": "API key revoked successfully"
}
```

## 👥 User Management

### **Get Current User**

Get information about the currently authenticated user.

```http
GET /api/auth/user/
```

#### **Example Request**

```bash
curl -X GET "http://localhost:8001/api/auth/user/" \
  -H "Authorization: Bearer <your_token>"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@company.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_active": true,
    "is_staff": true,
    "is_superuser": true,
    "permissions": [
      "auth.view_user",
      "auth.add_user",
      "auth.change_user",
      "auth.delete_user",
      "fbs.view_database",
      "fbs.manage_database",
      "fbs.view_models",
      "fbs.manage_models"
    ],
    "groups": [
      {
        "id": 1,
        "name": "Administrators",
        "permissions": [
          "auth.view_user",
          "auth.add_user",
          "auth.change_user",
          "auth.delete_user"
        ]
      },
      {
        "id": 2,
        "name": "API Users",
        "permissions": [
          "fbs.view_database",
          "fbs.manage_database"
        ]
      }
    ],
    "profile": {
      "phone": "+1-555-0123",
      "timezone": "America/New_York",
      "language": "en",
      "theme": "dark"
    },
    "last_login": "2024-01-15T10:30:00Z",
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

### **Update User Profile**

Update the current user's profile information.

```http
PUT /api/auth/user/
```

#### **Request Body**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@company.com",
  "profile": {
    "phone": "+1-555-0456",
    "timezone": "America/Los_Angeles",
    "language": "en",
    "theme": "light"
  }
}
```

### **Change Password**

Change the current user's password.

```http
POST /api/auth/change-password/
```

#### **Request Body**

```json
{
  "current_password": "old_password",
  "new_password": "new_secure_password",
  "confirm_password": "new_secure_password"
}
```

## 🔒 Role-Based Access Control (RBAC)

### **List Permissions**

Get all available permissions in the system.

```http
GET /api/auth/permissions/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "permissions": [
      {
        "codename": "view_user",
        "name": "Can view user",
        "content_type": "auth | user"
      },
      {
        "codename": "add_user",
        "name": "Can add user",
        "content_type": "auth | user"
      },
      {
        "codename": "change_user",
        "name": "Can change user",
        "content_type": "auth | user"
      },
      {
        "codename": "delete_user",
        "name": "Can delete user",
        "content_type": "auth | user"
      },
      {
        "codename": "view_database",
        "name": "Can view database",
        "content_type": "fbs | database"
      },
      {
        "codename": "manage_database",
        "name": "Can manage database",
        "content_type": "fbs | database"
      },
      {
        "codename": "view_models",
        "name": "Can view models",
        "content_type": "fbs | model"
      },
      {
        "codename": "manage_models",
        "name": "Can manage models",
        "content_type": "fbs | model"
      }
    ],
    "content_types": [
      {
        "app_label": "auth",
        "model": "user",
        "name": "user"
      },
      {
        "app_label": "fbs",
        "model": "database",
        "name": "database"
      },
      {
        "app_label": "fbs",
        "model": "model",
        "name": "model"
      }
    ]
  }
}
```

### **List Groups**

Get all user groups and their permissions.

```http
GET /api/auth/groups/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "groups": [
      {
        "id": 1,
        "name": "Administrators",
        "description": "Full system access",
        "permissions": [
          "auth.view_user",
          "auth.add_user",
          "auth.change_user",
          "auth.delete_user",
          "fbs.view_database",
          "fbs.manage_database",
          "fbs.view_models",
          "fbs.manage_models"
        ],
        "user_count": 5
      },
      {
        "id": 2,
        "name": "API Users",
        "description": "API access only",
        "permissions": [
          "fbs.view_database",
          "fbs.manage_database"
        ],
        "user_count": 15
      },
      {
        "id": 3,
        "name": "Read Only",
        "description": "Read-only access",
        "permissions": [
          "fbs.view_database",
          "fbs.view_models"
        ],
        "user_count": 25
      }
    ],
    "total": 3
  }
}
```

### **Create Group**

Create a new user group with specific permissions.

```http
POST /api/auth/groups/
```

#### **Request Body**

```json
{
  "name": "Data Analysts",
  "description": "Access to analytics and reporting",
  "permissions": [
    "fbs.view_database",
    "fbs.view_models",
    "fbs.view_reports",
    "fbs.view_dashboards"
  ]
}
```

## 🛡️ Security Features

### **Two-Factor Authentication (2FA)**

#### **Enable 2FA**

Enable two-factor authentication for the current user.

```http
POST /api/auth/2fa/enable/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "backup_codes": [
      "12345678",
      "87654321",
      "11223344",
      "44332211"
    ],
    "secret_key": "JBSWY3DPEHPK3PXP"
  },
  "message": "2FA enabled successfully"
}
```

#### **Verify 2FA**

Verify 2FA token during login.

```http
POST /api/auth/2fa/verify/
```

#### **Request Body**

```json
{
  "token": "123456"
}
```

### **Session Management**

#### **List Active Sessions**

Get all active sessions for the current user.

```http
GET /api/auth/sessions/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": 1,
        "device_type": "web",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "ip_address": "192.168.1.100",
        "location": "New York, NY, USA",
        "created_at": "2024-01-15T10:30:00Z",
        "last_activity": "2024-01-15T10:35:00Z",
        "is_current": true
      },
      {
        "id": 2,
        "device_type": "mobile",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0...",
        "ip_address": "192.168.1.101",
        "location": "New York, NY, USA",
        "created_at": "2024-01-15T09:00:00Z",
        "last_activity": "2024-01-15T09:30:00Z",
        "is_current": false
      }
    ],
    "total": 2
  }
}
```

#### **Revoke Session**

Revoke a specific session.

```http
DELETE /api/auth/sessions/{session_id}/
```

### **Audit Log**

#### **Get Audit Log**

Get security audit log for the current user.

```http
GET /api/auth/audit-log/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `action` | string | No | - | Filter by action type |
| `start_date` | string | No | - | Start date (ISO format) |
| `end_date` | string | No | - | End date (ISO format) |
| `limit` | integer | No | `50` | Number of records |
| `offset` | integer | No | `0` | Number of records to skip |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "audit_logs": [
      {
        "id": 1,
        "action": "login",
        "description": "User logged in successfully",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "timestamp": "2024-01-15T10:30:00Z",
        "status": "success"
      },
      {
        "id": 2,
        "action": "api_key_created",
        "description": "API key 'Mobile App Integration' created",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "timestamp": "2024-01-15T10:35:00Z",
        "status": "success"
      },
      {
        "id": 3,
        "action": "failed_login",
        "description": "Failed login attempt with invalid password",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "timestamp": "2024-01-15T10:25:00Z",
        "status": "failed"
      }
    ],
    "total": 150,
    "summary": {
      "successful_logins": 120,
      "failed_logins": 5,
      "api_key_operations": 15,
      "password_changes": 3,
      "session_revocations": 7
    }
  }
}
```

## 🚦 Rate Limiting

### **Rate Limit Information**

Get current rate limit status for the authenticated user.

```http
GET /api/auth/rate-limits/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "current_usage": {
      "requests_made": 45,
      "requests_remaining": 955,
      "reset_time": "2024-01-15T11:30:00Z"
    },
    "limits": {
      "requests_per_hour": 1000,
      "requests_per_minute": 100,
      "burst_limit": 50
    },
    "endpoints": {
      "core_operations": {
        "limit": 1000,
        "used": 30,
        "remaining": 970
      },
      "discovery": {
        "limit": 100,
        "used": 5,
        "remaining": 95
      },
      "workflows": {
        "limit": 500,
        "used": 10,
        "remaining": 490
      }
    }
  }
}
```

## 🔧 Security Configuration

### **Get Security Settings**

Get current security configuration.

```http
GET /api/auth/security-settings/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "jwt_settings": {
      "access_token_lifetime": 3600,
      "refresh_token_lifetime": 86400,
      "algorithm": "HS256",
      "issuer": "fbs-api"
    },
    "password_policy": {
      "min_length": 8,
      "require_uppercase": true,
      "require_lowercase": true,
      "require_numbers": true,
      "require_special_chars": true,
      "max_age_days": 90
    },
    "session_settings": {
      "max_sessions_per_user": 5,
      "session_timeout": 3600,
      "inactive_timeout": 1800
    },
    "rate_limiting": {
      "enabled": true,
      "default_limit": 1000,
      "burst_limit": 100
    },
    "ip_whitelist": [
      "192.168.1.0/24",
      "10.0.0.0/8"
    ],
    "security_headers": {
      "hsts_enabled": true,
      "csp_enabled": true,
      "x_frame_options": "DENY"
    }
  }
}
```

## 🔗 Related Documentation

- **[01. API Overview](./01_overview.md)** - Introduction and architecture
- **[02. Core Operations](./02_core_operations.md)** - Basic CRUD operations
- **[03. Discovery & Profiling](./03_discovery_profiling.md)** - Model discovery
- **[07. Error Handling](./07_error_handling.md)** - Error codes and handling 