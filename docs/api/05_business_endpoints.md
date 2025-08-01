# 05. Business Endpoints API 🏢

## Overview

The Business Endpoints API provides domain-specific functionality for different industries and business processes. These endpoints are dynamically generated based on discovered models and capabilities, offering tailored solutions for specific business domains like rental management, e-commerce, HR, and more.

## 🔐 Authentication

All business endpoints require JWT authentication:

```http
Authorization: Bearer <your_jwt_token>
```

## 🏠 Rental Management Domain

### **Property Management**

#### **List Properties**

Get all properties with filtering and pagination.

```http
GET /api/rental/properties/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | - | Filter by status (available, rented, maintenance) |
| `property_type` | string | No | - | Filter by property type (apartment, house, office) |
| `location` | string | No | - | Filter by location |
| `min_price` | number | No | - | Minimum rental price |
| `max_price` | number | No | - | Maximum rental price |
| `amenities` | string | No | - | Comma-separated amenities |
| `limit` | integer | No | `50` | Number of records |
| `offset` | integer | No | `0` | Number of records to skip |

#### **Example Request**

```bash
curl -X GET "http://localhost:8001/api/rental/properties/" \
  -H "Authorization: Bearer <your_token>" \
  -G \
  -d "status=available" \
  -d "property_type=apartment" \
  -d "min_price=1000" \
  -d "max_price=3000"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "properties": [
      {
        "id": 1,
        "name": "Sunset Apartments - Unit 101",
        "property_type": "apartment",
        "address": "123 Sunset Blvd, Los Angeles, CA 90210",
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1200,
        "monthly_rent": 2500,
        "status": "available",
        "amenities": ["pool", "gym", "parking"],
        "description": "Beautiful 2-bedroom apartment with city views",
        "images": [
          "https://example.com/property1_1.jpg",
          "https://example.com/property1_2.jpg"
        ],
        "owner_id": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      },
      {
        "id": 2,
        "name": "Downtown Loft - Unit 205",
        "property_type": "apartment",
        "address": "456 Main St, Los Angeles, CA 90211",
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 800,
        "monthly_rent": 1800,
        "status": "available",
        "amenities": ["elevator", "doorman", "rooftop"],
        "description": "Modern loft in the heart of downtown",
        "images": [
          "https://example.com/property2_1.jpg"
        ],
        "owner_id": 2,
        "created_at": "2024-01-05T00:00:00Z",
        "updated_at": "2024-01-15T09:15:00Z"
      }
    ],
    "total": 25,
    "count": 2,
    "has_more": true
  }
}
```

#### **Get Property Details**

Get detailed information about a specific property.

```http
GET /api/rental/properties/{property_id}/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Sunset Apartments - Unit 101",
    "property_type": "apartment",
    "address": {
      "street": "123 Sunset Blvd",
      "city": "Los Angeles",
      "state": "CA",
      "zip_code": "90210",
      "country": "USA"
    },
    "bedrooms": 2,
    "bathrooms": 2,
    "square_feet": 1200,
    "monthly_rent": 2500,
    "security_deposit": 2500,
    "status": "available",
    "amenities": [
      {
        "name": "pool",
        "description": "Swimming pool",
        "available": true
      },
      {
        "name": "gym",
        "description": "Fitness center",
        "available": true
      },
      {
        "name": "parking",
        "description": "Assigned parking spot",
        "available": true
      }
    ],
    "description": "Beautiful 2-bedroom apartment with city views",
    "images": [
      {
        "url": "https://example.com/property1_1.jpg",
        "caption": "Living room",
        "is_primary": true
      },
      {
        "url": "https://example.com/property1_2.jpg",
        "caption": "Kitchen",
        "is_primary": false
      }
    ],
    "owner": {
      "id": 1,
      "name": "John Smith",
      "email": "john.smith@email.com",
      "phone": "+1-555-0123"
    },
    "maintenance_history": [
      {
        "id": 1,
        "issue": "Leaky faucet",
        "status": "completed",
        "reported_date": "2024-01-10T00:00:00Z",
        "completed_date": "2024-01-12T00:00:00Z",
        "cost": 150
      }
    ],
    "rental_history": [
      {
        "tenant_id": 5,
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "monthly_rent": 2400
      }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### **Create Property**

Add a new property to the system.

```http
POST /api/rental/properties/
```

#### **Request Body**

```json
{
  "name": "Ocean View Condo - Unit 301",
  "property_type": "condo",
  "address": {
    "street": "789 Beach Ave",
    "city": "Santa Monica",
    "state": "CA",
    "zip_code": "90401",
    "country": "USA"
  },
  "bedrooms": 3,
  "bathrooms": 2,
  "square_feet": 1500,
  "monthly_rent": 3500,
  "security_deposit": 3500,
  "amenities": ["ocean_view", "balcony", "parking"],
  "description": "Stunning ocean view condo with modern amenities",
  "owner_id": 1
}
```

#### **Update Property**

Update property information.

```http
PUT /api/rental/properties/{property_id}/
```

#### **Delete Property**

Remove a property from the system.

```http
DELETE /api/rental/properties/{property_id}/
```

### **Tenant Management**

#### **List Tenants**

Get all tenants with filtering and search.

```http
GET /api/rental/tenants/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | - | Filter by status (active, inactive, pending) |
| `search` | string | No | - | Search by name, email, or phone |
| `property_id` | integer | No | - | Filter by current property |
| `limit` | integer | No | `50` | Number of records |
| `offset` | integer | No | `0` | Number of records to skip |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "tenants": [
      {
        "id": 1,
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice.johnson@email.com",
        "phone": "+1-555-0456",
        "status": "active",
        "current_property": {
          "id": 1,
          "name": "Sunset Apartments - Unit 101"
        },
        "lease_start": "2024-01-01",
        "lease_end": "2024-12-31",
        "monthly_rent": 2500,
        "security_deposit": 2500,
        "emergency_contact": {
          "name": "Bob Johnson",
          "phone": "+1-555-0789",
          "relationship": "Spouse"
        },
        "created_at": "2023-12-15T00:00:00Z"
      }
    ],
    "total": 15,
    "count": 1
  }
}
```

#### **Get Tenant Details**

Get detailed tenant information including rental history.

```http
GET /api/rental/tenants/{tenant_id}/
```

#### **Create Tenant**

Add a new tenant to the system.

```http
POST /api/rental/tenants/
```

#### **Request Body**

```json
{
  "first_name": "David",
  "last_name": "Wilson",
  "email": "david.wilson@email.com",
  "phone": "+1-555-0321",
  "date_of_birth": "1985-06-15",
  "ssn": "123-45-6789",
  "employment": {
    "employer": "Tech Corp",
    "position": "Software Engineer",
    "salary": 80000
  },
  "emergency_contact": {
    "name": "Sarah Wilson",
    "phone": "+1-555-0654",
    "relationship": "Spouse"
  },
  "references": [
    {
      "name": "Mike Brown",
      "phone": "+1-555-0987",
      "relationship": "Previous Landlord"
    }
  ]
}
```

### **Lease Management**

#### **List Leases**

Get all lease agreements with filtering.

```http
GET /api/rental/leases/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | - | Filter by status (active, expired, pending) |
| `property_id` | integer | No | - | Filter by property |
| `tenant_id` | integer | No | - | Filter by tenant |
| `start_date` | string | No | - | Filter by lease start date |
| `end_date` | string | No | - | Filter by lease end date |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "leases": [
      {
        "id": 1,
        "property": {
          "id": 1,
          "name": "Sunset Apartments - Unit 101"
        },
        "tenant": {
          "id": 1,
          "name": "Alice Johnson"
        },
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "monthly_rent": 2500,
        "security_deposit": 2500,
        "status": "active",
        "terms": [
          "No pets allowed",
          "No smoking",
          "Utilities included"
        ],
        "created_at": "2023-12-15T00:00:00Z"
      }
    ],
    "total": 8
  }
}
```

#### **Create Lease**

Create a new lease agreement.

```http
POST /api/rental/leases/
```

#### **Request Body**

```json
{
  "property_id": 1,
  "tenant_id": 2,
  "start_date": "2024-02-01",
  "end_date": "2025-01-31",
  "monthly_rent": 2500,
  "security_deposit": 2500,
  "terms": [
    "No pets allowed",
    "No smoking",
    "Utilities included",
    "Quiet hours 10 PM - 8 AM"
  ],
  "utilities_included": ["water", "electricity"],
  "late_fee": 50,
  "grace_period_days": 5
}
```

### **Payment Management**

#### **List Payments**

Get all rental payments with filtering.

```http
GET /api/rental/payments/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | - | Filter by status (paid, pending, late) |
| `property_id` | integer | No | - | Filter by property |
| `tenant_id` | integer | No | - | Filter by tenant |
| `start_date` | string | No | - | Filter by payment date |
| `end_date` | string | No | - | Filter by payment date |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "payments": [
      {
        "id": 1,
        "lease": {
          "id": 1,
          "property_name": "Sunset Apartments - Unit 101",
          "tenant_name": "Alice Johnson"
        },
        "amount": 2500,
        "due_date": "2024-01-01",
        "paid_date": "2024-01-01",
        "status": "paid",
        "payment_method": "bank_transfer",
        "reference_number": "TXN123456",
        "late_fee": 0,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 25,
    "summary": {
      "total_collected": 62500,
      "total_pending": 5000,
      "total_late": 250
    }
  }
}
```

#### **Record Payment**

Record a new payment.

```http
POST /api/rental/payments/
```

#### **Request Body**

```json
{
  "lease_id": 1,
  "amount": 2500,
  "payment_method": "credit_card",
  "reference_number": "CC789012",
  "notes": "January 2024 rent payment"
}
```

### **Maintenance Management**

#### **List Maintenance Requests**

Get all maintenance requests.

```http
GET /api/rental/maintenance/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | - | Filter by status (pending, in_progress, completed) |
| `priority` | string | No | - | Filter by priority (low, medium, high, urgent) |
| `property_id` | integer | No | - | Filter by property |
| `tenant_id` | integer | No | - | Filter by tenant |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "maintenance_requests": [
      {
        "id": 1,
        "property": {
          "id": 1,
          "name": "Sunset Apartments - Unit 101"
        },
        "tenant": {
          "id": 1,
          "name": "Alice Johnson"
        },
        "issue": "Leaky kitchen faucet",
        "description": "Water is dripping from the kitchen faucet handle",
        "priority": "medium",
        "status": "in_progress",
        "reported_date": "2024-01-15T10:00:00Z",
        "assigned_to": {
          "id": 3,
          "name": "Mike Plumber"
        },
        "estimated_completion": "2024-01-17T00:00:00Z",
        "estimated_cost": 150,
        "images": [
          "https://example.com/leak1.jpg"
        ]
      }
    ],
    "total": 12
  }
}
```

#### **Create Maintenance Request**

Create a new maintenance request.

```http
POST /api/rental/maintenance/
```

#### **Request Body**

```json
{
  "property_id": 1,
  "tenant_id": 1,
  "issue": "Broken window lock",
  "description": "The window lock in the living room is broken and won't secure properly",
  "priority": "high",
  "images": [
    "https://example.com/window_lock.jpg"
  ]
}
```

## 🛒 E-commerce Domain

### **Product Management**

#### **List Products**

Get all products with filtering and search.

```http
GET /api/ecommerce/products/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `category` | string | No | - | Filter by category |
| `search` | string | No | - | Search by name or description |
| `min_price` | number | No | - | Minimum price |
| `max_price` | number | No | - | Maximum price |
| `in_stock` | boolean | No | - | Filter by stock availability |
| `limit` | integer | No | `50` | Number of records |
| `offset` | integer | No | `0` | Number of records to skip |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "products": [
      {
        "id": 1,
        "name": "Wireless Bluetooth Headphones",
        "description": "High-quality wireless headphones with noise cancellation",
        "category": "Electronics",
        "price": 99.99,
        "sale_price": 79.99,
        "stock_quantity": 50,
        "sku": "WH-001",
        "images": [
          "https://example.com/headphones1.jpg"
        ],
        "specifications": {
          "brand": "AudioTech",
          "model": "ATH-WH1000",
          "battery_life": "30 hours",
          "connectivity": "Bluetooth 5.0"
        },
        "reviews": {
          "average_rating": 4.5,
          "total_reviews": 125
        },
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 150,
    "count": 1
  }
}
```

### **Order Management**

#### **List Orders**

Get all orders with filtering.

```http
GET /api/ecommerce/orders/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | - | Filter by status (pending, confirmed, shipped, delivered) |
| `customer_id` | integer | No | - | Filter by customer |
| `start_date` | string | No | - | Filter by order date |
| `end_date` | string | No | - | Filter by order date |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "orders": [
      {
        "id": 1,
        "order_number": "ORD-2024-001",
        "customer": {
          "id": 1,
          "name": "John Doe",
          "email": "john.doe@email.com"
        },
        "items": [
          {
            "product_id": 1,
            "name": "Wireless Bluetooth Headphones",
            "quantity": 1,
            "unit_price": 79.99,
            "total_price": 79.99
          }
        ],
        "subtotal": 79.99,
        "tax": 6.40,
        "shipping": 5.99,
        "total": 92.38,
        "status": "confirmed",
        "payment_status": "paid",
        "shipping_address": {
          "street": "123 Main St",
          "city": "Los Angeles",
          "state": "CA",
          "zip_code": "90210"
        },
        "order_date": "2024-01-15T10:30:00Z",
        "estimated_delivery": "2024-01-20T00:00:00Z"
      }
    ],
    "total": 45
  }
}
```

## 👥 HR Domain

### **Employee Management**

#### **List Employees**

Get all employees with filtering.

```http
GET /api/hr/employees/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `department` | string | No | - | Filter by department |
| `status` | string | No | - | Filter by status (active, inactive, terminated) |
| `search` | string | No | - | Search by name or email |
| `limit` | integer | No | `50` | Number of records |
| `offset` | integer | No | `0` | Number of records to skip |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "employees": [
      {
        "id": 1,
        "employee_id": "EMP001",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.johnson@company.com",
        "phone": "+1-555-0123",
        "department": {
          "id": 1,
          "name": "Engineering"
        },
        "position": "Senior Software Engineer",
        "hire_date": "2023-01-15",
        "salary": 85000,
        "status": "active",
        "manager": {
          "id": 2,
          "name": "Mike Manager"
        },
        "profile_image": "https://example.com/sarah.jpg"
      }
    ],
    "total": 25
  }
}
```

### **Attendance Management**

#### **List Attendance Records**

Get attendance records for employees.

```http
GET /api/hr/attendance/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `employee_id` | integer | No | - | Filter by employee |
| `date` | string | No | - | Filter by date |
| `start_date` | string | No | - | Filter by start date |
| `end_date` | string | No | - | Filter by end date |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "attendance_records": [
      {
        "id": 1,
        "employee": {
          "id": 1,
          "name": "Sarah Johnson"
        },
        "date": "2024-01-15",
        "check_in": "2024-01-15T09:00:00Z",
        "check_out": "2024-01-15T17:00:00Z",
        "total_hours": 8.0,
        "status": "present",
        "notes": "Regular work day"
      }
    ],
    "total": 150
  }
}
```

## 🔄 Workflow Management

### **Workflow Definitions**

#### **List Workflows**

Get all available workflow definitions.

```http
GET /api/workflows/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "workflows": [
      {
        "id": 1,
        "name": "rental_application",
        "display_name": "Rental Application Process",
        "model": "rental.application",
        "description": "Complete rental application workflow",
        "states": [
          {
            "name": "draft",
            "display_name": "Draft",
            "color": "#6c757d",
            "is_initial": true
          },
          {
            "name": "submitted",
            "display_name": "Submitted",
            "color": "#17a2b8",
            "is_initial": false
          },
          {
            "name": "under_review",
            "display_name": "Under Review",
            "color": "#ffc107",
            "is_initial": false
          },
          {
            "name": "approved",
            "display_name": "Approved",
            "color": "#28a745",
            "is_initial": false
          },
          {
            "name": "rejected",
            "display_name": "Rejected",
            "color": "#dc3545",
            "is_initial": false
          }
        ],
        "transitions": [
          {
            "from": "draft",
            "to": "submitted",
            "trigger": "submit",
            "conditions": ["application_complete"],
            "actions": ["send_notification", "assign_reviewer"]
          },
          {
            "from": "submitted",
            "to": "under_review",
            "trigger": "start_review",
            "conditions": ["reviewer_assigned"],
            "actions": ["schedule_interview"]
          },
          {
            "from": "under_review",
            "to": "approved",
            "trigger": "approve",
            "conditions": ["background_check_passed", "income_verified"],
            "actions": ["create_lease", "send_approval_email"]
          },
          {
            "from": "under_review",
            "to": "rejected",
            "trigger": "reject",
            "conditions": ["background_check_failed"],
            "actions": ["send_rejection_email"]
          }
        ],
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 5
  }
}
```

#### **Create Workflow**

Create a new workflow definition.

```http
POST /api/workflows/
```

#### **Request Body**

```json
{
  "name": "maintenance_request",
  "display_name": "Maintenance Request Process",
  "model": "rental.maintenance",
  "description": "Maintenance request workflow",
  "states": [
    {
      "name": "pending",
      "display_name": "Pending",
      "color": "#6c757d",
      "is_initial": true
    },
    {
      "name": "assigned",
      "display_name": "Assigned",
      "color": "#17a2b8",
      "is_initial": false
    },
    {
      "name": "in_progress",
      "display_name": "In Progress",
      "color": "#ffc107",
      "is_initial": false
    },
    {
      "name": "completed",
      "display_name": "Completed",
      "color": "#28a745",
      "is_initial": false
    }
  ],
  "transitions": [
    {
      "from": "pending",
      "to": "assigned",
      "trigger": "assign",
      "conditions": ["technician_available"],
      "actions": ["notify_technician"]
    },
    {
      "from": "assigned",
      "to": "in_progress",
      "trigger": "start_work",
      "conditions": ["technician_arrived"],
      "actions": ["update_tenant"]
    },
    {
      "from": "in_progress",
      "to": "completed",
      "trigger": "complete",
      "conditions": ["work_finished"],
      "actions": ["notify_tenant", "create_invoice"]
    }
  ]
}
```

### **Workflow Instances**

#### **List Workflow Instances**

Get all workflow instances.

```http
GET /api/workflows/instances/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `workflow_id` | integer | No | - | Filter by workflow |
| `status` | string | No | - | Filter by current state |
| `created_by` | integer | No | - | Filter by creator |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "instances": [
      {
        "id": 1,
        "workflow": {
          "id": 1,
          "name": "rental_application",
          "display_name": "Rental Application Process"
        },
        "record_id": 5,
        "current_state": "under_review",
        "current_state_display": "Under Review",
        "created_by": {
          "id": 1,
          "name": "Alice Johnson"
        },
        "assigned_to": {
          "id": 3,
          "name": "Property Manager"
        },
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T14:30:00Z",
        "history": [
          {
            "from_state": "draft",
            "to_state": "submitted",
            "trigger": "submit",
            "timestamp": "2024-01-15T10:00:00Z",
            "user": "Alice Johnson"
          },
          {
            "from_state": "submitted",
            "to_state": "under_review",
            "trigger": "start_review",
            "timestamp": "2024-01-15T14:30:00Z",
            "user": "Property Manager"
          }
        ]
      }
    ],
    "total": 12
  }
}
```

#### **Execute Workflow Transition**

Execute a workflow transition.

```http
POST /api/workflows/instances/{instance_id}/transition/
```

#### **Request Body**

```json
{
  "trigger": "approve",
  "data": {
    "approval_notes": "Application approved after background check",
    "lease_start_date": "2024-02-01"
  }
}
```

## 🔗 Related Documentation

- **[01. API Overview](./01_overview.md)** - Introduction and architecture
- **[02. Core Operations](./02_core_operations.md)** - Basic CRUD operations
- **[03. Discovery & Profiling](./03_discovery_profiling.md)** - Model discovery
- **[04. Authentication](./04_authentication.md)** - Security and authentication
- **[06. Business Intelligence](./06_business_intelligence.md)** - Analytics and reporting 