# 08. Webhooks & Integrations API 🔗

## Overview

The Webhooks & Integrations API provides comprehensive webhook management, third-party integrations, and event-driven communication capabilities. This API enables real-time data synchronization, automated workflows, and seamless integration with external systems.

## 🔐 Authentication

All webhook and integration endpoints require JWT authentication:

```http
Authorization: Bearer <your_jwt_token>
```

## 🔔 Webhook Management

### **Create Webhook**

Create a new webhook endpoint for receiving events.

```http
POST /api/webhooks/
```

#### **Request Body**

```json
{
  "name": "order_notifications",
  "description": "Webhook for order status updates",
  "url": "https://your-app.com/webhooks/orders",
  "events": [
    "order.created",
    "order.updated",
    "order.cancelled"
  ],
  "headers": {
    "X-Custom-Header": "custom-value",
    "Authorization": "Bearer your-secret-token"
  },
  "secret": "your-webhook-secret",
  "is_active": true,
  "retry_config": {
    "max_retries": 3,
    "retry_delay": 5000,
    "backoff_multiplier": 2
  },
  "filters": {
    "order_status": ["confirmed", "shipped"],
    "min_amount": 100
  }
}
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "webhook": {
      "id": 1,
      "name": "order_notifications",
      "description": "Webhook for order status updates",
      "url": "https://your-app.com/webhooks/orders",
      "events": [
        "order.created",
        "order.updated",
        "order.cancelled"
      ],
      "headers": {
        "X-Custom-Header": "custom-value"
      },
      "secret": "whsec_123456789",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "last_triggered": null,
      "success_count": 0,
      "failure_count": 0,
      "retry_config": {
        "max_retries": 3,
        "retry_delay": 5000,
        "backoff_multiplier": 2
      },
      "filters": {
        "order_status": ["confirmed", "shipped"],
        "min_amount": 100
      }
    }
  },
  "message": "Webhook created successfully"
}
```

### **List Webhooks**

Get all webhooks for the authenticated user.

```http
GET /api/webhooks/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | - | Filter by status (active, inactive) |
| `event` | string | No | - | Filter by event type |
| `limit` | integer | No | `50` | Number of records |
| `offset` | integer | No | `0` | Number of records to skip |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "webhooks": [
      {
        "id": 1,
        "name": "order_notifications",
        "description": "Webhook for order status updates",
        "url": "https://your-app.com/webhooks/orders",
        "events": [
          "order.created",
          "order.updated",
          "order.cancelled"
        ],
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "last_triggered": "2024-01-15T10:35:00Z",
        "success_count": 25,
        "failure_count": 2,
        "success_rate": 92.6
      },
      {
        "id": 2,
        "name": "inventory_alerts",
        "description": "Webhook for low stock alerts",
        "url": "https://your-app.com/webhooks/inventory",
        "events": [
          "inventory.low_stock",
          "inventory.out_of_stock"
        ],
        "is_active": true,
        "created_at": "2024-01-15T09:00:00Z",
        "last_triggered": "2024-01-15T10:20:00Z",
        "success_count": 10,
        "failure_count": 0,
        "success_rate": 100.0
      }
    ],
    "total": 2,
    "summary": {
      "total_webhooks": 2,
      "active_webhooks": 2,
      "total_events": 15,
      "avg_success_rate": 96.3
    }
  }
}
```

### **Get Webhook Details**

Get detailed information about a specific webhook.

```http
GET /api/webhooks/{webhook_id}/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "webhook": {
      "id": 1,
      "name": "order_notifications",
      "description": "Webhook for order status updates",
      "url": "https://your-app.com/webhooks/orders",
      "events": [
        "order.created",
        "order.updated",
        "order.cancelled"
      ],
      "headers": {
        "X-Custom-Header": "custom-value",
        "Authorization": "Bearer your-secret-token"
      },
      "secret": "whsec_123456789",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "last_triggered": "2024-01-15T10:35:00Z",
      "success_count": 25,
      "failure_count": 2,
      "success_rate": 92.6,
      "retry_config": {
        "max_retries": 3,
        "retry_delay": 5000,
        "backoff_multiplier": 2
      },
      "filters": {
        "order_status": ["confirmed", "shipped"],
        "min_amount": 100
      },
      "delivery_stats": {
        "total_deliveries": 27,
        "successful_deliveries": 25,
        "failed_deliveries": 2,
        "avg_response_time": 250,
        "last_response_time": 180
      }
    }
  }
}
```

### **Update Webhook**

