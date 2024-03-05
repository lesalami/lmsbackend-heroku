"""
Generic views for dasboard API
"""
import logging
from datetime import datetime, timedelta
# from itertools import chain
from django.db.models import (
    # Value, CharField,
    Sum
)
# from django.forms.models import model_to_dict
from rest_framework import (
    permissions, status, viewsets,
    filters
    )
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend

from core.models import (
    DatabaseActionLog,
    StudentClass,
    Staff,
    Class, AcademicYear,
    OrganizationDocument,
    OrganizationConfig,
    Payment
)
from curriculum.serializers import ClassSerializer, PaymentSerializer
from user.serializers import UserSerializer
from core.serializers import (
    DatabaseActionSerializer,
    # DashboardSerialaizer
    OrganizationDocumentSerializer,
    OrganizationConfigSerializer
    )
from finance.models import (
    Income, Expenditure
)
from finance.serializers import IncomeSerializer, ExpenditureSerializer
from utils.pagination import StandardResultsSetPagination
from core.utils import StaffType

logger = logging.getLogger(__name__)


class DashboardView(APIView):
    """Dashboard metrics view"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={
       (200, 'application/json'): {
            'description': 'Dashboard',
            'type': 'json',
            'example': {
                "user": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "email": "user@example.com",
                    "first_name": "string",
                    "last_name": "string",
                    "user_type": "Parent"
                    },
                "students": {
                    "total": 0,
                    "male": 0,
                    "female": 0,
                    "change": "100%",
                    "change_type": "increase"
                },
                "teachers": {
                    "total": 0,
                    "change": "100%",
                    "change_type": "increase"
                },
                "transactions": {
                    "total_expenditure": 0,
                    "total_income": 0,
                },
                "recent_activity": [
                        {
                            "model_name": "Student",
                            "message": "A Student was updated.",
                            "timestamp": "2023-08-11T10:23:07.158172Z",
                            "user": "13513368-e874-4188-8b51-219b51d54945"
                        }
                    ],
                "class": []
            }
        },
    })
    def get(self, request):
        """Data for initial dashboard"""
        # Miscellaneous
        user = UserSerializer(instance=request.user).data
        current_year = AcademicYear.objects.get(is_active=True)
        # current_classes = Class.objects.filter(
        #     academic_year=current_year
        # )
        current_payment = Payment.objects.filter(
            academic_year=current_year
        ).aggregate(Sum("amount")).get("amount__sum")
        previous_income = 0
        previous_expenditure = 0
        previous_payment = 0
        if current_year.previous:
            previous_students = StudentClass.objects.filter(
                academic_year=current_year.previous
            ).values_list("student").count()
            previous_income = Income.objects.filter(
                academic_year=current_year.previous
            ).aggregate(Sum("amount")).get("amount__sum")
            previous_expenditure = Expenditure.objects.filter(
                academic_year=current_year.previous
            ).aggregate(Sum("amount")).get("amount__sum")
            previous_payment = Payment.objects.filter(
                academic_year=current_year.previous
            ).aggregate(Sum("amount")).get("amount__sum")
        # Students data
        total_students = StudentClass.objects.filter(
            academic_year=current_year,
            student__is_active=True,
        ).values_list("student").count()
        student_percent_change = 100
        if previous_students > 0 and previous_students is not None:
            student_percent_change = (
                total_students-previous_students)/previous_students
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
        student_change_type = "increase"
        if student_percent_change < 0:
            student_change_type = "decrease"
        # Teacher data
        total_teachers = Staff.objects.filter(
            is_active=True, staff_type=StaffType.Teaching
            ).count()
        total_teachers_non = Staff.objects.filter(
            is_active=True, staff_type=StaffType.Non_Teaching
            ).count()
        payment_percent_change = 100
        if previous_payment is not None and previous_payment > 0:
            payment_percent_change = (
                current_payment-previous_payment)/previous_payment
        payment_change_type = "increase"
        if payment_percent_change < 0:
            payment_change_type = "decrease"
        # Recent activities
        recent_activity = DatabaseActionLog.objects.all().order_by(
            "-timestamp"
        )[:5]
        recent_serialzed = DatabaseActionSerializer(
            instance=recent_activity, many=True).data
        # Classes data
        class_obj = Class.objects.all()
        class_data = ClassSerializer(instance=class_obj, many=True).data
        # Transaction summary
        total_expenditure = Expenditure.objects.filter(
            academic_year__is_active=True,
        ).values_list("amount", flat=True)
        total_income = Income.objects.filter(
            academic_year__is_active=True,
        ).values_list("amount", flat=True)
        income_percent_change = 100
        expense_percent_change = 100
        if previous_income > 0 and previous_income is not None:
            income_percent_change = (
                total_income-previous_income)/previous_income
        if previous_expenditure > 0 and previous_expenditure is not None:
            expense_percent_change = (
                total_expenditure-previous_expenditure)/previous_expenditure
        income_change_type = "increase"
        expense_change_type = "increase"
        if income_percent_change < 0:
            income_change_type = "decrease"
        if expense_percent_change < 0:
            expense_change_type = "decrease"
        # Recent transactions
        recent_income = Income.objects.filter(
            academic_year__is_active=True
        ).order_by("-date_created")[:5]
        recent_expense = Expenditure.objects.filter(
            academic_year__is_active=True
        ).order_by("-date_created")[:5]
        monthly_payment = Payment.objects.filter(
            date_created__year=datetime.now().year,
            date_created__month=datetime.now().month
            ).aggregate(Sum("amount"))
        monthly_income = Income.objects.filter(
            date_created__year=datetime.now().year,
            date_created__month=datetime.now().month
            ).aggregate(Sum("amount"))
        start_week = datetime.today() - timedelta(datetime.today().weekday())
        end_week = start_week + timedelta(7)
        # print(start_week, end_week)
        weekly_income = Income.objects.filter(
            date_created__range=[start_week, end_week]
        ).aggregate(Sum("amount"))
        monthly_expenditure = Expenditure.objects.filter(
            date_created__year__gte=datetime.now().year,
            date_created__month=datetime.now().month
            ).aggregate(Sum("amount"))
        weekly_expenditure = Expenditure.objects.filter(
            date_created__range=[start_week, end_week]
        ).aggregate(Sum("amount"))
        weekly_payment = Payment.objects.filter(
            date_created__range=[start_week, end_week]
        ).aggregate(Sum("amount"))
        dashboard_data = {
                "user": user,
                "students": {
                     "total": total_students,
                     "male": male_students_count,
                     "female": female_students_count,
                     "change": str(abs(student_percent_change)) + "%",
                     "change_type": student_change_type
                },
                "teachers": {
                    "total_teachers": total_teachers,
                    "total_non_teaching_staff": total_teachers_non,
                },
                "transactions": {
                    "total_expenditure": sum(total_expenditure),
                    "expense_percent_change": str(
                        abs(expense_percent_change)) + "%",
                    "expense_change_type": expense_change_type,
                    "monthly_expenditure": monthly_expenditure["amount__sum"],
                    "weekly_expenditure": weekly_expenditure["amount__sum"],
                    "total_income": sum(total_income),
                    "income_percent_change": str(
                        abs(income_percent_change)) + "%",
                    "income_change_type": income_change_type,
                    "monthly_income": monthly_income["amount__sum"],
                    "weekly_income": weekly_income["amount__sum"],
                    "total_payment": current_payment,
                    "change": str(abs(payment_percent_change)) + "%",
                    "change_type": payment_change_type,
                    "monthly_payment": monthly_payment["amount__sum"],
                    "weekly_payment": weekly_payment["amount__sum"]
                },
                "classes": class_data,
                "recent_activity": recent_serialzed,
                "recent_transactions": {
                    "income": IncomeSerializer(
                        instance=recent_income, many=True
                        ).data,
                    "expenditure": ExpenditureSerializer(
                        recent_expense, many=True
                        ).data,
                    "payment": PaymentSerializer(
                        instance=Payment.objects.filter(
                            academic_year__is_active=True
                        ).order_by("-date_created")[:5],
                        many=True
                        ).data
                }
            }
        return Response(
            dashboard_data, status=status.HTTP_200_OK
        )


class OrganizationDocumentView(viewsets.ModelViewSet):
    """Document Upload endpoint"""
    queryset = OrganizationDocument.objects.filter(
    ).order_by("-date_created")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationDocumentSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'date_created', 'file_type',
        ]
    search_fields = [
        'organization__name', 'name', 'description',
        'file_type'
        ]


class OrganizationConfigView(viewsets.ModelViewSet):
    """School Config API views"""
    queryset = OrganizationConfig.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationConfigSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return self.queryset.filter(organizational_user=self.request.user)

    def list(self, request, *args, **kwargs):
        raw_data = self.queryset.get(
            organizational_user=self.request.user
        )
        return Response(
            self.serializer_class(instance=raw_data).data,
            status=status.HTTP_200_OK
            )
