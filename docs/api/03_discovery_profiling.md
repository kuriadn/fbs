# 03. Discovery & Profiling API 🔍

## Overview

The Discovery & Profiling API enables you to dynamically discover and analyze Odoo models, their capabilities, workflows, and business intelligence features. This API is the foundation for building adaptive applications that can work with any Odoo system without hardcoding model structures.

## 🔐 Authentication

All discovery endpoints require JWT authentication:

```http
Authorization: Bearer <your_jwt_token>
```

## 📊 Model Discovery

### **List All Models**

Discover all available models in the Odoo system with their metadata and capabilities.

```http
GET /api/profile/models/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `db` | string | Yes | - | Database name |
| `domain` | string | No | `[]` | Filter models by domain |
| `installed_only` | boolean | No | `true` | Show only installed models |
| `include_fields` | boolean | No | `false` | Include field definitions |
| `include_workflows` | boolean | No | `false` | Include workflow analysis |
| `include_bi` | boolean | No | `false` | Include BI features |

#### **Example Request**

```bash
curl -X GET "http://localhost:8001/api/profile/models/" \
  -H "Authorization: Bearer <your_token>" \
  -G \
  -d "db=fbs_rental_db" \
  -d "include_fields=true" \
  -d "include_workflows=true"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "models": {
      "hr.employee": {
        "name": "Employee",
        "description": "Employee management",
        "table": "hr_employee",
        "installed": true,
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
          },
          "manager_id": {
            "type": "many2one",
            "relation": "hr.employee",
            "required": false,
            "description": "Manager"
          },
          "salary": {
            "type": "monetary",
            "required": false,
            "description": "Salary"
          },
          "state": {
            "type": "selection",
            "selection": [
              ["draft", "Draft"],
              ["active", "Active"],
              ["inactive", "Inactive"]
            ],
            "default": "draft",
            "description": "Status"
          }
        },
        "workflows": {
          "available_states": ["draft", "active", "inactive"],
          "transitions": [
            {"from": "draft", "to": "active", "trigger": "activate"},
            {"from": "active", "to": "inactive", "trigger": "deactivate"},
            {"from": "inactive", "to": "active", "trigger": "reactivate"}
          ],
          "triggers": ["activate", "deactivate", "reactivate"]
        },
        "bi_features": {
          "available_kpis": [
            "total_employees",
            "avg_salary",
            "department_distribution"
          ],
          "reports": [
            "employee_list",
            "salary_report",
            "department_report"
          ],
          "dashboards": [
            "hr_overview",
            "employee_analytics"
          ]
        },
        "capabilities": {
          "crud_operations": true,
          "workflow_enabled": true,
          "reporting_enabled": true,
          "api_enabled": true
        }
      },
      "sale.order": {
        "name": "Sales Order",
        "description": "Sales order management",
        "table": "sale_order",
        "installed": true,
        "fields": {
          "id": {
            "type": "integer",
            "required": true,
            "readonly": true
          },
          "name": {
            "type": "char",
            "required": true,
            "size": 255
          },
          "partner_id": {
            "type": "many2one",
            "relation": "res.partner",
            "required": true
          },
          "amount_total": {
            "type": "monetary",
            "required": false
          },
          "state": {
            "type": "selection",
            "selection": [
              ["draft", "Draft"],
              ["sent", "Sent"],
              ["sale", "Sales Order"],
              ["done", "Done"],
              ["cancel", "Cancelled"]
            ],
            "default": "draft"
          }
        },
        "workflows": {
          "available_states": ["draft", "sent", "sale", "done", "cancel"],
          "transitions": [
            {"from": "draft", "to": "sent", "trigger": "send"},
            {"from": "sent", "to": "sale", "trigger": "confirm"},
            {"from": "sale", "to": "done", "trigger": "complete"},
            {"from": "draft", "to": "cancel", "trigger": "cancel"},
            {"from": "sent", "to": "cancel", "trigger": "cancel"}
          ]
        }
      }
    },
    "total_models": 150,
    "installed_models": 120,
    "available_models": 30,
    "domains": {
      "hr": 25,
      "sales": 20,
      "accounting": 15,
      "inventory": 30,
      "manufacturing": 20,
      "purchasing": 15,
      "project": 10,
      "other": 15
    }
  },
  "message": "Models discovered successfully"
}
```

### **Get Model Details**

Get detailed information about a specific model including fields, relationships, and capabilities.

```http
GET /api/profile/models/{model_name}/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `db` | string | Yes | - | Database name |
| `include_relationships` | boolean | No | `true` | Include relationship analysis |
| `include_constraints` | boolean | No | `true` | Include constraint information |
| `include_indexes` | boolean | No | `false` | Include database indexes |

