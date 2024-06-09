"""
Views for the Curriculum API.
"""
import os
from datetime import datetime, timedelta
from django.core.files import File
from django.http import Http404
from django.core.exceptions import ValidationError
from django.db.models import Sum, Case, When, Value, IntegerField
import logging
from rest_framework import (
    # generics,
    # authentication,
    permissions,
    status,
    viewsets,
    filters
)

# from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend

from curriculum.serializers import (
    AcademicYearSerializer, StudentSerializer,
    ParentOrGuardianSerializer, SubjectSerializer,
    StaffSerializer,
    ClassSerializer, AcademicTermSerializer,
    TeacherAssignmentSerializer, StudentClassSerializer,
    TeacherClassSerializer, FeeSerializer,
    StudentFeegroupSerializer, PaymentSerializer,
    PaymentReceiptSerializer, FeeArrearSerializer,
    ArrearPaymentSerializer,
)
from core.models import (
    AcademicYear, Student, ParentOrGuardian,
    Staff, Subject, Class,
    AcademicTerm, TeacherAssignment, StudentClass,
    TeacherClass, Fee, StudentFeeGroup, Payment,
    PaymentReceipt, FeeArrear, ArrearPayment,
)

from utils.pagination import StandardResultsSetPagination
from utils.pdf_generate import convert_html_to_pdf
from core.utils import StaffType
from utils.custom_permissions import SchoolAdmin
from utils.fee_payment import (
    fee_payment_breakdown, payment_aggregate,
    arrears_payment_aggregate
)
from utils.utils import generate_random_receipt_number


logger = logging.getLogger(__name__)


class AcademicYearView(viewsets.ModelViewSet):
    """API viewsets for the Academic Year"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AcademicYearSerializer
    queryset = AcademicYear.objects.filter(
        is_active=True
        ).order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]


class AcademicTermView(viewsets.ModelViewSet):
    """API viewsets for the Academic Year"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AcademicTermSerializer
    queryset = AcademicTerm.objects.filter(
        academic_year__is_active=True
    )
    http_method_names = ["get", "post", "patch", "delete"]


