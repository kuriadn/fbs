# Generated Django migration for FBS App Discovery Models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fbs_app', '0006_accounting_models'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='OdooModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=100, unique=True)),
                ('model_label', models.CharField(max_length=200)),
                ('model_description', models.TextField(blank=True)),
                ('model_type', models.CharField(choices=[('base', 'Base Model'), ('custom', 'Custom Model'), ('inherited', 'Inherited Model')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_abstract', models.BooleanField(default=False)),
                ('model_data', models.JSONField(default=dict, help_text='Additional model metadata')),
                ('discovered_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('discovered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_odoo_models',
                'ordering': ['model_name'],
                'indexes': [
                    models.Index(fields=['model_name'], name='fbs_odoo_models_name_idx'),
                    models.Index(fields=['model_type'], name='fbs_odoo_models_type_idx'),
                    models.Index(fields=['is_active'], name='fbs_odoo_models_active_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='OdooField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=100)),
                ('field_label', models.CharField(max_length=200)),
                ('field_type', models.CharField(max_length=50)),
                ('field_description', models.TextField(blank=True)),
                ('is_required', models.BooleanField(default=False)),
                ('is_readonly', models.BooleanField(default=False)),
                ('is_computed', models.BooleanField(default=False)),
                ('default_value', models.TextField(blank=True)),
                ('field_data', models.JSONField(default=dict, help_text='Additional field metadata')),
                ('discovered_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='fbs_app.odoomodel')),
            ],
            options={
                'db_table': 'fbs_odoo_fields',
                'ordering': ['field_name'],
                'indexes': [
                    models.Index(fields=['field_name'], name='fbs_odoo_fields_name_idx'),
                    models.Index(fields=['field_type'], name='fbs_odoo_fields_type_idx'),
                    models.Index(fields=['is_required'], name='fbs_odoo_fields_required_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='OdooModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_name', models.CharField(max_length=100, unique=True)),
                ('module_title', models.CharField(max_length=200)),
                ('module_description', models.TextField(blank=True)),
                ('module_version', models.CharField(max_length=20)),
                ('module_category', models.CharField(max_length=100, blank=True)),
                ('is_installed', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('installation_date', models.DateTimeField(null=True, blank=True)),
                ('module_data', models.JSONField(default=dict, help_text='Additional module metadata')),
                ('discovered_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('discovered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_odoo_modules',
                'ordering': ['module_name'],
                'indexes': [
                    models.Index(fields=['module_name'], name='fbs_odoo_modules_name_idx'),
                    models.Index(fields=['is_installed'], name='fbs_odoo_modules_installed_idx'),
                    models.Index(fields=['module_category'], name='fbs_odoo_modules_category_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='DiscoverySession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=100, unique=True)),
                ('session_name', models.CharField(max_length=200)),
                ('session_description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('execution_time', models.FloatField(null=True, blank=True, help_text='Execution time in seconds')),
                ('discovery_config', models.JSONField(default=dict, help_text='Discovery configuration and parameters')),
                ('discovery_results', models.JSONField(default=dict, help_text='Discovery results and statistics')),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('initiated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_discovery_sessions',
                'ordering': ['-started_at'],
                'indexes': [
                    models.Index(fields=['status'], name='fbs_discovery_sessions_status_idx'),
                    models.Index(fields=['started_at'], name='fbs_discovery_sessions_started_idx'),
                    models.Index(fields=['session_id'], name='fbs_discovery_sessions_session_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ModelRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship_type', models.CharField(choices=[('one2many', 'One to Many'), ('many2one', 'Many to One'), ('many2many', 'Many to Many'), ('one2one', 'One to One')], max_length=20)),
                ('relationship_name', models.CharField(max_length=100)),
                ('relationship_description', models.TextField(blank=True)),
                ('relationship_data', models.JSONField(default=dict, help_text='Additional relationship metadata')),
                ('discovered_at', models.DateTimeField(auto_now_add=True)),
                ('from_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_relationships', to='fbs_app.odoomodel')),
                ('to_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_relationships', to='fbs_app.odoomodel')),
            ],
            options={
                'db_table': 'fbs_model_relationships',
                'ordering': ['relationship_name'],
                'indexes': [
                    models.Index(fields=['relationship_type'], name='fbs_model_relationships_type_idx'),
                    models.Index(fields=['from_model', 'to_model'], name='fbs_model_relationships_models_idx'),
                ],
            },
        ),
    ]
