# Generated Django migration for FBS App Workflow Models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fbs_app', '0002_msme_models'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkflowDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('workflow_type', models.CharField(choices=[('approval', 'Approval Workflow'), ('document', 'Document Workflow'), ('purchase', 'Purchase Workflow'), ('compliance', 'Compliance Workflow'), ('custom', 'Custom Workflow')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('workflow_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_workflow_definitions',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='WorkflowStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_name', models.CharField(max_length=100)),
                ('step_order', models.IntegerField()),
                ('step_type', models.CharField(choices=[('manual', 'Manual Step'), ('automated', 'Automated Step'), ('decision', 'Decision Point'), ('notification', 'Notification Step')], max_length=20)),
                ('step_config', models.JSONField(default=dict)),
                ('is_required', models.BooleanField(default=True)),
                ('estimated_duration', models.IntegerField(help_text='Estimated duration in hours', null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='fbs_app.workflowdefinition')),
            ],
            options={
                'db_table': 'fbs_workflow_steps',
                'ordering': ['step_order'],
            },
        ),
        migrations.CreateModel(
            name='WorkflowTransition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('transition_type', models.CharField(choices=[('forward', 'Forward'), ('backward', 'Backward'), ('conditional', 'Conditional'), ('parallel', 'Parallel')], max_length=20)),
                ('conditions', models.JSONField(default=dict, help_text='Transition conditions and rules')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('from_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_transitions', to='fbs_app.workflowstep')),
                ('to_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_transitions', to='fbs_app.workflowstep')),
            ],
            options={
                'db_table': 'fbs_workflow_transitions',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='WorkflowInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance_id', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('paused', 'Paused'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='draft', max_length=20)),
                ('current_step', models.CharField(max_length=100)),
                ('progress_percentage', models.IntegerField(default=0)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('instance_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('initiated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fbs_app.workflowdefinition')),
            ],
            options={
                'db_table': 'fbs_workflow_instances',
                'ordering': ['-started_at'],
                'indexes': [
                    models.Index(fields=['status'], name='fbs_workflow_instances_status_idx'),
                    models.Index(fields=['workflow'], name='fbs_workflow_instances_workflow_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='WorkflowExecutionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100)),
                ('action_data', models.JSONField(default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('executed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('workflow_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='execution_logs', to='fbs_app.workflowinstance')),
            ],
            options={
                'db_table': 'fbs_workflow_execution_logs',
                'ordering': ['-timestamp'],
            },
        ),
    ]
