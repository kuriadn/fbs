"""
FBS App Accounting Models

Models for managing basic accounting operations including cash entries, income/expense tracking, and basic ledger.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
import json


class CashEntry(models.Model):
    """Model to store cash basis accounting entries"""
    business_id = models.CharField(max_length=100)  # Reference to business
    entry_date = models.DateField()
    entry_type = models.CharField(max_length=20, choices=[
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
    ])
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField()
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('mobile_payment', 'Mobile Payment'),
        ('other', 'Other'),
    ])
    reference_number = models.CharField(max_length=100, blank=True)
    vendor_customer = models.CharField(max_length=200, blank=True)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    attachments = models.JSONField(default=list)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cash Entry'
        verbose_name_plural = 'Cash Entries'
        ordering = ['-entry_date', '-created_at']
        app_label = 'fbs_app'
        indexes = [
            models.Index(fields=['business_id', 'entry_date']),
            models.Index(fields=['entry_type', 'category']),
            models.Index(fields=['payment_method', 'entry_date']),
        ]
    
    def __str__(self):
        return f"{self.entry_type.title()}: {self.amount} - {self.description} ({self.entry_date})"


class IncomeExpense(models.Model):
    """Model to store income and expense tracking"""
    business_id = models.CharField(max_length=100)  # Reference to business
    transaction_date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=[
        ('income', 'Income'),
        ('expense', 'Expense'),
    ])
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField()
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)
    account = models.CharField(max_length=100, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    vendor_customer = models.CharField(max_length=200, blank=True)
    payment_terms = models.CharField(max_length=100, blank=True)
    due_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Income/Expense'
        verbose_name_plural = 'Income/Expenses'
        ordering = ['-transaction_date', '-created_at']
        app_label = 'fbs_app'
        indexes = [
            models.Index(fields=['business_id', 'transaction_date']),
            models.Index(fields=['transaction_type', 'category']),
            models.Index(fields=['payment_status', 'due_date']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type.title()}: {self.amount} - {self.description} ({self.transaction_date})"


class BasicLedger(models.Model):
    """Model to store basic general ledger entries"""
    business_id = models.CharField(max_length=100)  # Reference to business
    entry_date = models.DateField()
    account = models.CharField(max_length=100)
    account_type = models.CharField(max_length=50, choices=[
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense'),
    ])
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True)
    reference_type = models.CharField(max_length=50, blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2)  # Running balance
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Basic Ledger Entry'
        verbose_name_plural = 'Basic Ledger Entries'
        ordering = ['account', 'entry_date']
        app_label = 'fbs_app'
        indexes = [
            models.Index(fields=['business_id', 'account', 'entry_date']),
            models.Index(fields=['account_type', 'entry_date']),
        ]
    
    def __str__(self):
        return f"{self.account}: {self.description} ({self.entry_date})"


class TaxCalculation(models.Model):
    """Model to store tax calculations and records"""
    business_id = models.CharField(max_length=100)  # Reference to business
    tax_period_start = models.DateField()
    tax_period_end = models.DateField()
    tax_type = models.CharField(max_length=50, choices=[
        ('income_tax', 'Income Tax'),
        ('sales_tax', 'Sales Tax'),
        ('payroll_tax', 'Payroll Tax'),
        ('property_tax', 'Property Tax'),
        ('other', 'Other'),
    ])
    taxable_amount = models.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2)
    deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_tax_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ], default='pending')
    due_date = models.DateField()
    filing_date = models.DateField(null=True, blank=True)
    filing_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tax Calculation'
        verbose_name_plural = 'Tax Calculations'
        ordering = ['-tax_period_end', 'tax_type']
        app_label = 'fbs_app'
        indexes = [
            models.Index(fields=['business_id', 'tax_type', 'tax_period_end']),
            models.Index(fields=['payment_status', 'due_date']),
        ]
    
    def __str__(self):
        return f"{self.tax_type}: {self.tax_period_start} to {self.tax_period_end} - {self.net_tax_amount}"
