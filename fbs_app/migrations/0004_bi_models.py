# Generated Django migration for FBS App Business Intelligence Models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fbs_app', '0003_workflow_models'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('dashboard_type', models.CharField(choices=[('executive', 'Executive Dashboard'), ('operational', 'Operational Dashboard'), ('financial', 'Financial Dashboard'), ('compliance', 'Compliance Dashboard'), ('custom', 'Custom Dashboard')], max_length=20)),
                ('layout_config', models.JSONField(default=dict, help_text='Dashboard layout and widget configuration')),
                ('is_public', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('refresh_interval', models.IntegerField(default=300, help_text='Refresh interval in seconds')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_dashboards',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('report_type', models.CharField(choices=[('financial', 'Financial Report'), ('operational', 'Operational Report'), ('compliance', 'Compliance Report'), ('analytics', 'Analytics Report'), ('custom', 'Custom Report')], max_length=20)),
                ('report_template', models.TextField(help_text='Report template or configuration')),
                ('parameters', models.JSONField(default=dict, help_text='Report parameters and filters')),
                ('is_scheduled', models.BooleanField(default=False)),
                ('schedule_config', models.JSONField(default=dict, help_text='Schedule configuration for automated reports')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_reports',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='KPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('kpi_type', models.CharField(choices=[('financial', 'Financial KPI'), ('operational', 'Operational KPI'), ('customer', 'Customer KPI'), ('employee', 'Employee KPI'), ('compliance', 'Compliance KPI')], max_length=20)),
                ('calculation_formula', models.TextField(help_text='KPI calculation formula or logic')),
                ('target_value', models.DecimalField(decimal_places=4, max_digits=15, null=True, blank=True)),
                ('current_value', models.DecimalField(decimal_places=4, max_digits=15, null=True, blank=True)),
                ('unit', models.CharField(max_length=50)),
                ('frequency', models.CharField(choices=[('real_time', 'Real Time'), ('hourly', 'Hourly'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_kpis',
                'ordering': ['name'],
                'indexes': [
                    models.Index(fields=['kpi_type'], name='fbs_kpis_type_idx'),
                    models.Index(fields=['frequency'], name='fbs_kpis_frequency_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Chart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('chart_type', models.CharField(choices=[('line', 'Line Chart'), ('bar', 'Bar Chart'), ('pie', 'Pie Chart'), ('area', 'Area Chart'), ('scatter', 'Scatter Plot'), ('table', 'Data Table'), ('gauge', 'Gauge'), ('funnel', 'Funnel Chart')], max_length=20)),
                ('chart_config', models.JSONField(default=dict, help_text='Chart configuration and styling')),
                ('data_source', models.CharField(max_length=200, help_text='Data source for the chart')),
                ('refresh_interval', models.IntegerField(default=300, help_text='Refresh interval in seconds')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_charts',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DashboardWidget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('widget_type', models.CharField(choices=[('chart', 'Chart Widget'), ('kpi', 'KPI Widget'), ('report', 'Report Widget'), ('table', 'Table Widget'), ('text', 'Text Widget')], max_length=20)),
                ('position_x', models.IntegerField()),
                ('position_y', models.IntegerField()),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('widget_config', models.JSONField(default=dict, help_text='Widget-specific configuration')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('chart', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fbs_app.chart')),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='widgets', to='fbs_app.dashboard')),
                ('kpi', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fbs_app.kpi')),
                ('report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fbs_app.report')),
            ],
            options={
                'db_table': 'fbs_dashboard_widgets',
                'ordering': ['position_y', 'position_x'],
            },
        ),
        migrations.CreateModel(
            name='ReportExecution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('execution_id', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('execution_time', models.FloatField(null=True, blank=True, help_text='Execution time in seconds')),
                ('result_file', models.CharField(max_length=500, null=True, blank=True, help_text='Path to generated report file')),
                ('error_message', models.TextField(null=True, blank=True)),
                ('execution_parameters', models.JSONField(default=dict)),
                ('executed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fbs_app.report')),
            ],
            options={
                'db_table': 'fbs_report_executions',
                'ordering': ['-started_at'],
                'indexes': [
                    models.Index(fields=['status'], name='fbs_report_executions_status_idx'),
                    models.Index(fields=['report'], name='fbs_report_executions_report_idx'),
                ],
            },
        ),
    ]
