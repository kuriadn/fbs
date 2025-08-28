# Generated Django migration for FBS App Accounting Models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fbs_app', '0005_compliance_models'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_type', models.CharField(choices=[('receipt', 'Receipt'), ('payment', 'Payment'), ('transfer', 'Transfer'), ('adjustment', 'Adjustment'), ('refund', 'Refund')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('currency', models.CharField(max_length=3, default='USD')),
                ('description', models.TextField()),
                ('reference_number', models.CharField(max_length=100, blank=True)),
                ('entry_date', models.DateField()),
                ('is_reconciled', models.BooleanField(default=False)),
                ('reconciliation_date', models.DateField(null=True, blank=True)),
                ('entry_data', models.JSONField(default=dict, help_text='Additional entry data')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_cash_entries',
                'ordering': ['-entry_date'],
                'indexes': [
                    models.Index(fields=['entry_date'], name='fbs_cash_entries_date_idx'),
                    models.Index(fields=['entry_type'], name='fbs_cash_entries_type_idx'),
                    models.Index(fields=['is_reconciled'], name='fbs_cash_entries_reconciled_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='IncomeExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('income', 'Income'), ('expense', 'Expense')], max_length=20)),
                ('category', models.CharField(max_length=100)),
                ('subcategory', models.CharField(max_length=100, blank=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('currency', models.CharField(max_length=3, default='USD')),
                ('description', models.TextField()),
                ('transaction_date', models.DateField()),
                ('due_date', models.DateField(null=True, blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('payment_method', models.CharField(max_length=100, blank=True)),
                ('transaction_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_income_expenses',
                'ordering': ['-transaction_date'],
                'indexes': [
                    models.Index(fields=['transaction_date'], name='fbs_income_expenses_date_idx'),
                    models.Index(fields=['transaction_type'], name='fbs_income_expenses_type_idx'),
                    models.Index(fields=['category'], name='fbs_income_expenses_category_idx'),
                    models.Index(fields=['status'], name='fbs_income_expenses_status_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='BasicLedger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=100)),
                ('account_type', models.CharField(choices=[('asset', 'Asset'), ('liability', 'Liability'), ('equity', 'Equity'), ('income', 'Income'), ('expense', 'Expense')], max_length=20)),
                ('description', models.TextField()),
                ('debit_amount', models.DecimalField(decimal_places=2, max_digits=15, default=0)),
                ('credit_amount', models.DecimalField(decimal_places=2, max_digits=15, default=0)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=15)),
                ('currency', models.CharField(max_length=3, default='USD')),
                ('entry_date', models.DateField()),
                ('reference', models.CharField(max_length=100, blank=True)),
                ('is_reconciled', models.BooleanField(default=False)),
                ('ledger_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_basic_ledgers',
                'ordering': ['entry_date'],
                'indexes': [
                    models.Index(fields=['entry_date'], name='fbs_basic_ledgers_date_idx'),
                    models.Index(fields=['account'], name='fbs_basic_ledgers_account_idx'),
                    models.Index(fields=['account_type'], name='fbs_basic_ledgers_account_type_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='TaxCalculation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tax_type', models.CharField(choices=[('income_tax', 'Income Tax'), ('sales_tax', 'Sales Tax'), ('property_tax', 'Property Tax'), ('payroll_tax', 'Payroll Tax'), ('custom_tax', 'Custom Tax')], max_length=20)),
                ('tax_period', models.CharField(max_length=20, help_text='Tax period (monthly, quarterly, yearly)')),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('gross_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('tax_rate', models.DecimalField(decimal_places=4, max_digits=6, help_text='Tax rate as percentage')),
                ('tax_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('net_tax_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('currency', models.CharField(max_length=3, default='USD')),
                ('calculation_date', models.DateField()),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('calculated', 'Calculated'), ('reviewed', 'Reviewed'), ('approved', 'Approved'), ('filed', 'Filed'), ('paid', 'Paid')], default='calculated', max_length=20)),
                ('calculation_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_tax_calculations',
                'ordering': ['-calculation_date'],
                'indexes': [
                    models.Index(fields=['calculation_date'], name='fbs_tax_calculations_date_idx'),
                    models.Index(fields=['tax_type'], name='fbs_tax_calculations_type_idx'),
                    models.Index(fields=['status'], name='fbs_tax_calculations_status_idx'),
                    models.Index(fields=['due_date'], name='fbs_tax_calculations_due_date_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ChartOfAccounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_code', models.CharField(max_length=20, unique=True)),
                ('account_name', models.CharField(max_length=200)),
                ('account_type', models.CharField(choices=[('asset', 'Asset'), ('liability', 'Liability'), ('equity', 'Equity'), ('income', 'Income'), ('expense', 'Expense')], max_length=20)),
                ('parent_account', models.CharField(max_length=20, null=True, blank=True, help_text='Parent account code for hierarchical structure')),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('normal_balance', models.CharField(choices=[('debit', 'Debit'), ('credit', 'Credit')], max_length=10)),
                ('account_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_chart_of_accounts',
                'ordering': ['account_code'],
                'indexes': [
                    models.Index(fields=['account_code'], name='fbs_chart_of_accounts_code_idx'),
                    models.Index(fields=['account_type'], name='fbs_chart_of_accounts_type_idx'),
                    models.Index(fields=['parent_account'], name='fbs_chart_of_accounts_parent_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='FinancialPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_name', models.CharField(max_length=100)),
                ('period_type', models.CharField(choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('is_closed', models.BooleanField(default=False)),
                ('closing_date', models.DateTimeField(null=True, blank=True)),
                ('closing_notes', models.TextField(blank=True)),
                ('period_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'fbs_financial_periods',
                'ordering': ['-start_date'],
                'indexes': [
                    models.Index(fields=['start_date'], name='fbs_financial_periods_start_date_idx'),
                    models.Index(fields=['period_type'], name='fbs_financial_periods_type_idx'),
                    models.Index(fields=['is_closed'], name='fbs_financial_periods_closed_idx'),
                ],
            },
        ),
    ]
