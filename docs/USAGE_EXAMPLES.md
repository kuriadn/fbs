# FBS App Usage Examples

This document demonstrates how to use the FBS app capabilities through proper service interfaces instead of API endpoints.

## Overview

The FBS app provides comprehensive business capabilities through clean service interfaces that can be used directly in Django views, management commands, or other parts of your application.

## Basic Usage

### 1. Initialize FBS Interface

```python
from fbs_app.interfaces import FBSInterface

# Initialize with solution context
fbs = FBSInterface('solution_name')

# Get solution information
info = fbs.get_solution_info()
print(f"Solution: {info['solution_name']}")
print(f"Capabilities: {info['capabilities']}")

# Get system health
health = fbs.get_system_health()
print(f"System status: {health['status']}")
```

### 2. MSME Business Management

```python
# Setup MSME business
business_config = {
    'solution_name': 'my_solution',
    'business_type': 'retail',
    'current_step': 'setup',
    'total_steps': 5,
    'progress': 0.0
}

result = fbs.msme.setup_business('retail', business_config)
if result['success']:
    print("Business setup completed successfully")

# Get business dashboard
dashboard = fbs.msme.get_dashboard()
print(f"Business overview: {dashboard}")

# Calculate KPIs
kpis = fbs.msme.calculate_kpis()
print(f"Current KPIs: {kpis}")

# Get compliance status
compliance = fbs.msme.get_compliance_status()
print(f"Compliance status: {compliance}")

# Update business profile
profile_update = {
    'solution_name': 'my_solution',
    'business_type': 'retail',
    'current_step': 'marketing',
    'total_steps': 5,
    'progress': 60.0
}
result = fbs.msme.update_business_profile(profile_update)

# Get business templates
templates = fbs.msme.get_business_templates()
print(f"Available templates: {templates}")

# Apply business template
result = fbs.msme.apply_business_template('retail_starter')
```

### 3. Business Intelligence & Analytics

```python
# Create dashboard
dashboard_data = {
    'name': 'Sales Dashboard',
    'dashboard_type': 'sales',
    'description': 'Sales performance overview',
    'is_active': True
}
dashboard = fbs.bi.create_dashboard(dashboard_data)

# Get all dashboards
dashboards = fbs.bi.get_dashboards()
print(f"Available dashboards: {dashboards}")

# Create report
report_data = {
    'name': 'Monthly Sales Report',
    'report_type': 'sales',
    'description': 'Monthly sales summary',
    'is_active': True
}
report = fbs.bi.create_report(report_data)

# Generate report
report_result = fbs.bi.generate_report(report['data']['id'], {'month': '2024-01'})
print(f"Report generated: {report_result}")

# Create KPI
kpi_data = {
    'name': 'Revenue Growth',
    'kpi_type': 'financial',
    'description': 'Monthly revenue growth percentage',
    'is_active': True
}
kpi = fbs.bi.create_kpi(kpi_data)

# Calculate KPI
kpi_value = fbs.bi.calculate_kpi(kpi['data']['id'])
print(f"KPI value: {kpi_value}")

# Create chart
chart_data = {
    'name': 'Sales Trend',
    'chart_type': 'line',
    'data_source': 'sales_data',
    'is_active': True
}
chart = fbs.bi.create_chart(chart_data)

# Get analytics data
analytics = fbs.bi.get_analytics_data('sales', {'period': 'monthly'})
print(f"Analytics data: {analytics}")
```

### 4. Workflow Management

```python
# Create workflow definition
workflow_data = {
    'name': 'Order Approval',
    'workflow_type': 'approval',
    'description': 'Order approval workflow',
    'is_active': True
}
workflow_def = fbs.workflows.create_workflow_definition(workflow_data)

# Get workflow definitions
workflows = fbs.workflows.get_workflow_definitions('approval')
print(f"Approval workflows: {workflows}")

# Start workflow
initial_data = {'order_id': 123, 'amount': 1000.00}
workflow_instance = fbs.workflows.start_workflow(workflow_def['data']['id'], initial_data)

# Get active workflows
active_workflows = fbs.workflows.get_active_workflows()
print(f"Active workflows: {active_workflows}")

# Execute workflow step
step_data = {'action': 'approve', 'comments': 'Looks good'}
result = fbs.workflows.execute_workflow_step(workflow_instance['data']['id'], step_data)

# Create approval request
approval_data = {
    'title': 'Expense Approval',
    'approval_type': 'expense',
    'description': 'Office supplies purchase',
    'requester_id': 1,
    'approver_id': 2
}
approval = fbs.workflows.create_approval_request(approval_data)

# Get approval requests
pending_approvals = fbs.workflows.get_approval_requests('pending')
print(f"Pending approvals: {pending_approvals}")

# Respond to approval
response = fbs.workflows.respond_to_approval(approval['data']['id'], 'approve', 'Approved')

# Get workflow analytics
analytics = fbs.workflows.get_workflow_analytics('approval')
print(f"Workflow analytics: {analytics}")
```

