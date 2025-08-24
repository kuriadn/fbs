# FBS App Integration Guide

## Overview

The **FBS App** (`fbs_app`) is the core business suite that provides MSME management, business intelligence, workflows, compliance, and accounting capabilities.

## Installation

```python
# settings.py
INSTALLED_APPS = [
    'fbs_app',
]

FBS_APP = {
    'ENABLE_MSME_FEATURES': True,
    'ENABLE_BI_FEATURES': True,
    'ENABLE_WORKFLOW_FEATURES': True,
    'ENABLE_COMPLIANCE_FEATURES': True,
    'ENABLE_ACCOUNTING_FEATURES': True,
    'CACHE_ENABLED': True,
    'ODOO_BASE_URL': 'http://localhost:8069',
    'DATABASE_USER': 'your_odoo_user',
    'DATABASE_PASSWORD': 'your_odoo_password',
}

DATABASE_ROUTERS = [
    'fbs_app.routers.FBSDatabaseRouter',
]
```

## Core Usage

```python
from fbs_app.interfaces import FBSInterface

# Initialize with solution context
fbs = FBSInterface('your_solution_name')

# Check system status
solution_info = fbs.get_solution_info()
health = fbs.get_system_health()
odoo_available = fbs.is_odoo_available()
```

## MSME Business Management

```python
# Setup business
setup_result = fbs.msme.setup_business(
    business_type='retail',
    config={'business_name': 'My Store', 'employees': 5}
)

# Get dashboard and KPIs
dashboard = fbs.msme.get_dashboard()
kpis = fbs.msme.calculate_kpis()
compliance = fbs.msme.get_compliance_status()
```

## Business Intelligence

```python
# Create dashboard
dashboard = fbs.bi.create_dashboard({
    'name': 'Sales Dashboard',
    'dashboard_type': 'sales',
    'description': 'Sales performance overview'
})

# Create KPI
kpi = fbs.bi.create_kpi({
    'name': 'Monthly Revenue',
    'kpi_type': 'financial',
    'calculation_method': 'sum(revenue)',
    'target_value': 500000.0
})

# Generate reports
report = fbs.bi.generate_report(report_id, {'period': '2024-01'})
```

## Workflow Management

```python
# Create workflow
workflow_def = fbs.workflows.create_workflow_definition({
    'name': 'Purchase Approval',
    'workflow_type': 'approval',
    'workflow_data': {'steps': ['submit', 'review', 'approve']}
})

# Start workflow
instance = fbs.workflows.start_workflow(
    workflow_definition_id=workflow_def['id'],
    initial_data={'amount': 5000, 'vendor': 'ABC Supplies'}
)

# Create approval request
approval = fbs.workflows.create_approval_request({
    'request_type': 'purchase',
    'title': 'Purchase Order Approval',
    'amount': 5000
})
```

## Odoo Integration

```python
# Discover models
models = fbs.odoo.discover_models()
fields = fbs.odoo.discover_fields('res.partner')

# CRUD operations
partners = fbs.odoo.get_records('res.partner', filters=[('is_company', '=', True)])
partner = fbs.odoo.get_record('res.partner', record_id=123)
new_partner = fbs.odoo.create_record('res.partner', {'name': 'New Company'})
```

## Virtual Fields

```python
# Set custom field
fbs.fields.set_custom_field(
    model_name='res.partner',
    record_id=123,
    field_name='customer_segment',
    field_value='premium'
)

# Merge Odoo with custom data
merged_data = fbs.fields.merge_odoo_with_custom('res.partner', 123)
```

## Error Handling

```python
try:
    result = fbs.msme.setup_business('retail', config_data)
    if result['success']:
        print(f"Setup completed: {result['data']}")
    else:
        print(f"Setup failed: {result['error']}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## Security Features

- **Solution Isolation**: Each solution has isolated data through `solution_name`
- **Database Routing**: Automatic routing prevents cross-solution access
- **Authentication**: Handshake-based API authentication
- **Request Logging**: Comprehensive audit trails
