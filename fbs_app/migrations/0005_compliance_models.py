# Generated Django migration for FBS App Compliance Models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fbs_app', '0004_bi_models'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComplianceRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('rule_type', models.CharField(choices=[('tax', 'Tax Compliance'), ('labor', 'Labor Law'), ('environmental', 'Environmental'), ('health_safety', 'Health & Safety'), ('financial', 'Financial'), ('data_privacy', 'Data Privacy'), ('industry_specific', 'Industry Specific')], max_length=20)),
                ('rule_category', models.CharField(choices=[('regulatory', 'Regulatory'), ('internal', 'Internal Policy'), ('industry_standard', 'Industry Standard'), ('contractual', 'Contractual')], max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=20)),
                ('rule_definition', models.JSONField(default=dict, help_text='Rule logic and conditions')),
                ('compliance_frequency', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly'), ('on_demand', 'On Demand')], max_length=20)),
                ('next_review_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_compliance_rules',
                'ordering': ['priority', 'name'],
                'indexes': [
                    models.Index(fields=['rule_type'], name='fbs_compliance_rules_type_idx'),
                    models.Index(fields=['priority'], name='fbs_compliance_rules_priority_idx'),
                    models.Index(fields=['next_review_date'], name='fbs_compliance_rules_review_date_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='AuditTrail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100)),
                ('action_type', models.CharField(choices=[('create', 'Create'), ('read', 'Read'), ('update', 'Update'), ('delete', 'Delete'), ('login', 'Login'), ('logout', 'Logout'), ('export', 'Export'), ('import', 'Import')], max_length=20)),
                ('resource_type', models.CharField(max_length=100, help_text='Type of resource being acted upon')),
                ('resource_id', models.CharField(max_length=100, help_text='ID of the resource being acted upon')),
                ('old_values', models.JSONField(null=True, blank=True, help_text='Previous values before change')),
                ('new_values', models.JSONField(null=True, blank=True, help_text='New values after change')),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('session_id', models.CharField(max_length=100, blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_audit_trails',
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['timestamp'], name='fbs_audit_trails_timestamp_idx'),
                    models.Index(fields=['action_type'], name='fbs_audit_trails_action_type_idx'),
                    models.Index(fields=['resource_type', 'resource_id'], name='fbs_audit_trails_resource_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ReportSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('schedule_type', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly'), ('custom', 'Custom')], max_length=20)),
                ('schedule_config', models.JSONField(default=dict, help_text='Schedule configuration (days, times, etc.)')),
                ('is_active', models.BooleanField(default=True)),
                ('last_run', models.DateTimeField(null=True, blank=True)),
                ('next_run', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_report_schedules',
                'ordering': ['next_run'],
                'indexes': [
                    models.Index(fields=['next_run'], name='fbs_report_schedules_next_run_idx'),
                    models.Index(fields=['schedule_type'], name='fbs_report_schedules_type_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='RecurringTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('transaction_type', models.CharField(choices=[('income', 'Income'), ('expense', 'Expense'), ('transfer', 'Transfer'), ('adjustment', 'Adjustment')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('currency', models.CharField(max_length=3, default='USD')),
                ('frequency', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True, blank=True)),
                ('last_executed', models.DateTimeField(null=True, blank=True)),
                ('next_execution', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('transaction_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_recurring_transactions',
                'ordering': ['next_execution'],
                'indexes': [
                    models.Index(fields=['next_execution'], name='fbs_recurring_transactions_next_execution_idx'),
                    models.Index(fields=['transaction_type'], name='fbs_recurring_transactions_type_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='UserActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('login', 'User Login'), ('logout', 'User Logout'), ('page_view', 'Page View'), ('action', 'User Action'), ('error', 'Error Occurred'), ('warning', 'Warning Generated')], max_length=20)),
                ('activity_description', models.TextField()),
                ('page_url', models.CharField(max_length=500, blank=True)),
                ('session_duration', models.IntegerField(null=True, blank=True, help_text='Session duration in seconds')),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('activity_data', models.JSONField(default=dict, help_text='Additional activity data')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_user_activity_logs',
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['timestamp'], name='fbs_user_activity_logs_timestamp_idx'),
                    models.Index(fields=['activity_type'], name='fbs_user_activity_logs_activity_type_idx'),
                    models.Index(fields=['user'], name='fbs_user_activity_logs_user_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ComplianceCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_name', models.CharField(max_length=200)),
                ('check_type', models.CharField(choices=[('automated', 'Automated Check'), ('manual', 'Manual Check'), ('scheduled', 'Scheduled Check')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('passed', 'Passed'), ('failed', 'Failed'), ('warning', 'Warning')], max_length=20)),
                ('check_result', models.JSONField(default=dict, help_text='Check results and details')),
                ('execution_time', models.FloatField(null=True, blank=True, help_text='Execution time in seconds')),
                ('last_checked', models.DateTimeField(auto_now_add=True)),
                ('next_check', models.DateTimeField()),
                ('compliance_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fbs_app.compliancerule')),
                ('checked_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_compliance_checks',
                'ordering': ['-last_checked'],
                'indexes': [
                    models.Index(fields=['status'], name='fbs_compliance_checks_status_idx'),
                    models.Index(fields=['next_check'], name='fbs_compliance_checks_next_check_idx'),
                ],
            },
        ),
    ]