### 5. Compliance Management

```python
# Create compliance rule
rule_data = {
    'name': 'Tax Filing Deadline',
    'compliance_type': 'tax',
    'description': 'Ensure tax returns filed on time',
    'check_frequency': 'monthly',
    'is_active': True
}
rule = fbs.compliance.create_compliance_rule(rule_data)

# Get compliance rules
tax_rules = fbs.compliance.get_compliance_rules('tax')
print(f"Tax compliance rules: {tax_rules}")

# Check compliance
compliance_check = fbs.compliance.check_compliance(rule['data']['id'], {'filing_date': '2024-01-15'})
print(f"Compliance check: {compliance_check}")

# Get compliance status
overall_status = fbs.compliance.get_compliance_status()
print(f"Overall compliance: {overall_status}")

# Create audit trail
audit_data = {
    'entity_type': 'invoice',
    'entity_id': 456,
    'action': 'created',
    'user_id': 1,
    'details': 'Invoice created for customer'
}
audit = fbs.compliance.create_audit_trail(audit_data)

# Get audit trails
audit_trails = fbs.compliance.get_audit_trails('invoice', 456)
print(f"Audit trails: {audit_trails}")

# Generate compliance report
report = fbs.compliance.generate_compliance_report('quarterly', {'quarter': 'Q1'})
print(f"Compliance report: {report}")

# Get compliance deadlines
deadlines = fbs.compliance.get_compliance_deadlines('tax')
print(f"Tax deadlines: {deadlines}")

# Update compliance status
status_update = fbs.compliance.update_compliance_status(rule['data']['id'], 'compliant', 'Tax filed on time')
```

### 6. Notification Management

```python
# Create notification
notification_data = {
    'title': 'Payment Due',
    'message': 'Invoice #123 is due in 3 days',
    'notification_type': 'alert',
    'priority': 'high',
    'user_id': 1
}
notification = fbs.notifications.create_notification(notification_data)

# Get notifications
unread_notifications = fbs.notifications.get_notifications(is_read=False)
print(f"Unread notifications: {unread_notifications}")

# Mark notification as read
fbs.notifications.mark_notification_read(notification['data']['id'])

# Mark all notifications as read
fbs.notifications.mark_all_notifications_read(1)

# Delete notification
fbs.notifications.delete_notification(notification['data']['id'])

# Get notification settings
settings = fbs.notifications.get_notification_settings(1)
print(f"Notification settings: {settings}")

# Update notification settings
new_settings = {
    'email_notifications': True,
    'sms_notifications': False,
    'push_notifications': True
}
fbs.notifications.update_notification_settings(new_settings)

# Send alert
alert_data = {
    'title': 'System Alert',
    'message': 'Database backup completed',
    'alert_type': 'info',
    'priority': 'medium'
}
alert = fbs.notifications.send_alert(alert_data)

# Get active alerts
active_alerts = fbs.notifications.get_active_alerts('info')
print(f"Active alerts: {active_alerts}")
```

### 7. Client Onboarding

```python
# Start onboarding
client_data = {
    'business_name': 'New Client Corp',
    'business_type': 'manufacturing',
    'contact_email': 'contact@newclient.com',
    'employee_count': 25
}
onboarding = fbs.onboarding.start_onboarding(client_data)

# Get onboarding status
status = fbs.onboarding.get_onboarding_status(onboarding['data']['id'])
print(f"Onboarding status: {status}")

# Update onboarding step
step_data = {
    'step_name': 'business_setup',
    'completed': True,
    'data': {'business_registered': True}
}
fbs.onboarding.update_onboarding_step(onboarding['data']['id'], 'business_setup', step_data)

# Complete onboarding
result = fbs.onboarding.complete_onboarding(onboarding['data']['id'])
print(f"Onboarding completed: {result}")

# Get onboarding templates
templates = fbs.onboarding.get_onboarding_templates('manufacturing')
print(f"Manufacturing templates: {templates}")

# Apply onboarding template
fbs.onboarding.apply_onboarding_template(onboarding['data']['id'], 'manufacturing_starter')

# Import demo data
demo_result = fbs.onboarding.import_demo_data(onboarding['data']['id'], 'sample_products')
print(f"Demo data imported: {demo_result}")

# Get onboarding timeline
timeline = fbs.onboarding.get_onboarding_timeline(onboarding['data']['id'])
print(f"Onboarding timeline: {timeline}")
```

