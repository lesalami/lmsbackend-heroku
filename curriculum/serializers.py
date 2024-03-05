"""
Curriculum administration for School,Subject,
"""
# Import required modules
# Order: Builtin, third-party, local modules, etc
import logging
from django.conf import settings
# from django.db.models import Sum
# from django.contrib.auth import get_user_model
# For translating messages for serializer response
# from django.utils.translation import gettext as _

# Rest framework imports here
from rest_framework import serializers

from core.models import (
    AcademicYear, AcademicTerm, Student, Subject,
    Staff, Class, StudentClass,
    ParentOrGuardian, TeacherAssignment, TeacherClass,
    Fee, User, StudentFeeGroup,
    Payment, PaymentReceipt
)

from user.serializers import UserSerializer

from core.serializers import (
    BaseModelSerializer,
    # OrganizationConfigSerializer
)

# Any other local import here
from utils.utils import generate_random_string

# Declare the logger for the file
logger = logging.getLogger(__name__)


class AcademicYearSerializer(BaseModelSerializer):
    """Serializer for the Academic Year"""
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = AcademicYear
        fields = [
            "id", "date_created", "last_modified",
            "year", "is_active", "previous"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class AcademicTermSerializer(BaseModelSerializer):
    """Serializer for the Academic term """
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = AcademicTerm
        fields = [
            "id", "date_created", "last_modified",
            "academic_year", "term", "previous"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class StudentSerializer(BaseModelSerializer):
    """Serializer for the Student model"""
    student_id = serializers.CharField(required=False)
    student_class = serializers.CharField(required=False)
    fee_assigned = serializers.CharField(required=False, write_only=True)
    student_class_obj = serializers.SerializerMethodField()
    guardian = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    date_of_admission = serializers.DateField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    date_of_birth = serializers.DateField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    def get_student_class_obj(self, instance):
        """Get the individual student_class for the student"""
        if StudentClass.objects.filter(student=instance).exists():
            std_class_obj = StudentClass.objects.get(
                student=instance
            )
            fees_obj = ""
            if std_class_obj.fee_assigned:
                fees_obj = std_class_obj.fee_assigned
                fees_obj = StudentFeegroupSerializer(
                    instance=fees_obj,
                    context=self.context
                    ).data
            return {
                "class": std_class_obj.student_class.name,
                "id": std_class_obj.student_class.id,
                "fees_paid": std_class_obj.fee_paid,
                "fees_assigned": fees_obj
                }
        return {}

    def get_guardian(self, instance):
        """Add parent/guardian object"""
        if ParentOrGuardian.objects.filter(students=instance).exists():
            guardian_obj = ParentOrGuardian.objects.get(
                students=instance
            )
            return ParentOrGuardianSerializer(
                instance=guardian_obj, context=self.context
            ).data
        return {}

    class Meta:
        model = Student
        fields = [
            "id", 'date_created', "last_modified",
            "student_id", "first_name", "last_name", "middle_name", "gender",
            "date_of_birth", "date_of_admission",
            "blood_type", "student_class_obj", "image", "address",
            "guardian", "is_active", "student_class", "fee_assigned"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]
        extra_kwargs = {
            "student_class": {"write_only": True},
            "fee_assigned": {"write_only": True}
            }

    def create(self, validated_data):
        std_class = validated_data.get("student_class", None)
        fee_assigned = validated_data.pop("fee_assigned", None)
        if std_class:
            validated_data.pop("student_class")
        if validated_data["date_of_admission"]:
            first_name = validated_data.get("first_name", "")
            last_name = validated_data.get("last_name", "")
            middle_name = validated_data.get("middle_name", "")
            student_name = first_name + " " + middle_name + " " + last_name
            date_of_admission = validated_data["date_of_admission"]
            studentID = generate_random_string(length=5).join(next(zip(
                                *student_name.split()
                                ))).upper() + str(
                                date_of_admission.strftime("%Y")
                                )
            print(studentID)
            validated_data["student_id"] = studentID
        instance = super().create(validated_data)
        if std_class:
            sdc_serializer = StudentClassSerializer(
                data={
                    "student": instance.pk,
                    "student_class": std_class,
                    "fee_assigned": fee_assigned
                    },
                context=self.context
                )
            if sdc_serializer.is_valid():
                sdc_serializer.save()
            else:
                print(sdc_serializer.errors)
        return instance

    def update(self, instance, validated_data):
        std_class = validated_data.pop("student_class", None)
        fee_assigned = validated_data.pop("fee_assigned", None)
        fee_grp = StudentFeeGroup.objects.get(id=fee_assigned)
        updated_instance = super().update(instance, validated_data)
        if std_class:
            if StudentClass.objects.filter(
                    student=updated_instance,
                    student_class=std_class
                    ).exists():
                stc_validated = {
                    "student": updated_instance,
                    "fee_assigned": fee_grp
                }
                StudentClassSerializer().update(
                    instance=StudentClass.objects.get(
                        student=updated_instance,
                        student_class=std_class
                        ),
                    validated_data=stc_validated
                )
            # else:
        if StudentClass.objects.filter(student=instance).exists():
            stc_validated = {
                "student": updated_instance,
                "fee_assigned": fee_grp
            }
            StudentClassSerializer(context=self.context).update(
                instance=StudentClass.objects.get(
                    student=updated_instance
                    ),
                validated_data=stc_validated
            )
        return updated_instance


class StudentSerializerLoc(serializers.ModelSerializer):
    """Student Serializer for the parent model"""
    student_id = serializers.CharField(required=False)
    student_class = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    date_of_admission = serializers.DateField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    date_of_birth = serializers.DateField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    def get_student_class(self, instance):
        """Get the individual student_class for the student"""
        if StudentClass.objects.filter(student=instance).exists():
            return StudentClass.objects.get(
                student=instance
            ).student_class.name
        return {}

    class Meta:
        model = Student
        fields = [
            "id", 'date_created', "last_modified",
            "student_id", "first_name", "last_name", "middle_name", "gender",
            "date_of_birth", "date_of_admission",
            "blood_type", "student_class", "image", "address",
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class ParentOrGuardianSerializer(BaseModelSerializer):
    """Serializer for the parent of Guardian"""
    student_obj = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    def get_student_obj(self, instance):
        """Return students objects"""
        return StudentSerializerLoc(
            instance=instance.students, many=True,
            context=self.context
        ).data

    class Meta:
        model = ParentOrGuardian
        fields = [
            "id", "date_created", "last_modified",
            "students", "full_name", "relationship_with_student",
            "mobile_number", "email", 'home_care_giver_name',
            "name_of_father", "father_telephone", 'name_of_mother',
            "mother_telephone", "address", "student_obj"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class SubjectSerializer(BaseModelSerializer):
    """Serializer for the Subject model"""
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = Subject
        fields = [
            "id", "date_created", "last_modified",
            "name", "subject_id"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class StaffSerializer(BaseModelSerializer):
    """Serializer for the staff model"""
    staff_id = serializers.CharField(required=False)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.CharField(write_only=True)
    user_type = serializers.CharField(write_only=True)
    teacher_class = serializers.ListField(required=False)
    teacher_class_obj = serializers.SerializerMethodField()
    subjects_assigned = serializers.ListField(required=False)
    subject_obj = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    date_of_birth = serializers.DateField(
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    start_date = serializers.DateField(
        required=False,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    user_obj = serializers.SerializerMethodField()

    def get_teacher_class_obj(self, instance):
        """return the classes assigned to teacher"""
        return TeacherClassSerializer(
            instance=instance.assigned_teacher_class,
            many=True, context=self.context
        ).data

    def get_subject_obj(self, instance):
        """Return the subject assigned to the teacher instance"""
        if instance.subject_teacher:
            return TeacherAssignmentSerializer(
                instance=instance.subject_teacher,
                many=True,
                context=self.context
            ).data
        return []

    def get_user_obj(self, instance):
        """Return user object"""
        return UserSerializer(
            instance=instance.user
        ).data

    class Meta:
        model = Staff
        fields = [
            "id", "date_created", "last_modified",
            "first_name", "last_name", "email", "user_type",
            "staff_id", "gender",
            "date_of_birth", "start_date", "is_active",
            "profile_picture", "staff_type", "address",
            "role", "employment_type",
            "teacher_class_obj",
            "teacher_class", "subject_obj", "subjects_assigned",
            "residency_status",
            "user_obj"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]

    def create(self, validated_data):
        """Create a tacher class object here"""
        tacher_class = validated_data.pop("teacher_class", None)
        subject_assigned = validated_data.pop("subjects_assigned", None)
        first_name = validated_data.pop("first_name", None)
        last_name = validated_data.pop("last_name", None)
        email = validated_data.pop("email", None)
        user_type = validated_data.pop("user_type", None)
        organization = self.context["request"].user.organization
        user_instance = User.objects.create(
            email=email, first_name=first_name, last_name=last_name,
            user_type=user_type, organization=organization
        )
        validated_data["user"] = user_instance
        validated_data["staff_id"] = generate_random_string()
        instance = super().create(validated_data)
        if tacher_class:
            for t_data in tacher_class:
                if TeacherClass.objects.filter(
                    teacher=instance.id,
                    teacher_class=t_data
                ).exists():
                    pass
                else:
                    TeacherClass.objects.create(
                        teacher=instance,
                        teacher_class=Class.objects.get(id=t_data)
                    )
        if subject_assigned:
            for subject in subject_assigned:
                if TeacherAssignment.objects.filter(
                    teacher=instance, subject=subject,
                    academic_year__is_active=True,
                    academic_term__is_active=True
                ).exists():
                    pass
                else:
                    current_term = AcademicTerm.objects.get(
                            is_active=True
                        )
                    current_year = AcademicYear.objects.get(
                            is_active=True
                        )
                    TeacherAssignment.objects.create(
                            teacher=instance,
                            subject=Subject.objects.get(pk=subject),
                            academic_year=current_year,
                            academic_term=current_term
                        )
        return instance

    def update(self, instance, validated_data):
        tacher_class = validated_data.get("teacher_class", None)
        subject_assigned = validated_data.get("subjects_assigned", None)
        updated_instance = super().update(instance, validated_data)
        if tacher_class:
            validated_data.pop("teacher_class")
            existing_class = TeacherClass.objects.filter(
                    teacher=updated_instance
                    ).values_list("teacher_class", flat=True)
            if existing_class.exists():
                for obj in existing_class:
                    if obj not in tacher_class:
                        TeacherClass.objects.get(
                            teacher=updated_instance,
                            teacher_class=obj
                        ).delete()
            for t_data in tacher_class:
                if t_data == "undefined":
                    pass
                else:
                    if TeacherClass.objects.filter(
                        teacher=updated_instance,
                        teacher_class=Class.objects.get(pk=t_data)
                    ).exists():
                        pass
                    else:
                        print(t_data)
                        TeacherClass.objects.create(
                            teacher=updated_instance,
                            teacher_class=Class.objects.get(pk=t_data)
                        )
        if subject_assigned:
            validated_data.pop("subjects_assigned")
            existing_subjects = TeacherAssignment.objects.filter(
                teacher=updated_instance,
                academic_year__is_active=True,
                academic_term__is_active=True
                ).values_list("subject", flat=True)
            if existing_subjects.exists():
                for obj in existing_subjects:
                    if obj not in subject_assigned:
                        TeacherAssignment.objects.get(
                            teacher=updated_instance, subject=obj,
                            academic_year__is_active=True,
                            academic_term__is_active=True
                            ).delete()
            for s_data in subject_assigned:
                if s_data == "undefined":
                    pass
                else:
                    if TeacherAssignment.objects.filter(
                        teacher=updated_instance,
                        academic_year__is_active=True,
                        academic_term__is_active=True,
                        subject=Subject.objects.get(pk=s_data)
                    ).exists():
                        pass
                    else:
                        current_term = AcademicTerm.objects.get(
                            is_active=True
                        )
                        current_year = AcademicYear.objects.get(
                            is_active=True
                        )
                        TeacherAssignment.objects.create(
                            teacher=updated_instance,
                            subject=Subject.objects.get(pk=s_data),
                            academic_year=current_year,
                            academic_term=current_term
                        )
        return updated_instance


class TeacherAssignmentSerializer(BaseModelSerializer):
    """Serializer for the subjects asigned to teachers"""
    subject_name = serializers.ReadOnlyField(
        source="subject.name"
    )
    subject_id = serializers.ReadOnlyField(
        source="subject.subject_id"
    )
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = TeacherAssignment
        fields = [
            "id", "date_created", "last_modified",
            "teacher", "subject", "subject_name", "subject_id",
            "academic_year", "academic_term"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class ClassSerializer(BaseModelSerializer):
    """Serializer for the classes/classes/levels"""
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = Class
        fields = [
            "id", "date_created", "last_modified",
            "name",
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class StudentFeegroupSerializer(serializers.ModelSerializer):
    """Serializer for the student fee group"""
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    fees_obj = serializers.SerializerMethodField()

    def get_fees_obj(self, instance):
        """Return a detailed object of fees"""
        return FeeSerializer(
            instance=instance.fees,
            many=True, context=self.context
        ).data

    class Meta:
        model = StudentFeeGroup
        fields = [
            "id", "date_created", "last_modified",
            "fees", "name", "fees_obj"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class StudentClassSerializer(BaseModelSerializer):
    """Serializer for the student to class mapping"""
    # owing = serializers.ReadOnlyField(source="owing")
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    # owing = serializers.SerializerMethodField()

    # def get_paid(self, instance):
    #     """Check if student has fully paid"""
    #     if instance.fee_assigned:
    #         total_fees_assigned = instance.fee_assigned.fees.all().aggregate(
    #             Sum("amount")
    #         )
    #         balance = total_fees_assigned["amount__sum"] - instance.fee_paid
    #         if balance <= 0:
    #             return True
    #     return False

    class Meta:
        model = StudentClass
        fields = [
            "id", "date_created", "last_modified",
            "student", "student_class", "fee_paid",
            "fee_assigned", "fee_owing", "owing",
            "academic_year"
        ]
        read_only_fields = [
            "id", "date_created", "last_modified",
            "owing"
            ]

    def create(self, validated_data):
        academic_year = validated_data.get("academic_year", None)
        if not academic_year:
            validated_data["academic_year"] = AcademicYear.objects.get(
                is_active=True
                )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        academic_year = validated_data.get("academic_year", None)
        if not academic_year:
            validated_data["academic_year"] = AcademicYear.objects.get(
                is_active=True
                )
        return super().update(instance, validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the payment model"""
    student_obj = serializers.SerializerMethodField()
    academic_year_obj = serializers.SerializerMethodField()
    academic_term_obj = serializers.SerializerMethodField()
    fee_obj = serializers.SerializerMethodField()

    def get_student_obj(self, instance):
        if instance.student:
            return StudentSerializer(
                instance=instance.student,
                context=self.context
            ).data
        return ""

    def get_academic_year_obj(self, instance):
        return AcademicYearSerializer(
            instance=instance.academic_year,
            context=self.context
        ).data

    def get_academic_term_obj(self, instance):
        return AcademicTermSerializer(
            instance=instance.academic_term,
            context=self.context
        ).data

    def get_fee_obj(self, instance):
        return FeeSerializer(
            instance=instance.fee,
            context=self.context
        ).data

    class Meta:
        model = Payment
        fields = [
            "id", "date_created", "last_modified",
            "academic_year", "academic_term", "student",
            "fee", "amount", "owing_after_payment",
            "academic_term_obj", "academic_year_obj",
            "student_obj", "fee_obj",
            "payment_method"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]

    def create(self, validated_data):
        user = self.context.get("request").user
        validated_data["user"] = user
        return super().create(validated_data)


class PaymentReceiptSerializer(BaseModelSerializer):
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
        model = PaymentReceipt
        fields = [
            "id", "date_created", "last_modified",
            "purpose", "file", "payment", "receipt_number"
        ]
        read_only_fields = [
            "id", "date_created", "last_modified", "file",
            "receipt_number"
            ]

    def create(self, validated_data):
        return super().create(validated_data)


class TeacherClassSerializer(BaseModelSerializer):
    """Serializer for the teacher to class mapping"""
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    class_obj = serializers.SerializerMethodField()

    def get_class_obj(self, instance):
        """Return the object for the class"""
        return ClassSerializer(
            instance=instance.teacher_class,
            context=self.context
        ).data

    class Meta:
        model = TeacherClass
        fields = [
            "id", "date_created", "last_modified",
            "teacher", "teacher_class", "class_obj"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]


class FeeSerializer(serializers.ModelSerializer):
    """Serializer for the fee model"""
    date_created = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )
    last_modified = serializers.DateTimeField(
        required=False, read_only=True,
        format="%d-%m-%Y", input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = Fee
        fields = [
            "id", "date_created", "last_modified",
            "academic_year", "academic_term",
            "amount", "name"
        ]
        read_only_fields = ["id", "date_created", "last_modified"]
