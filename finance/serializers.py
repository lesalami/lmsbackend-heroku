"""
Finance serializer including invoice, income and expenditure
"""
import logging
from decimal import Decimal
from rest_framework import serializers

from core.models import Staff

from finance.models import (
    TaxConfig,
    Tax,
    IncomeType, Income,
    ExpenditureType, Expenditure,
    AcademicTerm, AcademicYear,
    Supplier,
    SalaryBand,
    PaymentDetail,
    Payroll,
    Receipt,
    PayrollRun
)
from django.conf import settings

from core.serializers import (
    BaseModelSerializer, OrganizationDocumentSerializer
)

from curriculum.serializers import (
    StudentSerializer,
    StaffSerializer
)

from utils.finance import (
    summary_tax,
    update_chargeable,
    update_payrun_basic
    )


logger = logging.getLogger(__name__)


class TaxConfigSerializer(BaseModelSerializer):
    """Serializer for the tax config"""
    tax_percent = serializers.IntegerField(required=False)
    flat_tax_amount = serializers.IntegerField(required=False)
    date_created = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = TaxConfig
        fields = [
            "id", "date_created", "last_modified",
            "name", "tax_percent", "flat_tax_amount"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["organization"] = user.organization
        return super().create(validated_data)


class TaxSerializer(BaseModelSerializer):
    """Serializer for the tax object"""
    date_created = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    tax_config_obj = serializers.SerializerMethodField()

    def get_tax_config_obj(self, instance):
        """Return the details of the tax config"""
        return TaxConfigSerializer(
            instance=instance.tax_config,
            context=self.context
        ).data

    class Meta:
        model = Tax
        fields = [
            "id", "date_created", "last_modified",
            "tax_config", "tax_amount", "tax",
            "gross_amount", "tax_config_obj"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class SupplierSerializer(BaseModelSerializer):
    """Serializer for the supplier"""
    date_created = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = Supplier
        fields = [
            "id", "date_created", "last_modified",
            "full_name", "company_name", "address", "telephone",
            "image"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class IncomeTypeSerializer(BaseModelSerializer):
    """Serializer for the types of income that might arise"""
    date_created = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    last_modified = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )

    class Meta:
        model = IncomeType
        fields = [
            "id", "date_created", "last_modified",
            "name"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class IncomeSerializer(BaseModelSerializer):
    """Serializer for the income model"""
    date_created = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    last_modified = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    income_date = serializers.DateField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    academic_year = serializers.ReadOnlyField(
        source="academic_year.year"
    )
    academic_term = serializers.ReadOnlyField(
        source="academic_term.term"
    )
    academic_year_id = serializers.ReadOnlyField(
        source="academic_year.id"
    )
    academic_term_id = serializers.ReadOnlyField(
        source="academic_term.id"
    )
    uploaded_file_obj = serializers.SerializerMethodField()
    student_obj = serializers.SerializerMethodField()
    income_type_obj = serializers.SerializerMethodField()
    tax_obj = serializers.SerializerMethodField()
    receipt_obj = serializers.SerializerMethodField()
    income_time = serializers.SerializerMethodField()
    income_date = serializers.SerializerMethodField()

    def get_uploaded_file_obj(self, instance):
        """Get the uploaded file object"""
        return OrganizationDocumentSerializer(
            instance=instance.uploaded_file,
            many=True,
            context=self.context
        ).data

    def get_student_obj(self, instance):
        """Return the student object"""
        if instance.student:
            return StudentSerializer(
                instance=instance.student,
                context=self.context
            ).data
        return {}

    def get_income_type_obj(self, instance):
        """Return the details of income type"""
        return IncomeTypeSerializer(
            instance=instance.income_type,
            context=self.context
        ).data

    def get_tax_obj(self, instance):
        """Return the tax object"""
        return TaxSerializer(
            instance=instance.tax,
            context=self.context,
            many=True
        ).data

    def get_receipt_obj(self, instance):
        """Get the receipt object"""
        try:
            receipt_data = Receipt.objects.get(income=instance)
            return ReceiptSerializer(
                instance=receipt_data,
                context=self.context
            ).data
        except Receipt.DoesNotExist:
            return {}

    def get_income_time(self, instance):
        """Get the time from the date created"""
        return instance.date_created.strftime("%I:%M %p")

    def get_income_date(self, instance):
        return instance.income_date.strftime("%d %B %Y")

    class Meta:
        model = Income
        fields = [
            "id", "date_created", "last_modified",
            "income_type", "academic_year", "academic_term",
            "academic_term_id", "academic_year_id",
            "amount", "purpose", "payer", "student",
            "income_date", "income_time",
            "uploaded_file", "tax", "uploaded_file_obj", "student_obj",
            "income_type_obj", "tax_obj", "receipt_obj",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        acad_year = AcademicYear.objects.get(is_active=True)
        acad_term = AcademicTerm.objects.get(is_active=True)
        validated_data["user"] = user
        validated_data["academic_year"] = acad_year
        validated_data["academic_term"] = acad_term
        return super().create(validated_data)


class ExpenditureTypeSerializer(BaseModelSerializer):
    """Serializer for the expenditure types"""
    date_created = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    last_modified = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )

    class Meta:
        model = ExpenditureType
        fields = [
            "id", "date_created", "last_modified",
            "name"
        ]


class ExpenditureSerializer(BaseModelSerializer):
    """Serializer for the expenditure model"""
    date_created = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    last_modified = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    expense_date = serializers.DateField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    expenditure_type_name = serializers.ReadOnlyField(
        source="expenditure_type.name"
    )
    academic_year = serializers.ReadOnlyField(
        source="academic_year.year"
    )
    academic_term = serializers.ReadOnlyField(
        source="academic_term.term"
    )
    academic_year_id = serializers.ReadOnlyField(
        source="academic_year.id"
    )
    academic_term_id = serializers.ReadOnlyField(
        source="academic_term.id"
    )
    user_obj = serializers.SerializerMethodField()
    uploaded_file_obj = serializers.SerializerMethodField()
    expenditure_type_obj = serializers.SerializerMethodField()
    supplier_obj = serializers.SerializerMethodField()

    def get_expenditure_type_obj(self, instance):
        """Return the expenditure type"""
        return ExpenditureTypeSerializer(
            instance=instance.expenditure_type,
            context=self.context,
        ).data

    def get_uploaded_file_obj(self, instance):
        """Get the uploaded file object"""
        return OrganizationDocumentSerializer(
            instance=instance.uploaded_file,
            many=True,
            context=self.context
        ).data

    def get_user_obj(self, instance):
        """Add the user object here"""
        return {
            "id": instance.user.id,
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name,
            "email": instance.user.email
        }

    def get_supplier_obj(self, instance):
        """Get the full details of supplier"""
        return SupplierSerializer(
            instance=instance.supplier,
            context=self.context,
        ).data

    class Meta:
        model = Expenditure
        fields = [
            "id", "date_created", "last_modified",
            "amount", "expenditure_type", "expenditure_type_name",
            "expenditure_type_obj", "uploaded_file_obj",
            "user_obj", "purpose", "invoice",
            "academic_year", "academic_term", "academic_term_id",
            "academic_year_id", "expense_date",
            "uploaded_file", "supplier", "payment_type", "supplier_obj"
        ]
        read_only_fields = [
            "id", "date_created", "last_modified",
            "academic_year", "academic_term",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        acad_year = AcademicYear.objects.get(is_active=True)
        acad_term = AcademicTerm.objects.get(is_active=True)
        validated_data["user"] = user
        validated_data["academic_year"] = acad_year
        validated_data["academic_term"] = acad_term
        return super().create(validated_data)


class SalaryBandSerializer(BaseModelSerializer):
    """Serializer for the salary band of staff"""
    date_created = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    last_modified = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )

    class Meta:
        model = SalaryBand
        fields = [
            "id", "date_created", "last_modified",
            "name", "amount", "benefit_package"
        ]
        read_only_fields = [
            "id", "date_created", "last_modified",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class PaymentDetailSerializer(BaseModelSerializer):
    """Serializer for the payment details of staff"""
    date_created = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    last_modified = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    staff_obj = serializers.SerializerMethodField()
    salary_band_obj = serializers.SerializerMethodField()

    def get_staff_obj(self, instance):
        """Staff details"""
        return StaffSerializer(
            instance=instance.staff,
            context=self.context
        ).data

    def get_salary_band_obj(self, instance):
        """Return the salary band object"""
        return SalaryBandSerializer(
            instance=instance.salary_band,
            context=self.context
        ).data

    class Meta:
        model = PaymentDetail
        fields = [
            "id", "date_created", "last_modified",
            "staff", "bank_account_number",
            "bank_name", "bank_branch", "bank_sort_code",
            "bank_iban", "mobile_money_number", "mobile_money_network",
            "salary_band", "social_security_number", "staff_obj",
            "salary_band_obj"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class PayrollRunSerializer(BaseModelSerializer):
    """Serializer for the payroll run batch"""
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y",
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y",
    )
    total_basic = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False, read_only=True)
    total_chargeable_income = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False, read_only=True
    )
    payroll = serializers.SerializerMethodField()
    status = serializers.CharField(required=False, read_only=True)

    def get_payroll(self, instance):
        """Get a list of payrolls under this run"""
        payrolls = Payroll.objects.filter(payrun=instance)
        if payrolls:
            return PayrollSerializer(
                instance=payrolls, many=True,
                context=self.context
            ).data
        return []

    class Meta:
        model = PayrollRun
        fields = [
            "id", "date_created", "last_modified",
            "period", "total_basic", "total_chargeable_income",
            "status", "approved_by", "payroll"
        ]
        read_only_fields = [
            "id", "date_created", "last_modified",
            "total_chargeable_income", "approved_by"
            ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        payroll_run = super().create(validated_data)
        ssnit_rate = user.organization.ssnit_rate
        tier_three = user.organization.tier_three
        all_staff = Staff.objects.filter(
            is_active=True,
            user__organization=user.organization
            )
        result = []
        total_chargeable = 0
        total_basic = 0
        try:
            for staff in all_staff:
                # print(staff)
                payroll_calc = summary_tax(staff.id, ssnit_rate, tier_three)
                if payroll_calc is not None:
                    payroll_calc["payrun"] = payroll_run
                    instance = Payroll.objects.create(
                        staff=staff,
                        **payroll_calc
                    )
                    total_chargeable += payroll_calc["chargeable_income"]
                    total_basic += payroll_calc["basic_salary"]
                    result.append(instance)
            created_run = PayrollRun.objects.get(id=payroll_run.id)
            created_run.total_chargeable_income = total_chargeable
            created_run.total_basic = total_basic
            created_run.save()
        except Exception as e:
            try:
                PayrollRun.objects.get(id=payroll_run.id).delete()
            except Exception as ee:
                return str(ee)
            return str(e)
        return created_run


class PayrollSerializer(BaseModelSerializer):
    """Payroll generation"""
    date_created = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    last_modified = serializers.DateTimeField(
        required=False,
        format="%d-%m-%Y",
    )
    staff = serializers.CharField(required=False)
    basic_salary = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    paid_ssnit = serializers.BooleanField(default=False)
    ssnit_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    tier_three = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    cash_allowance = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    bonus_income = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    final_tax_on_bonus = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    excess_bonus = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    total_cash_amolument = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    vehicle_elements = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    non_cash_benefits = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    accessible_income = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    deductible_relief = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    total_relief = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    overtime_income = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    overtime_tax = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    tax_payable = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    severance_paid = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0),
        required=False)
    remarks = serializers.CharField(required=False)

    status = serializers.SerializerMethodField()

    def get_status(self, instance):
        """Get status from payrun execution"""
        return instance.payrun.status

    class Meta:
        model = Payroll
        fields = [
            "id", "date_created", "last_modified",
            "staff", "basic_salary", "paid_ssnit",
            "ssnit_amount", "tier_three", "cash_allowance",
            "bonus_income", "final_tax_on_bonus", "excess_bonus",
            "total_cash_amolument", "vehicle_elements", "non_cash_benefits",
            "accessible_income", "deductible_relief", "total_relief",
            "chargeable_income", "tax_deductible", "overtime_income",
            "overtime_tax", "tax_payable", "severance_paid", "remarks",
            "payrun", "status"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]

    def update(self, instance, validated_data):
        updated_obj = super().update(instance, validated_data)
        update_chargeable(updated_obj.payrun.id)
        update_payrun_basic(updated_obj.payrun.id)
        return updated_obj


class ReceiptSerializer(BaseModelSerializer):
    """Serializer for the receipt model"""
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y",
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y",
    )

    class Meta:
        model = Receipt
        fields = [
            "id", "date_created", "last_modified",
            "purpose", "file", "income", "receipt_number"
        ]
        read_only_fields = [
            "id", "date_created", "last_modified", "file",
            "receipt_number"
            ]

    def create(self, validated_data):
        return super().create(validated_data)


class TransactionSerializer(serializers.Serializer):
    """General transaction serializer"""
    date_created = serializers.DateTimeField(format="%d-%m-%Y")
    id = serializers.UUIDField()
    amount = serializers.IntegerField()
    amount = serializers.CharField()
    user = serializers.CharField()
    model_type = serializers.CharField()
    student = serializers.UUIDField(required=False)

    class Meta:
        fields = [
            "id", "date_created", "user", "amount", "purpose",
            "model_type",
            "student"
        ]