#### **Example Request**

```bash
curl -X GET "http://localhost:8001/api/profile/models/hr.employee/" \
  -H "Authorization: Bearer <your_token>" \
  -G \
  -d "db=fbs_rental_db" \
  -d "include_relationships=true"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "model": "hr.employee",
    "name": "Employee",
    "description": "Employee management",
    "table": "hr_employee",
    "installed": true,
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
    "relationships": {
      "many2one": [
        {
          "field": "department_id",
          "target_model": "hr.department",
          "target_field": "id",
          "ondelete": "restrict"
        },
        {
          "field": "manager_id",
          "target_model": "hr.employee",
          "target_field": "id",
          "ondelete": "set null"
        }
      ],
      "one2many": [
        {
          "field": "subordinate_ids",
          "target_model": "hr.employee",
          "target_field": "manager_id"
        }
      ],
      "many2many": [
        {
          "field": "skill_ids",
          "target_model": "hr.skill",
          "relation_table": "hr_employee_skill_rel"
        }
      ]
    },
    "constraints": [
      {
        "type": "unique",
        "fields": ["email"],
        "message": "Email must be unique"
      },
      {
        "type": "check",
        "condition": "salary >= 0",
        "message": "Salary must be positive"
      }
    ],
    "indexes": [
      {
        "name": "hr_employee_name_idx",
        "fields": ["name"],
        "type": "btree"
      },
      {
        "name": "hr_employee_email_idx",
        "fields": ["email"],
        "type": "btree",
        "unique": true
      }
    ],
    "capabilities": {
      "crud_operations": true,
      "workflow_enabled": true,
      "reporting_enabled": true,
      "api_enabled": true,
      "search_enabled": true,
      "export_enabled": true
    }
  }
}
```

## 🔄 Workflow Discovery

### **Discover Model Workflows**

Discover available workflows, state machines, and transitions for a specific model.