Update webhook configuration.

```http
PUT /api/webhooks/{webhook_id}/
```

#### **Request Body**

```json
{
  "name": "order_notifications_v2",
  "description": "Updated webhook for order notifications",
  "url": "https://your-app.com/webhooks/orders/v2",
  "events": [
    "order.created",
    "order.updated",
    "order.cancelled",
    "order.shipped"
  ],
  "headers": {
    "X-Custom-Header": "updated-value",
    "X-Version": "2.0"
  },
  "is_active": true,
  "filters": {
    "order_status": ["confirmed", "shipped", "delivered"],
    "min_amount": 50
  }
}
```

### **Delete Webhook**

Delete a webhook endpoint.

```http
DELETE /api/webhooks/{webhook_id}/
```

### **Test Webhook**

Test webhook delivery with a sample payload.

```http
POST /api/webhooks/{webhook_id}/test/
```

#### **Request Body**

```json
{
  "event": "order.created",
  "payload": {
    "order_id": "ORD-123",
    "status": "confirmed",
    "amount": 150.00,
    "customer": {
      "id": 1,
      "name": "John Doe"
    }
  }
}
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "test_result": {
      "status": "success",
      "response_code": 200,
      "response_time": 180,
      "response_body": "OK",
      "headers_sent": {
        "Content-Type": "application/json",
        "X-Webhook-Signature": "sha256=abc123...",
        "X-Custom-Header": "custom-value"
      },
      "timestamp": "2024-01-15T10:40:00Z"
    }
  },
  "message": "Webhook test completed successfully"
}
```

## 📊 Webhook Events

### **List Available Events**

Get all available webhook events.

```http
GET /api/webhooks/events/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "events": [
      {
        "name": "order.created",
        "description": "Order created",
        "category": "sales",
        "version": "1.0",
        "payload_schema": {
          "type": "object",
          "properties": {
            "order_id": {"type": "string"},
            "status": {"type": "string"},
            "amount": {"type": "number"},
            "customer": {"type": "object"}
          }
        },
        "example_payload": {
          "order_id": "ORD-123",
          "status": "draft",
          "amount": 150.00,
          "customer": {
            "id": 1,
            "name": "John Doe"
          }
        }
      },
      {
        "name": "order.updated",
        "description": "Order updated",
        "category": "sales",
        "version": "1.0",
        "payload_schema": {
          "type": "object",
          "properties": {
            "order_id": {"type": "string"},
            "status": {"type": "string"},
            "changes": {"type": "object"}
          }
        }
      },
      {
        "name": "inventory.low_stock",
        "description": "Product low stock alert",
        "category": "inventory",
        "version": "1.0",
        "payload_schema": {
          "type": "object",
          "properties": {
            "product_id": {"type": "integer"},
            "product_name": {"type": "string"},
            "current_stock": {"type": "integer"},
            "threshold": {"type": "integer"}
          }
        }
      }
    ],
    "categories": [
      {
        "name": "sales",
        "display_name": "Sales",
        "event_count": 8
      },
      {
        "name": "inventory",
        "display_name": "Inventory",
        "event_count": 5
      },
      {
        "name": "customer",
        "display_name": "Customer",
        "event_count": 4
      }
    ]
  }
}
```

### **Get Event Details**

Get detailed information about a specific event.

```http
GET /api/webhooks/events/{event_name}/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "event": {
      "name": "order.created",
      "description": "Triggered when a new order is created",
      "category": "sales",
      "version": "1.0",
      "deprecated": false,
      "payload_schema": {
        "type": "object",
        "required": ["order_id", "status", "amount"],
        "properties": {
          "order_id": {
            "type": "string",
            "description": "Unique order identifier"
          },
          "status": {
            "type": "string",
            "enum": ["draft", "confirmed", "shipped", "delivered", "cancelled"],
            "description": "Order status"
          },
          "amount": {
            "type": "number",
            "description": "Total order amount"
          },
          "customer": {
            "type": "object",
            "properties": {
              "id": {"type": "integer"},
              "name": {"type": "string"},
              "email": {"type": "string"}
            }
          },
          "items": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "product_id": {"type": "integer"},
                "name": {"type": "string"},
                "quantity": {"type": "integer"},
                "price": {"type": "number"}
              }
            }
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          }
        }
      },
      "example_payload": {
        "order_id": "ORD-123",
        "status": "draft",
        "amount": 150.00,
        "customer": {
          "id": 1,
          "name": "John Doe",
          "email": "john.doe@example.com"
        },
        "items": [
          {
            "product_id": 1,
            "name": "Wireless Headphones",
            "quantity": 1,
            "price": 150.00
          }
        ],
        "created_at": "2024-01-15T10:30:00Z"
      },
      "webhooks_count": 15,
      "last_triggered": "2024-01-15T10:35:00Z"
    }
  }
}
```