### 8. Odoo ERP Integration

```python
# Discover Odoo models
models = fbs.odoo.discover_models()
print(f"Available models: {models}")

# Discover model fields
fields = fbs.odoo.discover_fields('res.partner')
print(f"Partner fields: {fields}")

# Discover modules
modules = fbs.odoo.discover_modules()
print(f"Installed modules: {modules}")

# Get records from Odoo
partners = fbs.odoo.get_records('res.partner', {'is_company': True}, ['name', 'email'], 10)
print(f"Company partners: {partners}")

# Get single record
partner = fbs.odoo.get_record('res.partner', 1, ['name', 'email', 'phone'])
print(f"Partner details: {partner}")

# Create record in Odoo
new_partner_data = {
    'name': 'New Company Ltd',
    'is_company': True,
    'email': 'info@newcompany.com'
}
new_partner = fbs.odoo.create_record('res.partner', new_partner_data)
print(f"New partner created: {new_partner}")

# Update record in Odoo
update_data = {'phone': '+1234567890'}
updated = fbs.odoo.update_record('res.partner', new_partner['data']['id'], update_data)
print(f"Partner updated: {updated}")

# Delete record from Odoo
deleted = fbs.odoo.delete_record('res.partner', new_partner['data']['id'])
print(f"Partner deleted: {deleted}")

# Execute method on Odoo records
method_result = fbs.odoo.execute_method('res.partner', 'action_view_contacts', [1])
print(f"Method executed: {method_result}")

# Get database info
db_info = fbs.odoo.get_database_info()
print(f"Database info: {db_info}")
```

### 9. Virtual Fields & Custom Data

```python
# Set custom field
field_result = fbs.fields.set_custom_field(
    model_name='res.partner',
    record_id=1,
    field_name='customer_segment',
    field_value='premium',
    field_type='choice'
)
print(f"Custom field set: {field_result}")

# Get custom field
custom_value = fbs.fields.get_custom_field('res.partner', 1, 'customer_segment')
print(f"Custom field value: {custom_value}")

# Get all custom fields
all_custom_fields = fbs.fields.get_custom_fields('res.partner', 1)
print(f"All custom fields: {all_custom_fields}")

# Delete custom field
deleted = fbs.fields.delete_custom_field('res.partner', 1, 'customer_segment')
print(f"Custom field deleted: {deleted}")

# Merge Odoo data with custom fields
merged_data = fbs.fields.merge_odoo_with_custom(
    model_name='res.partner',
    record_id=1,
    odoo_fields=['name', 'email'],
    database_name='main_db'
)
print(f"Merged data: {merged_data}")

# Get virtual model schema
schema = fbs.fields.get_virtual_model_schema('res.partner')
print(f"Virtual model schema: {schema}")
```

### 10. Cache Management

```python
# Set cache
cache_result = fbs.cache.set_cache('user_preferences_1', {'theme': 'dark', 'language': 'en'}, 24)
print(f"Cache set: {cache_result}")

# Get cache
cached_data = fbs.cache.get_cache('user_preferences_1')
print(f"Cached data: {cached_data}")

# Delete cache
deleted = fbs.cache.delete_cache('user_preferences_1')
print(f"Cache deleted: {deleted}")

# Clear all cache
cleared = fbs.cache.clear_cache()
print(f"All cache cleared: {cleared}")

# Get cache statistics
stats = fbs.cache.get_cache_stats()
print(f"Cache statistics: {stats}")
```

### 11. Enhanced Accounting Operations

```python
# Create cash entry
cash_entry = fbs.accounting.create_cash_entry(
    entry_type='income',
    amount=1000.00,
    description='Customer payment',
    category='sales',
    date='2024-01-15'
)

# Track income/expense
income_record = fbs.accounting.track_income_expense(
    transaction_type='income',
    amount=500.00,
    description='Service fee',
    category='consulting'
)

expense_record = fbs.accounting.track_income_expense(
    transaction_type='expense',
    amount=200.00,
    description='Office supplies',
    category='operating_expenses'
)

# Get basic ledger
ledger = fbs.accounting.get_basic_ledger(
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# Get income/expense summary
summary = fbs.accounting.get_income_expense_summary('month')
print(f"Monthly summary: {summary}")

# Get financial health indicators
health = fbs.accounting.get_financial_health_indicators()
print(f"Financial health: {health}")

# Calculate tax
tax_calculation = fbs.accounting.calculate_tax(1000.00, 'vat', 0.20)
print(f"Tax calculation: {tax_calculation}")

# Get cash position
cash_position = fbs.accounting.get_cash_position()
print(f"Current cash position: {cash_position}")

# Create recurring transaction
recurring_data = {
    'description': 'Monthly rent',
    'amount': 2000.00,
    'frequency': 'monthly',
    'start_date': '2024-01-01',
    'is_active': True
}
recurring = fbs.accounting.create_recurring_transaction(recurring_data)

# Get recurring transactions
recurring_transactions = fbs.accounting.get_recurring_transactions('active')
print(f"Active recurring transactions: {recurring_transactions}")
```

