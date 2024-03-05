"""
All database models go here
"""
from decimal import Decimal
from uuid import uuid4
from django.db import models
# from django.forms.models import model_to_dict
# from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from .utils import (
    # user_type_choices,
    # gender_choices,
    # document_type_choices,
    # staff_type_choices,
    # employment_type_choices,
    # residency_choices,
    UserType,
    GenderChoices,
    DocumentTypeChoices,
    StaffType,
    EmploymentType,
    ResidencyChoices,
    get_upload_path,
    PaymentMethod
)

UserTypes = tuple((item.value, item.name) for item in list(UserType))
GenderChoices_list = tuple(
    (item.value, item.name) for item in list(GenderChoices)
    )
DocumentTypeChoices_list = tuple(
    (item.value, item.name) for item in list(DocumentTypeChoices)
    )
StaffTypes = tuple((item.value, item.name) for item in list(StaffType))
EmploymentTypes = tuple(
    (item.value, item.name) for item in list(EmploymentType)
    )
ResidencyChoices_list = tuple(
    (item.value, item.name) for item in list(ResidencyChoices))
PaymentMethods = tuple((item.value, item.name) for item in list(PaymentMethod))


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("User must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class DatabaseActionLog(models.Model):
    action_type = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=300, null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.action_type} on {self.model_name} at {self.timestamp}"


class OrganizationConfig(models.Model):
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=500)
    logo = models.ImageField(upload_to="organization", null=True, blank=True)
    address = models.CharField(max_length=700, null=True, blank=True)
    currency = models.CharField(
        max_length=150, default="GHC"
    )
    ssnit_rate = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00),
        help_text="Percentage rate for SSNIT without tier 3"
        )
    tier_three = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    add_cash_allowance_before_tax = models.BooleanField(
        default=False
    )
    tax_identification_number = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="TIN for the school/church/business"
    )
    payroll_approval_required = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    user_type = models.CharField(
        max_length=50, choices=UserTypes,
        default="Admin"
    )
    email_confirmed = models.BooleanField(default=False)
    organization = models.ForeignKey(
        OrganizationConfig, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="organizational_user"
        )

    objects = UserManager()

    USERNAME_FIELD = "email"


class AcademicYear(models.Model):
    """Each academic year is a separate entity"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    year = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    previous = models.OneToOneField(
        "self", on_delete=models.CASCADE,
        null=True, blank=True, related_name="next",
        help_text="Pointer to previous academic year"
        )

    def __str__(self):
        return self.year

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)
        if self.__class__.objects.filter(
            is_active=True
        ).exists() and not self.__class__.objects.filter(id=self.id).exists():
            raise ValidationError(
                message='An Academic year is active. Kindly Deactivate',
                code='unique_together',
            )


class AcademicTerm(models.Model):
    """The particular term in the academic year"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    previous = models.OneToOneField(
        "self", on_delete=models.CASCADE,
        null=True, blank=True, related_name="next",
        help_text="Pointer to previous academic term"
        )

    def __str__(self):
        return self.term


class OrganizationDocument(models.Model):
    """Document upload to be later mapped to object(expense/income/etc)"""
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
    file = models.FileField(upload_to=get_upload_path)
    name = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    file_type = models.CharField(
        max_length=300, null=True, blank=True,
        choices=DocumentTypeChoices_list
    )

    def __str__(self):
        return self.name


class Student(models.Model):
    """Student model: Studentid is dob,fn, ln combination"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    student_id = models.CharField(
        max_length=100, null=True, blank=True, unique=True
        )
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=300, null=True, blank=True)
    gender = models.CharField(
        max_length=100, choices=GenderChoices_list, default="Male"
        )
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_admission = models.DateField(null=True, blank=True)
    blood_type = models.CharField(max_length=150, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="students", null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def studentclass_object(self):
        return StudentClass.objects.get(student=self)

    @studentclass_object.setter
    def studentclass_fee(self, new_value):
        std_fee = StudentClass.objects.get(student=self)
        std_fee.fee_paid = new_value
        std_fee.save()


class ParentOrGuardian(models.Model):
    """Parent/guardian of the Student"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    students = models.ManyToManyField(
        Student, blank=True
        )
    full_name = models.CharField(max_length=500, null=True, blank=True)
    relationship_with_student = models.CharField(max_length=400)
    mobile_number = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    home_care_giver_name = models.CharField(
        max_length=400, null=True, blank=True
        )
    name_of_father = models.CharField(max_length=400)
    father_telephone = models.CharField(max_length=100, null=True, blank=True)
    name_of_mother = models.CharField(max_length=400)
    mother_telephone = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.full_name


