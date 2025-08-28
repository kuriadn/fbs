# Generated Django migration for FBS App MSME Models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fbs_app', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='MSMESetupWizard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200)),
                ('business_type', models.CharField(choices=[('retail', 'Retail'), ('manufacturing', 'Manufacturing'), ('services', 'Services'), ('agriculture', 'Agriculture'), ('other', 'Other')], max_length=20)),
                ('setup_stage', models.CharField(choices=[('initial', 'Initial Setup'), ('basic_info', 'Basic Information'), ('modules', 'Module Selection'), ('configuration', 'Configuration'), ('testing', 'Testing'), ('complete', 'Complete')], default='initial', max_length=20)),
                ('setup_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_msme_setup_wizards',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MSMEKPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kpi_name', models.CharField(max_length=100)),
                ('kpi_description', models.TextField()),
                ('kpi_type', models.CharField(choices=[('financial', 'Financial'), ('operational', 'Operational'), ('customer', 'Customer'), ('employee', 'Employee')], max_length=20)),
                ('current_value', models.DecimalField(decimal_places=2, max_digits=15)),
                ('target_value', models.DecimalField(decimal_places=2, max_digits=15)),
                ('unit', models.CharField(max_length=50)),
                ('frequency', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_msme_kpis',
                'ordering': ['kpi_name'],
            },
        ),
        migrations.CreateModel(
            name='MSMECompliance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compliance_name', models.CharField(max_length=200)),
                ('compliance_type', models.CharField(choices=[('tax', 'Tax Compliance'), ('labor', 'Labor Law'), ('environmental', 'Environmental'), ('health_safety', 'Health & Safety'), ('other', 'Other')], max_length=20)),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('overdue', 'Overdue')], default='pending', max_length=20)),
                ('compliance_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_msme_compliance',
                'ordering': ['due_date'],
            },
        ),
        migrations.CreateModel(
            name='MSMEMarketing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_name', models.CharField(max_length=200)),
                ('campaign_type', models.CharField(choices=[('social_media', 'Social Media'), ('email', 'Email Marketing'), ('print', 'Print Advertising'), ('digital', 'Digital Advertising'), ('events', 'Events')], max_length=20)),
                ('budget', models.DecimalField(decimal_places=2, max_digits=15)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('active', 'Active'), ('paused', 'Paused'), ('completed', 'Completed')], default='planned', max_length=20)),
                ('campaign_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_msme_marketing',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='MSMETemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_name', models.CharField(max_length=100)),
                ('template_type', models.CharField(choices=[('invoice', 'Invoice'), ('quotation', 'Quotation'), ('purchase_order', 'Purchase Order'), ('receipt', 'Receipt'), ('report', 'Report')], max_length=20)),
                ('template_content', models.TextField()),
                ('is_default', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_msme_templates',
                'ordering': ['template_name'],
            },
        ),
        migrations.CreateModel(
            name='MSMEAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric_name', models.CharField(max_length=100)),
                ('metric_value', models.DecimalField(decimal_places=2, max_digits=15)),
                ('metric_date', models.DateField()),
                ('metric_type', models.CharField(choices=[('revenue', 'Revenue'), ('expenses', 'Expenses'), ('profit', 'Profit'), ('customers', 'Customers'), ('orders', 'Orders')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_msme_analytics',
                'ordering': ['-metric_date'],
                'indexes': [
                    models.Index(fields=['metric_date'], name='fbs_msme_analytics_date_idx'),
                    models.Index(fields=['metric_type'], name='fbs_msme_analytics_type_idx'),
                ],
            },
        ),
    ]
