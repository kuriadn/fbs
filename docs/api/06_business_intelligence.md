# 06. Business Intelligence API 📊

## Overview

The Business Intelligence API provides comprehensive analytics, reporting, and dashboard capabilities. This API enables real-time data analysis, KPI tracking, and automated report generation across all business domains.

## 🔐 Authentication

All BI endpoints require JWT authentication:

```http
Authorization: Bearer <your_jwt_token>
```

## 📈 Key Performance Indicators (KPIs)

### **Get KPI Data**

Retrieve KPI data for specific metrics.

```http
GET /api/bi/kpis/{kpi_name}/
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | No | - | Start date (ISO format) |
| `end_date` | string | No | - | End date (ISO format) |
| `period` | string | No | `daily` | Time period (hourly, daily, weekly, monthly) |
| `filters` | string | No | - | JSON filters |

#### **Example Request**

```bash
curl -X GET "http://localhost:8001/api/bi/kpis/total_sales/" \
  -H "Authorization: Bearer <your_token>" \
  -G \
  -d "start_date=2024-01-01" \
  -d "end_date=2024-01-31" \
  -d "period=daily"
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "kpi": {
      "name": "total_sales",
      "display_name": "Total Sales",
      "description": "Total sales amount for the period",
      "unit": "currency",
      "calculation": "sum(amount_total)"
    },
    "current_value": 125000,
    "previous_value": 110000,
    "change_percentage": 13.64,
    "trend": "up",
    "target": 100000,
    "target_achievement": 125.0,
    "time_series": [
      {
        "date": "2024-01-01",
        "value": 3500,
        "target": 3000
      },
      {
        "date": "2024-01-02",
        "value": 4200,
        "target": 3000
      }
    ],
    "breakdown": {
      "by_category": [
        {
          "category": "Electronics",
          "value": 45000,
          "percentage": 36.0
        },
        {
          "category": "Clothing",
          "value": 35000,
          "percentage": 28.0
        }
      ],
      "by_region": [
        {
          "region": "North",
          "value": 50000,
          "percentage": 40.0
        },
        {
          "region": "South",
          "value": 40000,
          "percentage": 32.0
        }
      ]
    }
  }
}
```

### **List Available KPIs**

Get all available KPIs in the system.

```http
GET /api/bi/kpis/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "kpis": [
      {
        "name": "total_sales",
        "display_name": "Total Sales",
        "description": "Total sales amount",
        "unit": "currency",
        "category": "sales",
        "refresh_interval": "hourly",
        "is_active": true
      },
      {
        "name": "order_count",
        "display_name": "Order Count",
        "description": "Number of orders",
        "unit": "count",
        "category": "sales",
        "refresh_interval": "hourly",
        "is_active": true
      },
      {
        "name": "avg_order_value",
        "display_name": "Average Order Value",
        "description": "Average value per order",
        "unit": "currency",
        "category": "sales",
        "refresh_interval": "daily",
        "is_active": true
      },
      {
        "name": "conversion_rate",
        "display_name": "Conversion Rate",
        "description": "Order conversion rate",
        "unit": "percentage",
        "category": "sales",
        "refresh_interval": "daily",
        "is_active": true
      }
    ],
    "categories": [
      {
        "name": "sales",
        "display_name": "Sales",
        "kpi_count": 8
      },
      {
        "name": "inventory",
        "display_name": "Inventory",
        "kpi_count": 5
      },
      {
        "name": "customer",
        "display_name": "Customer",
        "kpi_count": 6
      }
    ]
  }
}
```

## 📋 Reports

### **Generate Report**

Generate a custom report with specified parameters.

```http
POST /api/bi/reports/generate/
```

#### **Request Body**

```json
{
  "report_type": "sales_summary",
  "parameters": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "group_by": ["category", "region"],
    "filters": {
      "status": ["confirmed", "shipped"],
      "min_amount": 100
    },
    "sort_by": "amount_total",
    "sort_order": "desc",
    "limit": 100
  },
  "format": "json",
  "include_charts": true
}
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "report": {
      "id": "rep_123456789",
      "type": "sales_summary",
      "name": "Sales Summary Report",
      "generated_at": "2024-01-15T10:30:00Z",
      "parameters": {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
      },
      "summary": {
        "total_sales": 125000,
        "total_orders": 250,
        "avg_order_value": 500,
        "top_category": "Electronics",
        "top_region": "North"
      },
      "data": [
        {
          "category": "Electronics",
          "region": "North",
          "sales": 25000,
          "orders": 50,
          "avg_order": 500
        },
        {
          "category": "Electronics",
          "region": "South",
          "sales": 20000,
          "orders": 40,
          "avg_order": 500
        }
      ],
      "charts": {
        "sales_by_category": {
          "type": "pie",
          "data": [
            {"label": "Electronics", "value": 45000},
            {"label": "Clothing", "value": 35000}
          ]
        },
        "sales_trend": {
          "type": "line",
          "data": [
            {"date": "2024-01-01", "value": 3500},
            {"date": "2024-01-02", "value": 4200}
          ]
        }
      }
    }
  }
}
```

### **Get Report Template**

Get available report templates.

```http
GET /api/bi/reports/templates/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "name": "sales_summary",
        "display_name": "Sales Summary Report",
        "description": "Comprehensive sales analysis",
        "category": "sales",
        "parameters": [
          {
            "name": "start_date",
            "type": "date",
            "required": true,
            "description": "Report start date"
          },
          {
            "name": "end_date",
            "type": "date",
            "required": true,
            "description": "Report end date"
          },
          {
            "name": "group_by",
            "type": "array",
            "required": false,
            "options": ["category", "region", "salesperson"],
            "description": "Grouping options"
          }
        ],
        "available_formats": ["json", "pdf", "excel", "csv"],
        "refresh_interval": "daily"
      },
      {
        "name": "inventory_status",
        "display_name": "Inventory Status Report",
        "description": "Current inventory levels and status",
        "category": "inventory",
        "parameters": [
          {
            "name": "category",
            "type": "string",
            "required": false,
            "description": "Product category filter"
          },
          {
            "name": "low_stock_threshold",
            "type": "number",
            "required": false,
            "default": 10,
            "description": "Low stock threshold"
          }
        ],
        "available_formats": ["json", "pdf", "excel"],
        "refresh_interval": "hourly"
      }
    ]
  }
}
```

### **Schedule Report**

Schedule a report for automatic generation.

```http
POST /api/bi/reports/schedule/
```

#### **Request Body**

```json
{
  "report_type": "sales_summary",
  "name": "Monthly Sales Report",
  "schedule": {
    "frequency": "monthly",
    "day_of_month": 1,
    "time": "09:00",
    "timezone": "America/New_York"
  },
  "parameters": {
    "start_date": "{{previous_month_start}}",
    "end_date": "{{previous_month_end}}",
    "group_by": ["category", "region"]
  },
  "recipients": [
    {
      "email": "manager@company.com",
      "format": "pdf"
    },
    {
      "email": "analytics@company.com",
      "format": "excel"
    }
  ],
  "is_active": true
}
```

## 📊 Dashboards

### **Get Dashboard**

Retrieve dashboard data and configuration.

```http
GET /api/bi/dashboards/{dashboard_name}/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "dashboard": {
      "name": "sales_overview",
      "display_name": "Sales Overview Dashboard",
      "description": "Real-time sales performance overview",
      "layout": {
        "columns": 12,
        "rows": 6
      },
      "widgets": [
        {
          "id": "total_sales_kpi",
          "type": "kpi",
          "title": "Total Sales",
          "position": {"x": 0, "y": 0, "w": 3, "h": 2},
          "data": {
            "kpi_name": "total_sales",
            "current_value": 125000,
            "previous_value": 110000,
            "change_percentage": 13.64,
            "trend": "up"
          },
          "config": {
            "show_target": true,
            "show_trend": true,
            "color_scheme": "green"
          }
        },
        {
          "id": "sales_trend_chart",
          "type": "chart",
          "title": "Sales Trend",
          "position": {"x": 3, "y": 0, "w": 6, "h": 3},
          "data": {
            "chart_type": "line",
            "series": [
              {
                "name": "Sales",
                "data": [
                  {"date": "2024-01-01", "value": 3500},
                  {"date": "2024-01-02", "value": 4200}
                ]
              }
            ]
          },
          "config": {
            "show_legend": true,
            "show_grid": true,
            "y_axis_label": "Sales Amount"
          }
        },
        {
          "id": "top_products_table",
          "type": "table",
          "title": "Top Products",
          "position": {"x": 9, "y": 0, "w": 3, "h": 3},
          "data": {
            "columns": [
              {"name": "product", "label": "Product"},
              {"name": "sales", "label": "Sales"},
              {"name": "quantity", "label": "Quantity"}
            ],
            "rows": [
              {
                "product": "Wireless Headphones",
                "sales": 15000,
                "quantity": 150
              },
              {
                "product": "Smartphone",
                "sales": 12000,
                "quantity": 60
              }
            ]
          },
          "config": {
            "sortable": true,
            "paginated": false,
            "max_rows": 10
          }
        }
      ],
      "refresh_interval": "5 minutes",
      "last_updated": "2024-01-15T10:30:00Z",
      "is_public": false,
      "permissions": {
        "view": ["sales_manager", "analyst"],
        "edit": ["sales_manager"]
      }
    }
  }
}
```

### **List Dashboards**

Get all available dashboards.

```http
GET /api/bi/dashboards/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "dashboards": [
      {
        "name": "sales_overview",
        "display_name": "Sales Overview",
        "description": "Real-time sales performance",
        "category": "sales",
        "widget_count": 8,
        "refresh_interval": "5 minutes",
        "is_public": false,
        "last_updated": "2024-01-15T10:30:00Z"
      },
      {
        "name": "inventory_analytics",
        "display_name": "Inventory Analytics",
        "description": "Inventory performance and trends",
        "category": "inventory",
        "widget_count": 6,
        "refresh_interval": "15 minutes",
        "is_public": true,
        "last_updated": "2024-01-15T10:15:00Z"
      }
    ],
    "categories": [
      {
        "name": "sales",
        "display_name": "Sales",
        "dashboard_count": 3
      },
      {
        "name": "inventory",
        "display_name": "Inventory",
        "dashboard_count": 2
      },
      {
        "name": "customer",
        "display_name": "Customer",
        "dashboard_count": 2
      }
    ]
  }
}
```

### **Create Dashboard**

Create a new custom dashboard.

```http
POST /api/bi/dashboards/
```

#### **Request Body**

```json
{
  "name": "custom_analytics",
  "display_name": "Custom Analytics Dashboard",
  "description": "Custom analytics dashboard for specific needs",
  "layout": {
    "columns": 12,
    "rows": 6
  },
  "widgets": [
    {
      "type": "kpi",
      "title": "Custom KPI",
      "position": {"x": 0, "y": 0, "w": 3, "h": 2},
      "config": {
        "kpi_name": "custom_metric",
        "show_target": true,
        "show_trend": true
      }
    },
    {
      "type": "chart",
      "title": "Custom Chart",
      "position": {"x": 3, "y": 0, "w": 6, "h": 3},
      "config": {
        "chart_type": "bar",
        "data_source": "custom_query",
        "show_legend": true
      }
    }
  ],
  "refresh_interval": "10 minutes",
  "is_public": false,
  "permissions": {
    "view": ["analyst"],
    "edit": ["analyst"]
  }
}
```

## 📊 Analytics Engine

### **Custom Analytics Query**

Execute custom analytics queries.

```http
POST /api/bi/analytics/query/
```

#### **Request Body**

```json
{
  "query": {
    "select": [
      "category",
      "sum(amount_total) as total_sales",
      "count(*) as order_count"
    ],
    "from": "sale.order",
    "where": [
      "state in ('confirmed', 'shipped')",
      "create_date >= '2024-01-01'",
      "create_date <= '2024-01-31'"
    ],
    "group_by": ["category"],
    "order_by": ["total_sales desc"],
    "limit": 10
  },
  "format": "json",
  "include_metadata": true
}
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "query_id": "qry_123456789",
    "execution_time": "0.15s",
    "result": {
      "columns": [
        {"name": "category", "type": "string"},
        {"name": "total_sales", "type": "decimal"},
        {"name": "order_count", "type": "integer"}
      ],
      "rows": [
        {
          "category": "Electronics",
          "total_sales": 45000.00,
          "order_count": 90
        },
        {
          "category": "Clothing",
          "total_sales": 35000.00,
          "order_count": 175
        }
      ],
      "total_rows": 2,
      "summary": {
        "total_sales": 80000.00,
        "total_orders": 265
      }
    },
    "metadata": {
      "query_hash": "abc123def456",
      "cached": false,
      "cache_ttl": 300
    }
  }
}
```

### **Get Analytics Schema**

Get the analytics schema for available data sources.

```http
GET /api/bi/analytics/schema/
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "tables": [
      {
        "name": "sale.order",
        "display_name": "Sales Orders",
        "description": "Sales order data",
        "columns": [
          {
            "name": "id",
            "type": "integer",
            "description": "Order ID"
          },
          {
            "name": "amount_total",
            "type": "decimal",
            "description": "Total order amount"
          },
          {
            "name": "state",
            "type": "string",
            "description": "Order status"
          },
          {
            "name": "create_date",
            "type": "datetime",
            "description": "Order creation date"
          }
        ],
        "relationships": [
          {
            "table": "sale.order.line",
            "type": "one_to_many",
            "foreign_key": "order_id"
          }
        ]
      }
    ],
    "functions": [
      {
        "name": "sum",
        "description": "Sum of values",
        "syntax": "sum(column_name)"
      },
      {
        "name": "count",
        "description": "Count of records",
        "syntax": "count(*)"
      },
      {
        "name": "avg",
        "description": "Average of values",
        "syntax": "avg(column_name)"
      }
    ]
  }
}
```

## 📈 Data Visualization

### **Generate Chart**

Generate chart data for visualization.

```http
POST /api/bi/charts/generate/
```

#### **Request Body**

```json
{
  "chart_type": "line",
  "title": "Sales Trend",
  "data_source": {
    "query": {
      "select": ["create_date", "sum(amount_total)"],
      "from": "sale.order",
      "where": ["state = 'confirmed'"],
      "group_by": ["date(create_date)"],
      "order_by": ["create_date"]
    }
  },
  "config": {
    "x_axis": {
      "label": "Date",
      "type": "datetime"
    },
    "y_axis": {
      "label": "Sales Amount",
      "type": "currency"
    },
    "show_legend": true,
    "show_grid": true,
    "colors": ["#007bff", "#28a745"]
  }
}
```

#### **Example Response**

```json
{
  "success": true,
  "data": {
    "chart": {
      "id": "chart_123456789",
      "type": "line",
      "title": "Sales Trend",
      "data": {
        "labels": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "datasets": [
          {
            "label": "Sales",
            "data": [3500, 4200, 3800],
            "borderColor": "#007bff",
            "backgroundColor": "rgba(0, 123, 255, 0.1)"
          }
        ]
      },
      "config": {
        "responsive": true,
        "maintainAspectRatio": false
      },
      "generated_at": "2024-01-15T10:30:00Z"
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