"""
Base Serializer for the tracking changes to models
"""
from decimal import Decimal
from rest_framework import serializers
from core.models import (
    DatabaseActionLog, OrganizationDocument,
    OrganizationConfig,
    AcademicTerm,
    AcademicYear
)

from core.utils import (
    CUSTOM_MESSAGES,
    # document_type_choices,
    DocumentTypeChoices,
    # residency_choices,
    ResidencyChoices,
    # employment_type_choices,
    EmploymentType,
    # staff_type_choices,
    StaffType,
    UserType,
    GenderChoices,
    PaymentMethod
    )


class BaseModelSerializer(serializers.ModelSerializer):
    """Serving as the base to audit log"""

    def create(self, validated_data):
        instance = super().create(validated_data)
        # if self.context.get("operation") == "create":
        user = self.context.get("request").user
        self.perform_create_logs(instance, user, "Create")
        return instance

    def update(self, instance, validated_data):
        orginal_data = instance.__dict__.copy()
        updated_instance = super().update(instance, validated_data)
        # if self.context.get("operation") == "update":
        user = self.context.get("request").user
        self.perform_create_logs(
            updated_instance, user, "Update", orginal_data
            )
        return updated_instance

    def delete(self, instance):
        # if self.context.get("operation") == "delete":
        user = self.context.get("request").user
        self.perform_create_logs(
            instance, user, "Delete", instance
            )
        instance.delete

    def perform_create_logs(self, instance, user, action_type, original=None):
        """Add create action to database"""
        model_name = instance.__class__.__name__
        object_id = instance.pk
        message = CUSTOM_MESSAGES.get((model_name, action_type), "")
        updated_fields = []
        if original:
            # print(original)
            for f, v in original.items():
                # print(v, getattr(instance, f))
                if v != getattr(instance, f):
                    updated_fields.append(f)
            if "last_modified" in updated_fields:
                updated_fields.remove("last_modified")
            # message = message.format(updated_fields)
            # print(message.format(updated_fields))
        if action_type == "Create" or action_type == "Delete":
            message = message.format(instance)
        elif action_type == "Update":
            message = message.format(
                ", ".join(map(str, updated_fields)),
                instance
                )

        DatabaseActionLog.objects.create(
            action_type=action_type,
            model_name=model_name,
            object_id=object_id,
            message=message,
            user=user
        )


class DatabaseActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DatabaseActionLog
        fields = [
            "model_name", "message", "timestamp", "user"
        ]


class DashboardSerialaizer(serializers.Serializer):
    total_income = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0)
    )
    total_expenditure = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal(0.00), min_value=Decimal(0.0)
    )
    total_students = serializers.IntegerField()
    recent_activity = serializers.JSONField()
    user = serializers.JSONField()
    total_teachers = serializers.IntegerField()


class OrganizationDocumentSerializer(serializers.ModelSerializer):
    """Serializer for the document upload"""
    description = serializers.CharField(required=False)

    class Meta:
        model = OrganizationDocument
        fields = [
            "id", "date_created", "last_modified",
            "file", "name", "description",
            "file_type",
        ]
        read_only_fields = ["id", "date_created", "last_modified"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["organization"] = user.organization
        return super().create(validated_data)


class OrganizationConfigSerializer(serializers.ModelSerializer):
    """Serializer for the School config"""
    file_types = serializers.ReadOnlyField(
        default=[item.value for item in DocumentTypeChoices]
    )
    residency_status = serializers.ReadOnlyField(
        default=[item.value for item in ResidencyChoices]
    )
    employment_type = serializers.ReadOnlyField(
        default=[item.value for item in EmploymentType]
    )
    staff_type = serializers.ReadOnlyField(
        default=[item.value for item in StaffType]
    )
    user_types = serializers.ReadOnlyField(
        default=[item.value for item in UserType]
    )
    gender_types = serializers.ReadOnlyField(
        default=[item.value for item in GenderChoices]
    )
    payment_methods = serializers.ReadOnlyField(
        default=[item.value for item in PaymentMethod]
    )
    academic_year = serializers.SerializerMethodField()
    academic_term = serializers.SerializerMethodField()

    def get_academic_year(self, instance):
        """return the current academic year"""
        return AcademicYear.objects.get(is_active=True).year

    def get_academic_term(self, instance):
        """Return the current academic term"""
        return AcademicTerm.objects.get(is_active=True).term

    class Meta:
        model = OrganizationConfig
        fields = [
            "id", "date_created", "last_modified",
            "name", "logo", "address", "file_types",
            "academic_year", "academic_term", "currency",
            "residency_status", "employment_type", "staff_type",
            "user_types", "gender_types", "payment_methods",
            "payroll_approval_required"
        ]