class Subject(models.Model):
    """Each subject available in the school"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    subject_id = models.CharField(max_length=150)
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Staff(models.Model):
    """All employees (teaching and non-teaching) records"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=200, unique=True)
    gender = models.CharField(
        max_length=150, choices=GenderChoices_list, default="Male"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    profile_picture = models.ImageField(
        upload_to="staff", null=True, blank=True)
    staff_type = models.CharField(
        max_length=100, choices=StaffTypes,
        default="Teaching"
    )
    address = models.CharField(max_length=300, null=True, blank=True)
    role = models.CharField(
        max_length=500, default="Teacher",
        help_text="Position/Role"
        )
    employment_type = models.CharField(
        max_length=200, choices=EmploymentTypes,
        default="Full_Time"
    )
    residency_status = models.CharField(
        max_length=200, choices=ResidencyChoices_list
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name_plural = "Staff"


class TeacherAssignment(models.Model):
    """Teacher assigned to subjects"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    teacher = models.ForeignKey(
        Staff, on_delete=models.CASCADE,
        related_name="subject_teacher"
        )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    academic_term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher.user.first_name} - {self.subject.name}"


class Fee(models.Model):
    """School fees model to be applied on a class"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    academic_term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Class(models.Model):
    """Students' classes: Each class/levels is valid within an academic year"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=300)
    # academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    # academic_term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    # school_fee = models.ForeignKey(
    #     Fee, on_delete=models.SET_NULL, null=True, blank=True
    #     )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "Classes"
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_classes"
                )
        ]


class StudentFeeGroup(models.Model):
    """A combination of fees to apply to a student """
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    fees = models.ManyToManyField(Fee)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class StudentClass(models.Model):
    """Each student->Class and fee mapping"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE,
        null=True
        )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name="student_in_class"
        )
    student_class = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="class_of_student"
        )
    fee_assigned = models.ForeignKey(
        StudentFeeGroup, on_delete=models.CASCADE,
        null=True, blank=True
        )
    fee_paid = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    fee_owing = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    owing = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Calculate the new owing after the payment
        if self.fee_assigned:
            total_fees_assigned = self.fee_assigned.fees.all().aggregate(
                models.Sum("amount")
            )
            if total_fees_assigned["amount__sum"] < self.fee_paid:
                raise ValidationError(
                    message="Payment amount is greater than the fee amount",
                    code="payment_error",
                )
            self.fee_owing = total_fees_assigned["amount__sum"] - self.fee_paid
            if self.fee_paid < total_fees_assigned["amount__sum"]:
                self.owing = True
            else:
                self.owing = True
        else:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.first_name} - {self.student_class.name}"

    class Meta:
        verbose_name_plural = "Student Classes"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "student_class"],
                name="unique_student_classes"
                )
        ]


class Payment(models.Model):
    """All payments for any service by students"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    academic_term = models.ForeignKey(
        AcademicTerm, on_delete=models.CASCADE,
        null=True, blank=True
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    owing_after_payment = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal(0.00)
    )
    payment_method = models.CharField(
        max_length=200, choices=PaymentMethods,
        default="Bank"
    )

    def __str__(self):
        return f"Payment for {self.student}"

    def save(self, *args, **kwargs):
        # Calculate the new balance after the payment
        if self.fee.amount < self.amount:
            return "Payment amount is greater than the fee amount"
        print(hasattr(self.student, "studentclass_object"))
        totalassigned = self.student.studentclass_object.fee_assigned.fees.all(

        ).aggregate(
                models.Sum("amount")
            )
        amount_paid = self.amount + self.student.studentclass_object.fee_paid
        self.owing_after_payment = totalassigned["amount__sum"] - amount_paid

        # Update the current balance of the student
        print(amount_paid)
        self.student.save()
        self.student.studentclass_fee = amount_paid
        # self.student.studentclass_object.save()

        super().save(*args, **kwargs)


class PaymentReceipt(models.Model):
    """Record of PDF receipts given out to payees, students, suppliers, etc"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    purpose = models.JSONField(null=True, blank=True)
    file = models.FileField(upload_to="payments/receipts")
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=100, unique=True)


class TeacherClass(models.Model):
    """Each teacher->class Mapping"""
    id = models.UUIDField(
        primary_key=True,
        unique=True, db_index=True,
        default=uuid4, editable=False
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    teacher = models.ForeignKey(
        Staff, on_delete=models.CASCADE,
        related_name="assigned_teacher_class"
        )
    teacher_class = models.ForeignKey(Class, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher.user.first_name} - {self.teacher_class.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "teacher_class"],
                name="unique_teacher_classes"
                )
        ]