## 📈 Webhook Analytics

### **Get Webhook Statistics**

Get webhook delivery statistics and performance metrics.

```http
GET /api/webhooks/{webhook_id}/stats/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | No | - | Start date (ISO format) |
| `end_date` | string | No | - | End date (ISO format) |
| `group_by` | string | No | `day` | Group by (hour, day, week, month) |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "webhook_id": 1,
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-15"
    },
    "summary": {
      "total_events": 150,
      "successful_deliveries": 142,
      "failed_deliveries": 8,
      "success_rate": 94.7,
      "avg_response_time": 245,
      "total_retries": 12
    },
    "events_by_type": [
      {
        "event": "order.created",
        "count": 75,
        "success_rate": 96.0
      },
      {
        "event": "order.updated",
        "count": 60,
        "success_rate": 93.3
      },
      {
        "event": "order.cancelled",
        "count": 15,
        "success_rate": 93.3
      }
    ],
    "time_series": [
      {
        "date": "2024-01-15",
        "total_events": 10,
        "successful": 9,
        "failed": 1,
        "avg_response_time": 230
      }
    ],
    "error_breakdown": [
      {
        "error_type": "timeout",
        "count": 5,
        "percentage": 62.5
      },
      {
        "error_type": "http_500",
        "count": 2,
        "percentage": 25.0
      },
      {
        "error_type": "connection_error",
        "count": 1,
        "percentage": 12.5
      }
    ]
  }
}
```

### **Get Webhook Delivery Logs**

Get detailed delivery logs for a webhook.

```http
GET /api/webhooks/{webhook_id}/logs/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | - | Filter by status (success, failed) |
| `event` | string | No | - | Filter by event type |
| `start_date` | string | No | - | Start date (ISO format) |
| `end_date` | string | No | - | End date (ISO format) |
| `limit` | integer | No | `50` | Number of records |
| `offset` | integer | No | `0` | Number of records to skip |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 1,
        "event": "order.created",
        "status": "success",
        "response_code": 200,
        "response_time": 180,
        "timestamp": "2024-01-15T10:35:00Z",
        "payload": {
          "order_id": "ORD-123",
          "status": "confirmed",
          "amount": 150.00
        },
        "response_body": "OK",
        "retry_count": 0
      },
      {
        "id": 2,
        "event": "order.updated",
        "status": "failed",
        "response_code": 500,
        "response_time": 5000,
        "timestamp": "2024-01-15T10:30:00Z",
        "payload": {
          "order_id": "ORD-124",
          "status": "shipped"
        },
        "error_message": "Internal server error",
        "retry_count": 2,
        "next_retry": "2024-01-15T10:40:00Z"
      }
    ],
    "total": 150,
    "summary": {
      "successful": 142,
      "failed": 8,
      "pending_retry": 2
    }
  }
}
```

## 🔗 Third-Party Integrations

### **List Available Integrations**

Get all available third-party integrations.

```http
GET /api/integrations/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "integrations": [
      {
        "id": 1,
        "name": "slack",
        "display_name": "Slack",
        "description": "Send notifications to Slack channels",
        "category": "communication",
        "icon": "https://example.com/slack-icon.png",
        "is_available": true,
        "is_configured": true,
        "config_fields": [
          {
            "name": "webhook_url",
            "type": "url",
            "required": true,
            "description": "Slack webhook URL"
          },
          {
            "name": "channel",
            "type": "string",
            "required": false,
            "description": "Default channel for notifications"
          }
        ]
      },
      {
        "id": 2,
        "name": "zapier",
        "display_name": "Zapier",
        "description": "Connect with 5000+ apps via Zapier",
        "category": "automation",
        "icon": "https://example.com/zapier-icon.png",
        "is_available": true,
        "is_configured": false,
        "config_fields": [
          {
            "name": "api_key",
            "type": "string",
            "required": true,
            "description": "Zapier API key"
          }
        ]
      },
      {
        "id": 3,
        "name": "mailchimp",
        "display_name": "Mailchimp",
        "description": "Email marketing integration",
        "category": "marketing",
        "icon": "https://example.com/mailchimp-icon.png",
        "is_available": true,
        "is_configured": false,
        "config_fields": [
          {
            "name": "api_key",
            "type": "string",
            "required": true,
            "description": "Mailchimp API key"
          },
          {
            "name": "list_id",
            "type": "string",
            "required": true,
            "description": "Audience list ID"
          }
        ]
      }
    ],
    "categories": [
      {
        "name": "communication",
        "display_name": "Communication",
        "integration_count": 3
      },
      {
        "name": "automation",
        "display_name": "Automation",
        "integration_count": 2
      },
      {
        "name": "marketing",
        "display_name": "Marketing",
        "integration_count": 1
      }
    ]
  }
}
```