```http
GET /api/profile/workflows/{model_name}/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `db` | string | Yes | - | Database name |
| `include_triggers` | boolean | No | `true` | Include trigger information |
| `include_actions` | boolean | No | `true` | Include automated actions |
| `include_validation` | boolean | No | `true` | Include validation rules |

#### **Example Request**

```bash
curl -X GET "http://localhost:8001/api/profile/workflows/sale.order/" \
  -H "Authorization: Bearer <your_token>" \
  -G \
  -d "db=fbs_rental_db"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "model": "sale.order",
    "workflow_name": "sales_order_workflow",
    "states": [
      {
        "name": "draft",
        "description": "Draft Order",
        "color": "#6c757d",
        "is_initial": true,
        "is_final": false
      },
      {
        "name": "sent",
        "description": "Order Sent",
        "color": "#17a2b8",
        "is_initial": false,
        "is_final": false
      },
      {
        "name": "sale",
        "description": "Sales Order",
        "color": "#28a745",
        "is_initial": false,
        "is_final": false
      },
      {
        "name": "done",
        "description": "Order Done",
        "color": "#6f42c1",
        "is_initial": false,
        "is_final": true
      },
      {
        "name": "cancel",
        "description": "Cancelled",
        "color": "#dc3545",
        "is_initial": false,
        "is_final": true
      }
    ],
    "transitions": [
      {
        "from": "draft",
        "to": "sent",
        "trigger": "send",
        "description": "Send order to customer",
        "conditions": [
          "partner_id is set",
          "order_line is not empty"
        ],
        "actions": [
          "send_email",
          "create_invoice"
        ]
      },
      {
        "from": "sent",
        "to": "sale",
        "trigger": "confirm",
        "description": "Confirm sales order",
        "conditions": [
          "customer_confirmed = true"
        ],
        "actions": [
          "reserve_stock",
          "create_delivery"
        ]
      },
      {
        "from": "sale",
        "to": "done",
        "trigger": "complete",
        "description": "Complete order",
        "conditions": [
          "delivery_confirmed = true",
          "payment_received = true"
        ],
        "actions": [
          "update_inventory",
          "send_completion_email"
        ]
      }
    ],
    "triggers": [
      {
        "name": "send",
        "description": "Send order to customer",
        "required_fields": ["partner_id", "order_line"],
        "validation_rules": [
          "partner_id must be valid",
          "order_line must not be empty"
        ]
      },
      {
        "name": "confirm",
        "description": "Confirm sales order",
        "required_fields": ["customer_confirmed"],
        "validation_rules": [
          "customer_confirmed must be true"
        ]
      },
      {
        "name": "complete",
        "description": "Complete order",
        "required_fields": ["delivery_confirmed", "payment_received"],
        "validation_rules": [
          "delivery_confirmed must be true",
          "payment_received must be true"
        ]
      }
    ],
    "validation_rules": [
      {
        "name": "check_partner",
        "condition": "partner_id.active = true",
        "message": "Partner must be active"
      },
      {
        "name": "check_order_lines",
        "condition": "len(order_line) > 0",
        "message": "Order must have at least one line"
      },
      {
        "name": "check_amount",
        "condition": "amount_total > 0",
        "message": "Order total must be positive"
      }
    ],
    "automated_actions": [
      {
        "name": "send_email",
        "trigger": "state_changed",
        "conditions": ["new_state = 'sent'"],
        "action": "send_order_email"
      },
      {
        "name": "create_invoice",
        "trigger": "state_changed",
        "conditions": ["new_state = 'sale'"],
        "action": "create_customer_invoice"
      },
      {
        "name": "reserve_stock",
        "trigger": "state_changed",
        "conditions": ["new_state = 'sale'"],
        "action": "reserve_product_stock"
      }
    ]
  }
}
```

### **List All Workflows**

Get a comprehensive list of all available workflows in the system.

```http
GET /api/profile/workflows/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "workflows": [
      {
        "model": "sale.order",
        "name": "Sales Order Workflow",
        "states_count": 5,
        "transitions_count": 8,
        "is_active": true
      },
      {
        "model": "hr.employee",
        "name": "Employee Workflow",
        "states_count": 3,
        "transitions_count": 4,
        "is_active": true
      },
      {
        "model": "account.invoice",
        "name": "Invoice Workflow",
        "states_count": 4,
        "transitions_count": 6,
        "is_active": true
      }
    ],
    "total_workflows": 25,
    "active_workflows": 20,
    "inactive_workflows": 5
  }
}
```

## 📈 Business Intelligence Discovery

### **Discover BI Features**

Discover available business intelligence features, KPIs, reports, and dashboards for a model.

```http
GET /api/profile/bi/{model_name}/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `db` | string | Yes | - | Database name |
| `include_kpis` | boolean | No | `true` | Include KPI definitions |
| `include_reports` | boolean | No | `true` | Include report definitions |
| `include_dashboards` | boolean | No | `true` | Include dashboard definitions |

#### **Example Request**

