# 02. Core Operations API 🔧

## Overview

Core operations provide the foundation for all FBS functionality, including generic model operations, database management, token handling, and schema operations. These endpoints enable you to perform basic CRUD operations on any Odoo model while maintaining security and performance.

## 🔐 Authentication

All core operation endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

## 📊 Generic Model Operations

### **List Records**

Retrieve records from any Odoo model with advanced filtering, sorting, and pagination capabilities.

```http
GET /api/v1/{model_name}/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `domain` | string | No | `[]` | Odoo domain filter (JSON string) |
| `fields` | string | No | All fields | Comma-separated field names |
| `order` | string | No | `id` | Sort order (field ASC/DESC) |
| `limit` | integer | No | `100` | Number of records (max: 1000) |
| `offset` | integer | No | `0` | Number of records to skip |
| `context` | string | No | `{}` | Odoo context (JSON string) |
| `count` | boolean | No | `false` | Return total count only |

#### **Domain Filter Examples**

```json
// Simple filter
[["name", "=", "John Doe"]]

// Multiple conditions
[["name", "ilike", "john"], ["active", "=", true]]

// Complex filter with OR
["|", ["name", "ilike", "john"], ["email", "ilike", "john"]]

// Date range filter
[["create_date", ">=", "2024-01-01"], ["create_date", "<=", "2024-12-31"]]

// Related field filter
[["department_id.name", "=", "IT"]]
```

#### **Example Request**

```bash
curl -X GET "http://localhost:8001/api/v1/hr.employee/" \
  -H "Authorization: Bearer <your_token>" \
  -G \
  -d "limit=10" \
  -d "fields=id,name,salary,department_id" \
  -d "order=name" \
  -d "domain=[['active','=',true]]"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "records": [
      {
        "id": 1,
        "name": "John Doe",
        "salary": 50000,
        "department_id": [1, "IT Department"]
      },
      {
        "id": 2,
        "name": "Jane Smith",
        "salary": 55000,
        "department_id": [2, "HR Department"]
      }
    ],
    "count": 2,
    "total": 150,
    "has_more": true
  },
  "message": "Records retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Get Single Record**

Retrieve a specific record by ID with all its fields and related data.

```http
GET /api/v1/{model_name}/{id}/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `fields` | string | No | All fields | Comma-separated field names |
| `context` | string | No | `{}` | Odoo context (JSON string) |

#### **Example Request**

```bash
curl -X GET "http://localhost:8001/api/v1/hr.employee/1/" \
  -H "Authorization: Bearer <your_token>"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@company.com",
    "phone": "+1-555-0123",
    "salary": 50000,
    "department_id": [1, "IT Department"],
    "manager_id": [2, "Jane Smith"],
    "job_title": "Software Engineer",
    "hire_date": "2023-01-15",
    "active": true,
    "create_date": "2024-01-15T10:30:00Z",
    "write_date": "2024-01-15T10:30:00Z"
  },
  "message": "Record retrieved successfully"
}
```

### **Create Record**

Create a new record in the specified model with validation and error handling.

```http
POST /api/v1/{model_name}/
```

#### **Request Body**

The request body should contain the field values for the new record.

#### **Example Request**

```bash
curl -X POST "http://localhost:8001/api/v1/hr.employee/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice.johnson@company.com",
    "phone": "+1-555-0456",
    "salary": 60000,
    "department_id": 1,
    "job_title": "Senior Developer",
    "hire_date": "2024-01-20"
  }'
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "id": 3,
    "name": "Alice Johnson",
    "email": "alice.johnson@company.com",
    "phone": "+1-555-0456",
    "salary": 60000,
    "department_id": [1, "IT Department"],
    "job_title": "Senior Developer",
    "hire_date": "2024-01-20",
    "active": true,
    "create_date": "2024-01-15T10:35:00Z"
  },
  "message": "Employee created successfully"
}
```

### **Update Record**

Update an existing record with partial or complete field updates.

```http
PUT /api/v1/{model_name}/{id}/
```

#### **Example Request**

```bash
curl -X PUT "http://localhost:8001/api/v1/hr.employee/1/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "salary": 52000,
    "job_title": "Lead Developer"
  }'
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "salary": 52000,
    "job_title": "Lead Developer",
    "write_date": "2024-01-15T10:40:00Z"
  },
  "message": "Employee updated successfully"
}
```

### **Delete Record**

Delete a record from the specified model.

```http
DELETE /api/v1/{model_name}/{id}/
```

#### **Example Request**

```bash
curl -X DELETE "http://localhost:8001/api/v1/hr.employee/3/" \
  -H "Authorization: Bearer <your_token>"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "id": 3,
    "deleted": true
  },
  "message": "Employee deleted successfully"
}
```

### **Bulk Operations**

Perform operations on multiple records simultaneously for better performance.

#### **Bulk Create**

```http
POST /api/v1/{model_name}/bulk_create/
```

```bash
curl -X POST "http://localhost:8001/api/v1/hr.employee/bulk_create/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {
        "name": "Bob Wilson",
        "email": "bob.wilson@company.com",
        "salary": 45000,
        "department_id": 1
      },
      {
        "name": "Carol Davis",
        "email": "carol.davis@company.com",
        "salary": 48000,
        "department_id": 2
      }
    ]
  }'
