"""
Isolated Model for Finance aspects of the app
"""
# Regular inbuilt modules imports
from uuid import uuid4
from datetime import date
from decimal import Decimal
from django.core.validators import MinValueValidator

# Django imports
from django.db import models
from django.contrib.postgres.fields import (
    DateRangeField,
    # RangeOperators
)
# from django.contrib.postgres.constraints import ExclusionConstraint

# Local imports
from core.models import (
    User, AcademicYear, AcademicTerm,
    Student, OrganizationDocument,
    OrganizationConfig, Staff
)
from core.utils import (
    # invoice_status,
    # payment_type_choices,
    PaymentType,
    # employment_type_choices,
    # payment_method,
    PaymentMethod,
    PayrollRunStatus,
    get_payrun_period
)

PaymentTypes = tuple((item.value, item.name) for item in list(PaymentType))
PaymentMethods = tuple((item.value, item.name) for item in list(PaymentMethod))
PayrollRunStatuses = tuple(
    (item.value, item.name) for item in list(PayrollRunStatus)
    )


class TaxConfig(models.Model):
    """Taxation model on the organization"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(
        OrganizationConfig, on_delete=models.CASCADE
        )
    name = models.CharField(
        max_length=250,
        help_text="Name of the Tax. e.g PAYE, Witholding, etc"
        )
    tax_percent = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Percentage to be applied as tax"
        )
    flat_tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="If tax is a flat amount rather than a percentage rate"
        )


class Tax(models.Model):
    """The tax objects calculated on incomes"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    tax_config = models.ForeignKey(TaxConfig, on_delete=models.CASCADE)
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Amount of money to be taxed"
    )
    tax = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="The actual amount being paid as tax"
    )
    gross_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Total amount on the income"
    )


class Supplier(models.Model):
    """Supplier details"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    full_name = models.CharField(max_length=500, unique=True)
    company_name = models.CharField(max_length=500, unique=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    telephone = models.CharField(max_length=150, null=True, blank=True)
    image = models.ImageField(
        upload_to="suppliers", null=True, blank=True,
        help_text="Logo of the supplier"
        )

    def __self__(self):
        return self.name


class IncomeType(models.Model):
    """Income types: Fees, etc"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Income(models.Model):
    """All incomes accruing to the school"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    income_type = models.ForeignKey(IncomeType, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    academic_term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00))
    purpose = models.CharField(max_length=500)
    payer = models.CharField(max_length=400, null=True, blank=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        null=True, blank=True,
        help_text="this is null if it's not fees"
        )
    uploaded_file = models.ManyToManyField(
        OrganizationDocument,
        blank=True
        )
    income_date = models.DateField(default=date.today)
    tax = models.ManyToManyField(Tax, blank=True)
    payment_method = models.CharField(
        max_length=200, choices=PaymentMethods,
        default="Bank"
    )
    # payment_id = models.UUIDField(null=True, blank=True)


class ExpenditureType(models.Model):
    """Types or Categories of expenditure that are incurred"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=400)

    def __str__(self):
        return self.name


class Expenditure(models.Model):
    """The actual expenditure incurred in the term under the academic year"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    expenditure_type = models.ForeignKey(
        ExpenditureType, on_delete=models.CASCADE
        )
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    academic_term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),)
    purpose = models.CharField(max_length=500)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE,
        null=True, blank=True
        )
    invoice = models.FileField(upload_to="invoices", null=True, blank=True)
    expense_date = models.DateField(default=date.today)
    uploaded_file = models.ManyToManyField(
        OrganizationDocument,
        blank=True
        )
    payment_type = models.CharField(
        max_length=100, choices=PaymentTypes,
        default="Invoice"
        )
    payment_method = models.CharField(
        max_length=200, choices=PaymentMethods,
        default="Bank"
    )


class SalaryBand(models.Model):
    """The salary divisions for the various roles"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=300, unique=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00))
    benefit_package = models.JSONField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PaymentDetail(models.Model):
    """Payment details for the staff"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    staff = models.OneToOneField(
        Staff, on_delete=models.CASCADE,
        related_name="staff_payment_details"
        )
    bank_account_number = models.CharField(
        max_length=300, null=True, blank=True
        )
    bank_name = models.CharField(max_length=300, null=True, blank=True)
    bank_branch = models.CharField(max_length=300, null=True, blank=True)
    bank_sort_code = models.CharField(max_length=100, null=True, blank=True)
    bank_iban = models.CharField(max_length=200, null=True, blank=True)
    mobile_money_number = models.CharField(
        max_length=100, null=True, blank=True
        )
    mobile_money_network = models.CharField(
        max_length=200, null=True, blank=True
        )
    salary_band = models.ForeignKey(
        SalaryBand, on_delete=models.CASCADE,
        related_name="salary_band_payment"
        )
    add_cash_allowance_before_tax = models.BooleanField(
        default=False
    )
    social_security_number = models.CharField(
        max_length=300, null=True, blank=True
        )


class PayrollRun(models.Model):
    """Track each batch execution of the payroll"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    period = DateRangeField(default=get_payrun_period)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="payrun_creator"
        )
    total_basic = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00))
    total_chargeable_income = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00))
    status = models.CharField(
        max_length=100, choices=PayrollRunStatuses,
        default="Draft"
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="approval_user",
        null=True, blank=True
        )

    # class Meta:
    #     constraints = [
    #         ExclusionConstraint(
    #             name="exclude_overlapping_period_range",
    #             expressions=[
    #                 ("period", RangeOperators.OVERLAPS)
    #             ],
    #         ),
    #     ]

    def __str__(self):
        return str(self.period)


class Payroll(models.Model):
    """Payroll for the staff"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    payrun = models.ForeignKey(PayrollRun, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Total gross salary before deductions"
    )
    paid_ssnit = models.BooleanField(default=False)
    ssnit_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Amount to be paid as a SSNIT deduction without tier 3",
        null=True, blank=True
    )
    tier_three = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Amount to be paid as Tier 3 if applicable",
        null=True, blank=True
    )
    cash_allowance = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Any allowance that does not attract tax deductions",
        null=True, blank=True
    )
    bonus_income = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Any bonus attracted by contract or performance"
    )
    final_tax_on_bonus = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Total tax on bonus - this tax"
    )
    excess_bonus = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    total_cash_amolument = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Sum of basic salary, cash allowance and excess bonus"
    )
    vehicle_elements = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    non_cash_benefits = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Cost of non cash benefits"
    )
    accessible_income = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Total of salary, bonus and benefits"
    )
    deductible_relief = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    total_relief = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="sum of SSNIT, tier 3 and deductible reliefs"
    )
    chargeable_income = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Difference btn total accessible income and total reliefs"
    )
    tax_deductible = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),)
    overtime_income = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    overtime_tax = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    tax_payable = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="sum of Tax on bonus income, tax deductible and overtime tax"
        )
    severance_paid = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00))
    remarks = models.CharField(max_length=700, null=True, blank=True)


class Receipt(models.Model):
    """Record of PDF receipts given out to payees, students, suppliers, etc"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    purpose = models.JSONField(null=True, blank=True)
    file = models.FileField(upload_to="receipts")
    income = models.ForeignKey(Income, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=100, unique=True)