class StudentView(viewsets.ModelViewSet):
    """API View for Students"""
    permissions = {
        'default': (permissions.IsAuthenticated,),
        'partial_update': (SchoolAdmin,),
        'update': (SchoolAdmin,)
        }
    serializer_class = StudentSerializer
    queryset = Student.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'date_created', 'gender',
        'is_active'
        ]
    search_fields = [
        'first_name', 'last_name', 'middle_name',
        'student_id'
        ]

    def get_permissions(self):
        self.permission_classes = self.permissions.get(
            self.action, self.permissions['default']
            )
        return super().get_permissions()

    def filter_queryset(self, queryset):
        class_id = self.request.GET.get("student_class", None)
        if class_id:
            print(class_id)
            students_in_the_class = queryset.annotate(
                class_id_count=Sum(
                    Case(
                        When(
                            student_in_class__student_class=class_id,
                            then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                )
            )
            student_filtered = students_in_the_class.filter(
                class_id_count__gt=0
            )
            return super().filter_queryset(student_filtered)
        return super().filter_queryset(queryset)

    @action(
            detail=False, methods=["get"],
            url_path="metrics", url_name="metrics")
    def metrics(self, request, *args, **kwargs):
        """Return some metrics on students"""
        current_year = AcademicYear.objects.get(is_active=True)
        total_students = StudentClass.objects.filter(
            academic_year=current_year
        ).values_list("student").count()
        previous_students = 0
        if current_year.previous:
            previous_students = StudentClass.objects.filter(
                academic_year=current_year.previous
            ).values_list("student").count()
        percent_change = 100
        if previous_students is not None and previous_students > 0:
            percent_change = (
                total_students-previous_students)/previous_students
        else:
            previous_students = 0
        change_type = "increase"
        if percent_change < 0:
            change_type = "decrease"
        male_students_count = StudentClass.objects.filter(
            academic_year=current_year,
            student__is_active=True,
            student__gender="Male",
        ).values_list("student").count()
        female_students_count = StudentClass.objects.filter(
            academic_year=current_year,
            student__is_active=True,
            student__gender="Female",
        ).values_list("student").count()
        return Response(
            {
                "total_students": str(total_students),
                "male": male_students_count,
                "female": female_students_count,
                "change": str(abs(percent_change)) + "%",
                "change_type": change_type
            },
            status=status.HTTP_200_OK
        )

    @action(
            detail=True, methods=["get"],
            url_path="finance", url_name="finance")
    def finance(self, request, pk=None):
        """Return financial data on the student"""
        try:
            student_class = StudentClass.objects.get(
                student=self.get_object(),
                student_class__academic_year__is_active=True
            )
            total_fees = student_class.fee_assigned
            total_paid = student_class.fee_paid
            owing = student_class.owing
            fee_group = StudentFeegroupSerializer(
                total_fees, context={"request": request}
                ).data
            return Response({
                "owing": owing,
                "fee_group": fee_group,
                "total_amount_paid": total_paid
            }, status=status.HTTP_200_OK)
        except StudentFeeGroup.DoesNotExist:
            fee_group = {}
            return Response({
                "owing": owing,
                "fee_group": fee_group,
                "total_amount_paid": total_paid
            }, status=status.HTTP_404_NOT_FOUND)
        except StudentClass.DoesNotExist:
            return Response({
                "message": "Student does not have have a class assignment"
            }, status=status.HTTP_404_NOT_FOUND)

    @action(
            detail=True, methods=["get"],
            url_path="fees", url_name="fees")
    def student_fee_assigned(self, request, pk=None):
        """Fee assigned, paid, owing"""
        acad_term = AcademicTerm.objects.get(is_active=True).term,
        if not acad_term:
            acad_term = ""
        try:
            student_class = StudentClass.objects.get(
                student=self.get_object(),
                academic_year__is_active=True
            )
            if student_class.fee_assigned:
                fees = student_class.fee_assigned.fees.all().order_by("date_created")
                fee_paid = Payment.objects.filter(
                    student=self.get_object(),
                    academic_year__is_active=True
                ).aggregate(Sum("amount"))
                fee_owing = fees.aggregate(Sum("amount"))["amount__sum"] - fee_paid["amount__sum"]
                if fees:
                    fee_list = []
                    for fee in fees:
                        amount_paid = Payment.objects.filter(
                            fee=fee,
                            student=self.get_object()
                            ).aggregate(
                            Sum("amount")
                        )
                        fee_list.append({
                            "fee_id": fee.id,
                            "fee_name": fee.name,
                            "academic_year": fee.academic_year.year,
                            "amount": fee.amount,
                            "amount_paid": amount_paid["amount__sum"]
                        })
                    result = {
                        "fees": fee_list,
                        "academic_year": AcademicYear.objects.get(
                            is_active=True).year,
                        "academic_term": AcademicTerm.objects.get(
                            is_active=True).term,
                        "amount_paid": fee_paid["amount__sum"],
                        "amount_owing": fee_owing,
                        "owing": fee_owing > 0
                    }
                    return Response(
                        result,
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response({
                        "message": "No fees assigned to the student"
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"message": "Student does not have a fee assignment"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as pay_except:
            return Response(
                {"message": pay_except.__str__()},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(
           detail=False, methods=["POST"],
           url_path="fee-group-assignment", url_name="fee-group-assignment"
    )
    def assigned_fee_group_to_students(self, request, *args, **kwargs):
        """Assign fee group to multiple students"""
        try:
            student_ids = request.data["students"]
            fee_group = request.data["fee_group"]
            student_fee_group = StudentFeeGroup.objects.get(id=fee_group)
            students = self.queryset.filter(id__in=student_ids)
            for student in students:
                student_class = StudentClass.objects.get(
                    academic_year__is_active=True,
                    student=student
                )
                student_class.fee_assigned = student_fee_group
                student_class.save()
            return Response(
                {"message": "Successfully added fee group to Students"},
                status=status.HTTP_200_OK)
        except StudentClass.DoesNotExist:
            return Response({
                "message": "Student does not have a class in the current academic year"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({
                "message": exc.__str__()
            }, status.HTTP_400_BAD_REQUEST)


class ParentOrGuardianView(viewsets.ModelViewSet):
    """API View for Parent or Guardian"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ParentOrGuardianSerializer
    queryset = ParentOrGuardian.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'date_created'
        ]
    search_fields = [
        'full_name', 'home_care_giver_name', 'name_of_father',
        'name_of_mother', 'students__first_name',
        'students__last_name'
        ]


class StaffView(viewsets.ModelViewSet):
    """API View for the Teacher """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StaffSerializer
    queryset = Staff.objects.filter().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'date_created', 'gender', 'staff_type',
        'employment_type', 'is_active'
        ]
    search_fields = [
        'user__first_name', 'user__last_name', 'staff_id',
        ]

    def get_queryset(self):
        return self.queryset.filter(
            user__organization=self.request.user.organization
            )

    @action(
            detail=False, methods=["get"],
            url_path="metrics", url_name="metrics")
    def metrics(self, request, *args, **kwargs):
        """Return some metrics on teachers"""
        total_teachers = Staff.objects.filter(
            is_active=True, staff_type=StaffType.Teaching
            ).count()
        total_teachers_non = Staff.objects.filter(
            is_active=True, staff_type=StaffType.Non_Teaching
            ).count()
        return Response(
            {
                "total_teachers": total_teachers,
                "total_non_teaching_staff": total_teachers_non,
            },
            status=status.HTTP_200_OK
        )


class SubjectView(viewsets.ModelViewSet):
    """API View for the Subject"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'date_created'
        ]
    search_fields = [
        'name', 'subject_id',
        ]


# class NonTeachingStaffView(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = NonTeachingStaffSerializer
#     queryset = NonTeachingStaff.objects.all()
#     http_method_names = ["get", "post", "patch", "delete"]
#     pagination_class = StandardResultsSetPagination
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     filterset_fields = [
#         'is_active'
#         ]
#     search_fields = [
#         'full_name', 'designation', 'phone_number',
#         ]


class ClassView(viewsets.ModelViewSet):
    """API View for the Class View"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassSerializer
    queryset = Class.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'date_created'
        ]
    search_fields = [
        'name', 'academic_year__year', 'academic_term__term'
        ]


class StudentFeeGroupView(viewsets.ModelViewSet):
    """API View for the student fee grup"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentFeegroupSerializer
    queryset = StudentFeeGroup.objects.all()
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination


class TeacherAssignmentView(viewsets.ModelViewSet):
    """API view for the teacher to subject mapping"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeacherAssignmentSerializer
    queryset = TeacherAssignment.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination


class StudentClassView(viewsets.ModelViewSet):
    """API View for the student to class mapping"""
    permissions = {
        'default': (permissions.IsAuthenticated,),
        'partial_update': (SchoolAdmin,),
        'update': (SchoolAdmin,)
        }
    serializer_class = StudentClassSerializer
    queryset = StudentClass.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        self.permission_classes = self.permissions.get(
            self.action, self.permissions['default']
            )
        return super().get_permissions()

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            return Response(
                {"message": exc.message, "error_message": "Validation Error"},
                status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)


class TeacherClassView(viewsets.ModelViewSet):
    """API View for the teacher to class mapping"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeacherClassSerializer
    queryset = TeacherClass.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination


class FeeView(viewsets.ModelViewSet):
    """API Views for the Fee model"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FeeSerializer
    queryset = Fee.objects.filter(
        academic_year__is_active=True,
        academic_term__is_active=True
    )
    http_method_names = ["get", "post", "patch", "delete"]


class PaymentView(viewsets.ModelViewSet):
    """API View for Fee Payment"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer
    queryset = Payment.objects.filter(
        academic_year__is_active=True
    )
    http_method_names = ["get", "post"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'payment_method'
        ]
    search_fields = [
        'student__first_name', 'student__last_name', 'academic_year__year',
        'academic_term__term'
        ]

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            return Response(
                {"message": exc.message, "error_message": "Validation Error"},
                status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)

    @action(
            detail=False, methods=["get"],
            url_path="metrics", url_name="metrics")
    def metrics(self, request, *args, **kwargs):
        """Return some metrics on Payment"""
        current_year = AcademicYear.objects.get(is_active=True)
        current_payment = self.queryset.filter(
            academic_year__is_active=True
        ).aggregate(Sum("amount")).get("amount__sum")
        previous_payment = 0
        if current_year.previous:
            previous_payment = self.queryset.filter(
                academic_year=current_year.previous
            ).aggregate(Sum("amount")).get("amount__sum")
        percent_change = 100
        if previous_payment is not None and previous_payment > 0:
            percent_change = (
                current_payment-previous_payment)/previous_payment
        else:
            previous_payment = 0
        change_type = "increase"
        if percent_change < 0:
            change_type = "decrease"
        monthly_payment = self.queryset.filter(
            date_created__year=datetime.now().year,
            date_created__month=datetime.now().month
            ).aggregate(Sum("amount"))
        start_week = datetime.today() - timedelta(datetime.today().weekday())
        end_week = start_week + timedelta(7)
        print(start_week, end_week)
        weekly_payment = self.queryset.filter(
            date_created__range=[start_week, end_week]
        ).aggregate(Sum("amount"))
        return Response(
            {
                "total_payment": current_payment,
                "change": str(abs(percent_change)) + "%",
                "change_type": change_type,
                "monthly_payment": monthly_payment["amount__sum"],
                "weekly_payment": weekly_payment["amount__sum"]
            },
            status=status.HTTP_200_OK
        )

    @action(
            detail=True, methods=["get"],
            url_path="receipt", url_name="receipt")
    def get_receipt(self, request, pk=None):
        """Generate and retun a PDF receipt given Payment ID"""
        arrear_payment_map = []
        receipt_number = generate_random_receipt_number()
        try:
            arrear_paid_obj = None
            payment_data = self.get_object()
            fee_arrears = FeeArrear.objects.filter(
                student=payment_data.student,
                arrear_balance__gt=0
            )
            for each_arrear in fee_arrears:
                arrear_payment_map.append(
                    {
                        "arrear_type": "Arrears",
                        "fee_amount": each_arrear.amount,
                        "amount_paid": ArrearPayment.objects.filter(
                            fee_arrear=each_arrear
                            ).aggregate(Sum("amount"))["amount__sum"],
                        "amount_owing": each_arrear.arrear_balance,
                    }
                )
        except Http404:
            arrear_paid_obj = ArrearPayment.objects.get(id=pk)
            fee_arrears = FeeArrear.objects.filter(
                student=arrear_paid_obj.fee_arrear.student,
                arrear_balance__gt=0
                )
            for each_arrear in fee_arrears:
                arrear_payment_map.append(
                    {
                        "arrear_type": "Arrears",
                        "fee_amount": each_arrear.amount,
                        "amount_paid": ArrearPayment.objects.filter(
                            fee_arrear=each_arrear
                            ).aggregate(Sum("amount"))["amount__sum"],
                        "amount_owing": each_arrear.arrear_balance
                    }
                )
            payment_data = self.queryset.filter(student=arrear_paid_obj.fee_arrear.student)
        org = request.user.organization
        data_dict = {
            "organization_name": org.name,
            "organization_address": "" if org.address is None else org.address,
            "organization_contact": "" if org.contact_number is None else org.contact_number,
        }
        if payment_data:
            try:
                receipt = PaymentReceipt.objects.get(
                    payment__id=payment_data.id
                    )
                result = PaymentReceiptSerializer(
                        instance=receipt, context={"request": request}
                        )
                return Response(
                    result.data,
                    status=status.HTTP_200_OK
                )
            except PaymentReceipt.DoesNotExist:
                try:
                    all_payments = fee_payment_breakdown(payment_data.student.id)
                    amount_assigned, amount_paid, amount_owing = payment_aggregate(
                        payment_data.student.id
                    )
                    purpose = f"Payment for {payment_data.fee.name}"
                    data_dict.update({
                        "cashier_name": payment_data.user.__str__(),
                        "payment_mode": "" if payment_data.payment_method is None else payment_data.payment_method,
                        "cheque_number": "" if payment_data.cheque_number is None else payment_data.cheque_number,
                        "payer": payment_data.student.__str__(),
                        "date": payment_data.date_created.strftime("%d-%m-%Y"),
                        "receipt_number": receipt_number[:8],
                        "client_reference": payment_data.student.__str__(),
                        "description": f"Payment for {payment_data.fee.name}",
                        "income_amount": payment_data.amount,
                        "payment_time": payment_data.date_created.strftime(
                            "%I:%M %p"
                            ),
                        "payment_breakdown": all_payments,
                        "total_amount_assigned": amount_assigned,
                        "total_amount_paid": amount_paid,
                        "total_amount_owing": amount_owing,
                        "fee_arrears_payment": arrear_payment_map
                    })
                    arrear_paid_obj = None
                    arrears_owing, total_paid, arrear_balance = arrears_payment_aggregate(payment_data.student.id)
                    data_dict["total_amount_assigned"] += arrears_owing
                    data_dict["total_amount_paid"] += total_paid
                    data_dict["total_amount_owing"] += arrear_balance
                except Exception as rec_except:
                    return Response(
                        {"message": rec_except.__str()},
                        status=status.HTTP_400_BAD_REQUEST)
            except Exception as rec_except1:
                return Response(
                    {"message": rec_except1.__str()},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            if arrear_paid_obj:
                payment_data = None
                arrears_owing, total_paid, arrear_balance = arrears_payment_aggregate(arrear_paid_obj.fee_arrear.student.id)
                data_dict["total_amount_assigned"] += arrears_owing
                data_dict["total_amount_paid"] += total_paid
                data_dict["total_amount_owing"] += arrear_balance
                try:
                    receipt = PaymentReceipt.objects.get(
                        arrear_payment__id=arrear_paid_obj.id
                        )
                    result = PaymentReceiptSerializer(
                            instance=receipt, context={"request": request}
                            )
                    return Response(
                        result.data,
                        status=status.HTTP_200_OK
                    )
                except PaymentReceipt.DoesNotExist:
                    purpose = f"Arrears Payment for {arrear_paid_obj.fee_arrear.student.__str__()}"
                    data_dict.update({
                            "cashier_name": arrear_paid_obj.user.__str__(),
                            "payment_mode": "" if arrear_paid_obj.payment_method is None else arrear_paid_obj.payment_method,
                            "cheque_number": "" if arrear_paid_obj.cheque_number is None else arrear_paid_obj.cheque_number,
                            "payer": arrear_paid_obj.fee_arrear.student.__str__(),
                            "date": arrear_paid_obj.date_created.strftime("%d-%m-%Y"),
                            "receipt_number": receipt_number,
                            "client_reference": arrear_paid_obj.fee_arrear.student.__str__(),
                            "description": f"Arrear Payment for {arrear_paid_obj.fee_arrear.student.__str__()}",
                            "income_amount": arrear_paid_obj.amount,
                            "payment_time": arrear_paid_obj.date_created.strftime(
                                "%I:%M %p"
                                ),
                            "payment_breakdown": None,
                            "total_amount_assigned": fee_arrears.aggregate(Sum("amount"))["amount__sum"],
                            "total_amount_paid": total_paid,
                            "total_amount_owing": arrears_owing,
                            "fee_arrears_payment": arrear_payment_map
                        })
                except Exception as rec_except2:
                    return Response(
                        {"message": rec_except2.__str()},
                        status=status.HTTP_400_BAD_REQUEST)
        pdf = convert_html_to_pdf(
            data_dict, "fee_receipt.html", f'{receipt_number}.pdf'
            )
        if pdf:
            receipt = PaymentReceipt.objects.create(
                payment=payment_data,
                arrear_payment=arrear_paid_obj,
                receipt_number=receipt_number,
                purpose=purpose,
                # details=data_dict
            )
            # receipt_file = ""
            f = open(f'{receipt_number}.pdf', 'rb')
            receipt.file.save(
                name=f'{receipt_number}.pdf',
                content=File(f), save=True
                )
            receipt.save()
            result = PaymentReceiptSerializer(
                instance=receipt, context={"request": request}
                )
            os.remove(f'{receipt_number}.pdf')
            return Response(
                result.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Receipt generation failed"},
                status=status.HTTP_400_BAD_REQUEST
            )


class FeeArrearView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FeeArrearSerializer
    queryset = FeeArrear.objects.all()
    http_method_names = ["get", "post", "patch", "delete"]


class ArrearPaymentView(viewsets.ModelViewSet):
    """API Views for the arears payment"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArrearPaymentSerializer
    queryset = ArrearPayment.objects.filter(
        fee_arrear__arrear_balance__gt=0
    )
    http_method_names = ["get", "post"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'payment_method'
        ]
    search_fields = [
        'fee_arrear__student__first_name', 'fee_arrear__student__last_name',
        'fee_arrear__student__id',
        'fee_arrear__academic_year__year', 'fee_arrear__academic_term__term'
        ]

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            return Response(
                {"message": exc.message, "error_message": "Validation Error"},
                status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)