```

#### **Bulk Update**

```http
PUT /api/v1/{model_name}/bulk_update/
```

```bash
curl -X PUT "http://localhost:8001/api/v1/hr.employee/bulk_update/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": [["department_id", "=", 1]],
    "values": {
      "salary": 55000
    }
  }'
```

#### **Bulk Delete**

```http
DELETE /api/v1/{model_name}/bulk_delete/
```

```bash
curl -X DELETE "http://localhost:8001/api/v1/hr.employee/bulk_delete/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": [["active", "=", false]]
  }'
```

## 🗄️ Database Management

### **List Databases**

Get a list of all available databases for the authenticated user.

```http
GET /api/databases/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "databases": [
      {
        "name": "fbs_rental_db",
        "description": "Rental Management System",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "last_activity": "2024-01-15T10:30:00Z",
        "size_mb": 1024,
        "user_count": 25
      },
      {
        "name": "fbs_ecommerce_db",
        "description": "E-commerce Platform",
        "status": "active",
        "created_at": "2024-01-05T00:00:00Z",
        "last_activity": "2024-01-15T09:15:00Z",
        "size_mb": 2048,
        "user_count": 50
      }
    ],
    "total": 2
  }
}
```

### **Create Database**

Create a new database with specified configuration.

```http
POST /api/databases/
```

#### **Example Request**

```bash
curl -X POST "http://localhost:8001/api/databases/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fbs_hr_db",
    "description": "Human Resources Management",
    "template_db": "fayvad",
    "modules": ["hr", "hr_attendance", "hr_expense"],
    "admin_user": "admin",
    "admin_password": "secure_password"
  }'
```

### **Database Status**

Get detailed status and statistics for a specific database.

```http
GET /api/databases/{database_name}/status/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "name": "fbs_rental_db",
    "status": "active",
    "uptime": "14 days, 5 hours",
    "connections": 15,
    "size_mb": 1024,
    "tables": 150,
    "users": 25,
    "last_backup": "2024-01-14T23:00:00Z",
    "performance": {
      "avg_query_time": "0.15s",
      "cache_hit_ratio": "95%",
      "active_queries": 3
    }
  }
}
```

## 🔑 Token Management

### **List API Tokens**

Get all API tokens for the authenticated user.

```http
GET /api/tokens/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "tokens": [
      {
        "id": 1,
        "name": "Mobile App Token",
        "key": "fbs_****_****_****_****",
        "created_at": "2024-01-01T00:00:00Z",
        "last_used": "2024-01-15T10:30:00Z",
        "permissions": ["read", "write"],
        "expires_at": "2024-12-31T23:59:59Z"
      }
    ]
  }
}
```

### **Create API Token**

Generate a new API token with specified permissions.

```http
POST /api/tokens/
```

#### **Example Request**

```bash
curl -X POST "http://localhost:8001/api/tokens/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Integration Token",
    "permissions": ["read", "write", "delete"],
    "expires_at": "2024-12-31T23:59:59Z",
    "allowed_ips": ["192.168.1.0/24"]
  }'