## Advanced Usage Patterns

### 1. **Error Handling & Validation**

```python
try:
    # Attempt operation
    result = fbs.msme.setup_business('retail', business_config)
    
    if result['success']:
        print("Operation successful:", result['data'])
    else:
        print("Operation failed:", result['error'])
        
except Exception as e:
    print("Exception occurred:", str(e))
    # Handle specific error types
    if "database" in str(e).lower():
        print("Database connection issue")
    elif "validation" in str(e).lower():
        print("Data validation error")
```

### 2. **Batch Operations**

```python
# Batch create multiple records
results = []
for i in range(5):
    result = fbs.msme.create_custom_field({
        'field_name': f'custom_field_{i}',
        'field_type': 'char',
        'field_value': f'value_{i}'
    })
    results.append(result)

# Check batch results
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]
print(f"Batch completed: {len(successful)} successful, {len(failed)} failed")
```

### 3. **Data Synchronization**

```python
# Sync Odoo data with custom fields
def sync_customer_data(customer_id):
    # Get Odoo customer data
    odoo_data = fbs.odoo.get_record('res.partner', customer_id, ['name', 'email'])
    
    if odoo_data['success']:
        # Get custom fields
        custom_fields = fbs.fields.get_custom_fields('res.partner', customer_id)
        
        # Merge data
        merged = fbs.fields.merge_odoo_with_custom('res.partner', customer_id)
        
        # Update cache
        fbs.cache.set_cache(f'customer_{customer_id}', merged['data'], 1)
        
        return merged
    else:
        return odoo_data

# Sync multiple customers
customer_ids = [1, 2, 3, 4, 5]
for customer_id in customer_ids:
    sync_result = sync_customer_data(customer_id)
    print(f"Customer {customer_id} synced: {sync_result['success']}")
```

### 4. **Workflow Orchestration**

```python
# Complex workflow orchestration
def process_order_workflow(order_id, order_data):
    try:
        # 1. Create approval request
        approval = fbs.workflows.create_approval_request({
            'title': f'Order {order_id} Approval',
            'approval_type': 'order',
            'description': f'Order for {order_data["customer"]}',
            'requester_id': order_data['user_id'],
            'approver_id': order_data['manager_id']
        })
        
        if not approval['success']:
            return approval
        
        # 2. Send notification
        notification = fbs.notifications.create_notification({
            'title': 'Order Approval Required',
            'message': f'Order {order_id} requires approval',
            'notification_type': 'alert',
            'priority': 'high',
            'user_id': order_data['manager_id']
        })
        
        # 3. Update cache
        fbs.cache.set_cache(f'order_workflow_{order_id}', {
            'approval_id': approval['data']['id'],
            'notification_id': notification['data']['id'],
            'status': 'pending_approval'
        }, 24)
        
        return {
            'success': True,
            'workflow_id': approval['data']['id'],
            'message': 'Order workflow started successfully'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Execute workflow
workflow_result = process_order_workflow(123, {
    'customer': 'ABC Corp',
    'user_id': 1,
    'manager_id': 2
})
print(f"Workflow result: {workflow_result}")
```

## Summary

The FBS app now provides **comprehensive business capabilities** through clean service interfaces, restoring all the functionality that was documented in the original API specification:

✅ **MSME Business Management** - Complete business setup and management
✅ **Business Intelligence & Analytics** - Dashboards, reports, KPIs, charts
✅ **Workflow Management** - Approval workflows, process automation
✅ **Compliance Management** - Rules, audits, reporting, deadlines
✅ **Notification System** - Alerts, settings, priority management
✅ **Client Onboarding** - Templates, demo data, timeline tracking
✅ **Odoo ERP Integration** - Model discovery, CRUD operations, method execution
✅ **Virtual Fields** - Custom data extension, data merging
✅ **Cache Management** - Performance optimization, data caching
✅ **Enhanced Accounting** - Cash basis, recurring transactions, tax calculations

This approach provides **better performance**, **type safety**, **error handling**, and **direct access** to business logic compared to HTTP API endpoints, while maintaining all the original functionality.