```bash
curl -X GET "http://localhost:8001/api/profile/bi/sale.order/" \
  -H "Authorization: Bearer <your_token>" \
  -G \
  -d "db=fbs_rental_db"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "model": "sale.order",
    "kpis": [
      {
        "name": "total_sales",
        "description": "Total Sales Amount",
        "calculation": "sum(amount_total)",
        "unit": "currency",
        "refresh_interval": "daily",
        "trend": "up",
        "target": 100000
      },
      {
        "name": "order_count",
        "description": "Number of Orders",
        "calculation": "count(id)",
        "unit": "count",
        "refresh_interval": "daily",
        "trend": "up",
        "target": 50
      },
      {
        "name": "avg_order_value",
        "description": "Average Order Value",
        "calculation": "avg(amount_total)",
        "unit": "currency",
        "refresh_interval": "daily",
        "trend": "stable",
        "target": 2000
      },
      {
        "name": "conversion_rate",
        "description": "Order Conversion Rate",
        "calculation": "count(state='sale') / count(state='sent') * 100",
        "unit": "percentage",
        "refresh_interval": "daily",
        "trend": "up",
        "target": 75
      }
    ],
    "reports": [
      {
        "name": "sales_summary",
        "description": "Sales Summary Report",
        "type": "summary",
        "filters": [
          "date_range",
          "partner_category",
          "salesperson"
        ],
        "columns": [
          "order_date",
          "partner_name",
          "amount_total",
          "state"
        ],
        "grouping": ["partner_category", "month"],
        "chart_types": ["bar", "line", "pie"]
      },
      {
        "name": "sales_detailed",
        "description": "Detailed Sales Report",
        "type": "detailed",
        "filters": [
          "date_range",
          "partner",
          "product_category"
        ],
        "columns": [
          "order_id",
          "order_date",
          "partner_name",
          "product_name",
          "quantity",
          "unit_price",
          "amount_total"
        ],
        "export_formats": ["pdf", "excel", "csv"]
      },
      {
        "name": "sales_trends",
        "description": "Sales Trends Analysis",
        "type": "trend",
        "filters": [
          "date_range",
          "product_category"
        ],
        "metrics": [
          "total_sales",
          "order_count",
          "avg_order_value"
        ],
        "time_periods": ["daily", "weekly", "monthly", "quarterly"]
      }
    ],
    "dashboards": [
      {
        "name": "sales_overview",
        "description": "Sales Overview Dashboard",
        "widgets": [
          {
            "name": "total_sales_kpi",
            "type": "kpi",
            "position": {"x": 0, "y": 0, "w": 3, "h": 2},
            "kpi_name": "total_sales"
          },
          {
            "name": "order_count_kpi",
            "type": "kpi",
            "position": {"x": 3, "y": 0, "w": 3, "h": 2},
            "kpi_name": "order_count"
          },
          {
            "name": "sales_trend_chart",
            "type": "chart",
            "position": {"x": 0, "y": 2, "w": 6, "h": 4},
            "chart_type": "line",
            "data_source": "sales_trends_report"
          },
          {
            "name": "top_customers_table",
            "type": "table",
            "position": {"x": 6, "y": 2, "w": 6, "h": 4},
            "data_source": "top_customers_report"
          }
        ],
        "refresh_interval": "5 minutes",
        "is_public": false
      },
      {
        "name": "sales_analytics",
        "description": "Sales Analytics Dashboard",
        "widgets": [
          {
            "name": "sales_by_category",
            "type": "chart",
            "position": {"x": 0, "y": 0, "w": 6, "h": 4},
            "chart_type": "pie",
            "data_source": "sales_by_category_report"
          },
          {
            "name": "sales_by_region",
            "type": "chart",
            "position": {"x": 6, "y": 0, "w": 6, "h": 4},
            "chart_type": "bar",
            "data_source": "sales_by_region_report"
          },
          {
            "name": "sales_performance_table",
            "type": "table",
            "position": {"x": 0, "y": 4, "w": 12, "h": 4},
            "data_source": "sales_performance_report"
          }
        ],
        "refresh_interval": "15 minutes",
        "is_public": true
      }
    ],
    "metrics": [
      {
        "name": "revenue_growth",
        "description": "Revenue Growth Rate",
        "calculation": "(current_period - previous_period) / previous_period * 100",
        "unit": "percentage",
        "time_period": "monthly"
      },
      {
        "name": "customer_lifetime_value",
        "description": "Customer Lifetime Value",
        "calculation": "sum(amount_total) / count(distinct partner_id)",
        "unit": "currency",
        "time_period": "quarterly"
      }
    ]
  }
}
```

### **List All BI Features**

Get a comprehensive list of all available BI features across all models.

```http
GET /api/profile/bi/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "total_kpis": 150,
    "total_reports": 75,
    "total_dashboards": 25,
    "models_with_bi": 45,
    "bi_features_by_domain": {
      "sales": {
        "kpis": 25,
        "reports": 15,
        "dashboards": 5
      },
      "accounting": {
        "kpis": 20,
        "reports": 12,
        "dashboards": 4
      },
      "hr": {
        "kpis": 15,
        "reports": 8,
        "dashboards": 3
      },
      "inventory": {
        "kpis": 18,
        "reports": 10,
        "dashboards": 4
      }
    }
  }
}
```

## 🔍 Capability Analysis

### **Analyze Model Capabilities**

Perform a comprehensive analysis of a model's capabilities and potential use cases.

```http
GET /api/profile/capabilities/{model_name}/
```

#### **Example Request**