```

### **Revoke API Token**

Revoke an existing API token.

```http
DELETE /api/tokens/{token_id}/
```

## 🏗️ Schema Operations

### **Get Model Schema**

Retrieve the complete schema definition for a specific model.

```http
GET /api/schema/{model_name}/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "model": "hr.employee",
    "table": "hr_employee",
    "fields": {
      "id": {
        "type": "integer",
        "required": true,
        "readonly": true,
        "description": "Record ID"
      },
      "name": {
        "type": "char",
        "required": true,
        "size": 255,
        "description": "Employee Name"
      },
      "email": {
        "type": "char",
        "required": false,
        "size": 255,
        "description": "Email Address"
      },
      "department_id": {
        "type": "many2one",
        "relation": "hr.department",
        "required": false,
        "description": "Department"
      }
    },
    "constraints": [
      {
        "type": "unique",
        "fields": ["email"],
        "message": "Email must be unique"
      }
    ],
    "indexes": [
      {
        "name": "hr_employee_name_idx",
        "fields": ["name"]
      }
    ]
  }
}
```

### **Create Custom Schema**

Create a custom schema definition for a new model.

```http
POST /api/schema/
```

#### **Example Request**

```bash
curl -X POST "http://localhost:8001/api/schema/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "custom.project",
    "name": "Custom Project",
    "fields": {
      "name": {
        "type": "char",
        "required": true,
        "size": 255
      },
      "description": {
        "type": "text",
        "required": false
      },
      "start_date": {
        "type": "date",
        "required": true
      },
      "end_date": {
        "type": "date",
        "required": false
      },
      "status": {
        "type": "selection",
        "selection": [
          ["draft", "Draft"],
          ["active", "Active"],
          ["completed", "Completed"]
        ],
        "default": "draft"
      }
    }
  }'
```

## 📊 Performance Optimization

### **Query Optimization**

Use these techniques to optimize your API queries:

#### **Field Selection**
```bash
# Good: Select only needed fields
curl -X GET "http://localhost:8001/api/v1/hr.employee/" \
  -G -d "fields=id,name,email"

# Avoid: Selecting all fields
curl -X GET "http://localhost:8001/api/v1/hr.employee/"
```

#### **Efficient Filtering**
```bash
# Good: Use indexed fields
curl -X GET "http://localhost:8001/api/v1/hr.employee/" \
  -G -d "domain=[['id','=',1]]"

# Avoid: Complex text searches on large datasets
curl -X GET "http://localhost:8001/api/v1/hr.employee/" \
  -G -d "domain=[['name','ilike','john']]"
```

#### **Pagination**
```bash
# Good: Use pagination for large datasets
curl -X GET "http://localhost:8001/api/v1/hr.employee/" \
  -G -d "limit=50" -d "offset=0"

# Avoid: Loading all records at once
curl -X GET "http://localhost:8001/api/v1/hr.employee/" \
  -G -d "limit=10000"
```

## 🔗 Related Documentation

- **[01. API Overview](./01_overview.md)** - Introduction and architecture
- **[03. Discovery & Profiling](./03_discovery_profiling.md)** - Model discovery
- **[04. Authentication](./04_authentication.md)** - Security and authentication
- **[07. Error Handling](./07_error_handling.md)** - Error codes and handling 