### **Configure Integration**

Configure a third-party integration.

```http
POST /api/integrations/{integration_name}/configure/
```

#### **Request Body**

```json
{
  "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
  "channel": "#orders",
  "notifications": {
    "order.created": true,
    "order.updated": true,
    "inventory.low_stock": false
  },
  "message_template": "New order {{order_id}} for ${{amount}} has been {{status}}"
}
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "integration": {
      "id": 1,
      "name": "slack",
      "display_name": "Slack",
      "is_configured": true,
      "config": {
        "webhook_url": "https://hooks.slack.com/services/...",
        "channel": "#orders",
        "notifications": {
          "order.created": true,
          "order.updated": true,
          "inventory.low_stock": false
        },
        "message_template": "New order {{order_id}} for ${{amount}} has been {{status}}"
      },
      "status": "active",
      "last_sync": "2024-01-15T10:30:00Z",
      "sync_count": 25
    }
  },
  "message": "Slack integration configured successfully"
}
```

### **Test Integration**

Test a configured integration.

```http
POST /api/integrations/{integration_name}/test/
```

#### **Request Body**

```json
{
  "event": "order.created",
  "payload": {
    "order_id": "ORD-123",
    "status": "confirmed",
    "amount": 150.00,
    "customer": {
      "name": "John Doe"
    }
  }
}
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "test_result": {
      "status": "success",
      "message": "Test notification sent to #orders channel",
      "response_time": 1200,
      "timestamp": "2024-01-15T10:40:00Z"
    }
  },
  "message": "Integration test completed successfully"
}
```

### **Get Integration Status**

Get status and statistics for a configured integration.

```http
GET /api/integrations/{integration_name}/status/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "integration": {
      "id": 1,
      "name": "slack",
      "display_name": "Slack",
      "status": "active",
      "is_configured": true,
      "last_sync": "2024-01-15T10:30:00Z",
      "sync_count": 25,
      "error_count": 2,
      "success_rate": 92.0,
      "config": {
        "webhook_url": "https://hooks.slack.com/services/...",
        "channel": "#orders",
        "notifications": {
          "order.created": true,
          "order.updated": true,
          "inventory.low_stock": false
        }
      },
      "recent_activity": [
        {
          "event": "order.created",
          "timestamp": "2024-01-15T10:30:00Z",
          "status": "success",
          "message": "Notification sent to #orders"
        },
        {
          "event": "order.updated",
          "timestamp": "2024-01-15T10:25:00Z",
          "status": "success",
          "message": "Notification sent to #orders"
        }
      ]
    }
  }
}
```

## 🔄 Event Streaming

### **Subscribe to Event Stream**

Subscribe to real-time event stream.

```http
GET /api/events/stream/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `events` | string | No | - | Comma-separated event types |
| `format` | string | No | `json` | Stream format (json, sse) |

#### **Example Response (Server-Sent Events)**

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: order.created
data: {
  "order_id": "ORD-123",
  "status": "confirmed",
  "amount": 150.00,
  "timestamp": "2024-01-15T10:30:00Z"
}

event: inventory.low_stock
data: {
  "product_id": 1,
  "product_name": "Wireless Headphones",
  "current_stock": 5,
  "threshold": 10,
  "timestamp": "2024-01-15T10:31:00Z"
}
```

## 🔗 Related Documentation

- **[01. API Overview](./01_overview.md)** - Introduction and architecture
- **[02. Core Operations](./02_core_operations.md)** - Basic CRUD operations
- **[03. Discovery & Profiling](./03_discovery_profiling.md)** - Model discovery
- **[04. Authentication](./04_authentication.md)** - Security and authentication
- **[05. Business Endpoints](./05_business_endpoints.md)** - Domain-specific APIs
- **[06. Business Intelligence](./06_business_intelligence.md)** - Analytics and reporting
- **[07. Error Handling](./07_error_handling.md)** - Error codes and handling 