```bash
curl -X GET "http://localhost:8001/api/profile/capabilities/hr.employee/" \
  -H "Authorization: Bearer <your_token>" \
  -G \
  -d "db=fbs_rental_db"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "model": "hr.employee",
    "analysis": {
      "crud_capabilities": {
        "can_create": true,
        "can_read": true,
        "can_update": true,
        "can_delete": true,
        "bulk_operations": true
      },
      "workflow_capabilities": {
        "has_state_machine": true,
        "state_field": "state",
        "available_states": 3,
        "available_transitions": 4,
        "automated_actions": 2
      },
      "reporting_capabilities": {
        "has_kpis": true,
        "kpi_count": 8,
        "has_reports": true,
        "report_count": 5,
        "has_dashboards": true,
        "dashboard_count": 2
      },
      "integration_capabilities": {
        "api_enabled": true,
        "webhook_support": true,
        "export_formats": ["pdf", "excel", "csv"],
        "import_formats": ["excel", "csv"]
      },
      "security_capabilities": {
        "access_control": true,
        "field_level_security": true,
        "record_level_security": true,
        "audit_trail": true
      },
      "performance_capabilities": {
        "indexed_fields": 5,
        "cached_queries": true,
        "optimized_searches": true,
        "bulk_operations": true
      }
    },
    "use_cases": [
      {
        "name": "employee_management",
        "description": "Complete employee lifecycle management",
        "complexity": "medium",
        "estimated_effort": "2-3 weeks"
      },
      {
        "name": "org_chart",
        "description": "Organizational chart visualization",
        "complexity": "low",
        "estimated_effort": "1 week"
      },
      {
        "name": "hr_analytics",
        "description": "HR analytics and reporting",
        "complexity": "high",
        "estimated_effort": "3-4 weeks"
      }
    ],
    "recommendations": [
      {
        "type": "optimization",
        "title": "Add salary range validation",
        "description": "Implement validation to ensure salary is within acceptable range",
        "priority": "medium"
      },
      {
        "type": "feature",
        "title": "Add employee skills tracking",
        "description": "Implement many2many relationship with skills model",
        "priority": "high"
      },
      {
        "type": "reporting",
        "title": "Create turnover analysis report",
        "description": "Add report to analyze employee turnover trends",
        "priority": "medium"
      }
    ]
  }
}
```

## 📊 Discovery Summary

### **Get Discovery Summary**

Get a comprehensive summary of all discovery results for a database.

```http
GET /api/profile/summary/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `db` | string | Yes | - | Database name |
| `include_statistics` | boolean | No | `true` | Include detailed statistics |
| `include_recommendations` | boolean | No | `true` | Include recommendations |

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "database": "fbs_rental_db",
    "discovery_summary": {
      "models": {
        "total": 150,
        "installed": 120,
        "available": 30,
        "with_workflows": 45,
        "with_bi": 60
      },
      "workflows": {
        "total": 25,
        "active": 20,
        "inactive": 5,
        "complex_workflows": 8
      },
      "bi_features": {
        "total_kpis": 150,
        "total_reports": 75,
        "total_dashboards": 25,
        "automated_reports": 30
      },
      "capabilities": {
        "crud_enabled": 120,
        "api_enabled": 100,
        "export_enabled": 80,
        "import_enabled": 60
      }
    },
    "domain_breakdown": {
      "hr": {
        "models": 25,
        "workflows": 8,
        "kpis": 20,
        "reports": 12
      },
      "sales": {
        "models": 20,
        "workflows": 6,
        "kpis": 25,
        "reports": 15
      },
      "accounting": {
        "models": 15,
        "workflows": 4,
        "kpis": 18,
        "reports": 10
      }
    },
    "recommendations": [
      {
        "category": "performance",
        "title": "Optimize slow queries",
        "description": "Add indexes to frequently queried fields",
        "impact": "high",
        "effort": "medium"
      },
      {
        "category": "security",
        "title": "Implement field-level security",
        "description": "Add field-level access control for sensitive data",
        "impact": "high",
        "effort": "high"
      },
      {
        "category": "functionality",
        "title": "Add missing workflows",
        "description": "Implement workflows for models without state management",
        "impact": "medium",
        "effort": "medium"
      }
    ],
    "last_updated": "2024-01-15T10:30:00Z",
    "next_refresh": "2024-01-15T11:30:00Z"
  }
}
```

## 🔗 Related Documentation

- **[01. API Overview](./01_overview.md)** - Introduction and architecture
- **[02. Core Operations](./02_core_operations.md)** - Basic CRUD operations
- **[04. Authentication](./04_authentication.md)** - Security and authentication
- **[05. Business Endpoints](./05_business_endpoints.md)** - Domain-specific APIs
- **[06. Business Intelligence](./06_business_intelligence.md)** - Analytics and reporting 