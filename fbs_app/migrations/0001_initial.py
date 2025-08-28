# Generated Django migration for FBS App
# This migration creates all the required database tables for FBS functionality

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # Core models
        migrations.CreateModel(
            name='OdooDatabase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('host', models.CharField(max_length=255)),
                ('port', models.IntegerField(default=8069)),
                ('protocol', models.CharField(default='http', max_length=10)),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Odoo Database',
                'verbose_name_plural': 'Odoo Databases',
                'db_table': 'fbs_odoo_databases',
            },
        ),
        migrations.CreateModel(
            name='TokenMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('database', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fbs_app.odoodatabase')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_token_mappings',
                'unique_together': {('user', 'database')},
            },
        ),
        migrations.CreateModel(
            name='RequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('PATCH', 'PATCH'), ('DELETE', 'DELETE')], max_length=10)),
                ('path', models.CharField(max_length=500)),
                ('status_code', models.IntegerField()),
                ('response_time', models.FloatField(help_text='Response time in milliseconds')),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('request_data', models.JSONField(blank=True, default=dict)),
                ('response_data', models.JSONField(blank=True, default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('database', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fbs_app.odoodatabase')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_request_logs',
                'indexes': [
                    models.Index(fields=['timestamp'], name='fbs_request_logs_timestamp_idx'),
                    models.Index(fields=['user', 'timestamp'], name='fbs_request_logs_user_timestamp_idx'),
                    models.Index(fields=['database', 'timestamp'], name='fbs_request_logs_database_timestamp_idx'),
                    models.Index(fields=['status_code', 'timestamp'], name='fbs_request_logs_status_code_timestamp_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='BusinessRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('rule_type', models.CharField(choices=[('validation', 'Validation Rule'), ('calculation', 'Calculation Rule'), ('workflow', 'Workflow Rule'), ('compliance', 'Compliance Rule')], max_length=20)),
                ('rule_definition', models.JSONField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'fbs_business_rules',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CacheEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255, unique=True)),
                ('value', models.TextField()),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'fbs_cache_entries',
                'indexes': [
                    models.Index(fields=['expires_at'], name='fbs_cache_entries_expires_at_idx'),
                    models.Index(fields=['key'], name='fbs_cache_entries_key_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Handshake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solution_name', models.CharField(max_length=100)),
                ('handshake_token', models.CharField(max_length=255, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('handshake_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'fbs_handshakes',
                'indexes': [
                    models.Index(fields=['solution_name'], name='fbs_handshakes_solution_name_idx'),
                    models.Index(fields=['status'], name='fbs_handshakes_status_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('info', 'Information'), ('warning', 'Warning'), ('error', 'Error'), ('success', 'Success')], max_length=20)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_notifications',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', 'is_read'], name='fbs_notifications_user_read_idx'),
                    models.Index(fields=['notification_type'], name='fbs_notifications_type_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ApprovalRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('approval_type', models.CharField(choices=[('workflow', 'Workflow Approval'), ('document', 'Document Approval'), ('purchase', 'Purchase Approval'), ('expense', 'Expense Approval'), ('other', 'Other')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('solution_name', models.CharField(blank=True, max_length=100)),
                ('request_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('approver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approvals_to_review', to='auth.user')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_requests', to='auth.user')),
            ],
            options={
                'db_table': 'fbs_approval_requests',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['requester', 'status'], name='fbs_approval_requests_requester_status_idx'),
                    models.Index(fields=['approver', 'status'], name='fbs_approval_requests_approver_status_idx'),
                    models.Index(fields=['solution_name', 'status'], name='fbs_approval_requests_solution_status_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ApprovalResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(choices=[('approve', 'Approve'), ('reject', 'Reject'), ('request_changes', 'Request Changes')], max_length=20)),
                ('comments', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approval_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='fbs_app.approvalrequest')),
                ('responder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_approval_responses',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=100)),
                ('record_id', models.IntegerField()),
                ('field_name', models.CharField(max_length=100)),
                ('field_type', models.CharField(choices=[('char', 'Character'), ('text', 'Text'), ('integer', 'Integer'), ('float', 'Float'), ('boolean', 'Boolean'), ('date', 'Date'), ('datetime', 'DateTime'), ('json', 'JSON'), ('choice', 'Choice')], default='char', max_length=20)),
                ('field_value', models.TextField()),
                ('database_name', models.CharField(blank=True, max_length=100)),
                ('solution_name', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'fbs_custom_fields',
                'unique_together': {('model_name', 'record_id', 'field_name', 'database_name')},
                'indexes': [
                    models.Index(fields=['model_name', 'record_id'], name='fbs_custom_fields_model_record_idx'),
                    models.Index(fields=['database_name', 'model_name'], name='fbs_custom_fields_database_model_idx'),
                ],
            },
        ),
    ]
