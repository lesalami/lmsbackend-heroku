"""
Views for the Curriculum API.
"""
import os
import logging
# import random
from datetime import datetime, timedelta
from itertools import chain
from typing import Any
from django.core.files.base import File
from django.db.models import (
    Sum, Value, CharField, UUIDField,
    Q
    )
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from rest_framework.views import APIView
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
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema

from core.models import (
    AcademicTerm,
    AcademicYear,
    User
)

from user.serializers import UserSerializer

from finance.serializers import (
    IncomeTypeSerializer,
    IncomeSerializer, ExpenditureTypeSerializer,
    ExpenditureSerializer,
    SupplierSerializer,
    # TransactionSerializer,
    TaxConfigSerializer,
    TaxSerializer,
    SalaryBandSerializer,
    PaymentDetailSerializer,
    PayrollSerializer,
    ReceiptSerializer,
    PayrollRunSerializer
)
from finance.models import (
    IncomeType, Income,
    ExpenditureType, Expenditure,
    Supplier,
    TaxConfig, Tax,
    SalaryBand,
    PaymentDetail,
    Payroll,
    Receipt,
    PayrollRun
)
from finance.forms import UserLogin

from utils.pagination import StandardResultsSetPagination
from utils.pdf_generate import convert_html_to_pdf


logger = logging.getLogger(__name__)


class TaxConfigView(viewsets.ModelViewSet):
    """Tax Config API View"""
    queryset = TaxConfig.objects.all()
    serializer_class = TaxConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        return self.queryset.filter(
            organization=self.request.user.organization
        )


class TaxView(viewsets.ModelViewSet):
    """Tax API View"""
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        return self.queryset.filter(
            tax_config__organization=self.request.user.organization
        )


class SupplierView(viewsets.ModelViewSet):
    """Supplier API view"""
    queryset = Supplier.objects.all().order_by("-date_created")
    serializer_class = SupplierSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'date_created'
        ]
    search_fields = [
        'full_name', 'company_name'
        ]

    def get_queryset(self):
        return self.queryset.filter(
            user__organization=self.request.user.organization
        )


class IncomeTypeView(viewsets.ModelViewSet):
    """API View for Income Type"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IncomeTypeSerializer
    queryset = IncomeType.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    # pagination_class = StandardResultsSetPagination


class IncomeView(viewsets.ModelViewSet):
    """API View for Income"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IncomeSerializer
    queryset = Income.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'income_type__name': ['exact'],
        'payment_method': ['exact'],
        'date_created': ['gt', 'lt', 'exact'],
        }
    search_fields = [
        'student__first_name', 'student__last_name', 'tax__tax_config__name',
        'income_type__name', 'payer'
        ]

    @action(
            detail=False, methods=["get"],
            url_path="metrics", url_name="metrics")
    def metrics(self, request, *args, **kwargs):
        """Return some metrics on Income"""
        current_year = AcademicYear.objects.get(is_active=True)
        current_income = self.queryset.filter(
            academic_year=current_year
        ).aggregate(Sum("amount")).get("amount__sum")
        previous_income = 0
        if current_year.previous:
            previous_income = self.queryset.filter(
                academic_term=current_year.previous
            ).aggregate(Sum("amount")).get("amount__sum")
        percent_change = 100
        if previous_income != 0:
            percent_change = (
                current_income-previous_income)/previous_income
        change_type = "increase"
        if percent_change < 0:
            change_type = "decrease"
        monthly_income = self.queryset.filter(
            date_created__year=datetime.now().year,
            date_created__month=datetime.now().month
            ).aggregate(Sum("amount"))
        start_week = datetime.today() - timedelta(datetime.today().weekday())
        end_week = start_week + timedelta(7)
        print(start_week, end_week)
        weekly_income = self.queryset.filter(
            date_created__range=[start_week, end_week]
        ).aggregate(Sum("amount"))
        return Response(
            {
                "total_income": current_income,
                "change": str(abs(percent_change)) + "%",
                "change_type": change_type,
                "monthly_income": monthly_income["amount__sum"],
                "weekly_income": weekly_income["amount__sum"]
            },
            status=status.HTTP_200_OK
        )

    @action(
            detail=True, methods=["get"],
            url_path="receipt", url_name="receipt")
    def get_receipt(self, request, pk=None):
        """Generate and retun a PDF receipt given income ID"""
        income_data = self.get_object()
        org = request.user.organization
        print(income_data)
        if income_data:
            try:
                receipt = Receipt.objects.get(income__id=income_data.id)
                result = ReceiptSerializer(
                        instance=receipt, context={"request": request}
                        )
                return Response(
                    result.data,
                    status=status.HTTP_200_OK
                )
            except Receipt.DoesNotExist:
                # income_data = Income.objects.get(id=income.id)
                receipt_number = str(income_data.id).replace("-", "")
                data_dict = {
                    "organization_name": org.name,
                    "organization_address": org.address,
                    "payer": income_data.payer,
                    "date": income_data.income_date,
                    "receipt_number": receipt_number[:8],
                    "client_reference": income_data.payer,
                    "description": income_data.purpose,
                    "income_amount": income_data.amount,
                    "payment_time": income_data.date_created.strftime(
                        "%I:%M %p"
                        )
                }
                pdf = convert_html_to_pdf(
                    data_dict, "receipt.html", f'{receipt_number}.pdf'
                    )
                if pdf:
                    receipt = Receipt.objects.create(
                        income=income_data,
                        receipt_number=receipt_number[:8],
                        purpose=income_data.purpose
                    )
                    # receipt_file = ""
                    f = open(f'{receipt_number}.pdf', 'rb')
                    receipt.file.save(
                        name=f'{receipt_number}.pdf',
                        content=File(f), save=True
                        )
                    receipt.save()
                    result = ReceiptSerializer(
                        instance=receipt, context={"request": request}
                        )
                    os.remove(f'{receipt_number}.pdf')
                    return Response(
                        result.data,
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"message": "Receipt generation faile"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            return Response(
                {"message": "Income not found"},
                status=status.HTTP_400_BAD_REQUEST
                )

    # @action(
    #         detail=False, methods=["get"],
    #         url_path="files", url_name="files")
    # def files(self, request, *args, **kwargs):
    #     """Return all invoices with files"""
    #     return ""


class ExpenditureTypeView(viewsets.ModelViewSet):
    """API View for Expenditure Type"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExpenditureTypeSerializer
    queryset = ExpenditureType.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    # pagination_class = StandardResultsSetPagination


class ExpenditureView(viewsets.ModelViewSet):
    """API View for Expenditure"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExpenditureSerializer
    queryset = Expenditure.objects.all().order_by("-date_created")
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'expenditure_type__name': ['exact'],
        'payment_type': ['exact'],
        'payment_method': ['exact'],
        'date_created': ['gt', 'lt', 'exact'],
        }
    search_fields = [
        'payment_method',
        'supplier__full_name',
        'supplier__company_name'
        ]

    @action(
            detail=False, methods=["get"],
            url_path="metrics", url_name="metrics")
    def metrics(self, request, *args, **kwargs):
        """Return some metrics on Expenditure"""
        current_year = AcademicYear.objects.get(is_active=True)
        current_expenditure = self.queryset.filter(
            academic_year=current_year
        ).aggregate(Sum("amount")).get("amount__sum")
        previous_expenditure = 0
        if current_year.previous:
            previous_expenditure = self.queryset.filter(
                academic_year=current_year.previous
            ).aggregate(Sum("amount")).get("amount__sum")
        percent_change = 100
        if previous_expenditure != 0:
            percent_change = (
                current_expenditure-previous_expenditure)/previous_expenditure
        change_type = "increase"
        if percent_change < 0:
            change_type = "decrease"
        monthly_expenditure = self.queryset.filter(
            date_created__year=datetime.now().year,
            date_created__month=datetime.now().month
            ).aggregate(Sum("amount"))
        start_week = datetime.today() - timedelta(datetime.today().weekday())
        end_week = start_week + timedelta(7)
        # print(start_week, end_week)
        weekly_expenditure = self.queryset.filter(
            date_created__range=[start_week, end_week]
        ).aggregate(Sum("amount"))
        return Response(
            {
                "total_expenditure": current_expenditure,
                "change": str(abs(percent_change)) + "%",
                "change_type": change_type,
                "monthly_expenditure": monthly_expenditure["amount__sum"],
                "weekly_expenditure": weekly_expenditure["amount__sum"]
            },
            status=status.HTTP_200_OK
        )

    @action(
            detail=False, methods=["get"],
            url_path="files", url_name="files")
    def files(self, request, *args, **kwargs):
        """Return all expenses with files"""
        file_data = self.queryset.filter(
            Q(invoice__isnull=False)
            )
        allowed_ids = []
        for res in file_data:
            if res.invoice:
                allowed_ids.append(res.id)
        n_file_data = self.queryset.filter(id__in=allowed_ids)
        results = self.paginate_queryset(n_file_data)
        serialized = self.serializer_class(
            results, many=True, context={"request": request}
            )
        return self.get_paginated_response(
                serialized.data
                )


class SalaryBandView(viewsets.ModelViewSet):
    """API View for Salary Band"""
    queryset = SalaryBand.objects.all()
    serializer_class = SalaryBandSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        return self.queryset.filter(
            user__organization=self.request.user.organization
        )


class PaymentDetailView(viewsets.ModelViewSet):
    """API View for Payment Details for staff"""
    queryset = PaymentDetail.objects.all()
    serializer_class = PaymentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        return self.queryset.filter(
            user__organization=self.request.user.organization
        )


class PayrunView(viewsets.ModelViewSet):
    """API views for Payrun Details"""
    queryset = PayrollRun.objects.all().order_by("-date_created")
    serializer_class = PayrollRunSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'status',
        ]

    @action(
            detail=True, methods=["post"],
            url_path="process", url_name="process")
    def process_payrun(self, request, pk=None):
        """Process the payrun"""
        obj = self.queryset.get(id=pk)
        if obj.status == "Draft":
            obj.status = "Processed"
            obj.save()
            return Response(
                self.serializer_class(instance=obj).data,
                status=status.HTTP_200_OK
                )
        else:
            return Response(
                {"message": f"""
                 Payrun is in {obj.status} state. Cannot process"""
                 },
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
            detail=True, methods=["post"],
            url_path="approve", url_name="approve")
    def approve_payrun(self, request, pk=None):
        """Approve the pay run"""
        obj = self.queryset.get(id=pk)
        approver = request.user
        if obj.status == "Processed":
            obj.status = "Approved"
            obj.approved_by = approver
            obj.save()
            return Response(
                self.serializer_class(instance=obj).data,
                status=status.HTTP_200_OK
                )
        else:
            return Response(
                {"message": f"""
                 Payrun is in {obj.status} state. Cannot approve"""
                 },
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
            detail=False, methods=["get"],
            url_path="approve-by-list", url_name="approve-by-list")
    def approval_list(self, request, *args, **kwargs):
        """Return with admin and accountant roles """
        user_org = request.user.organization
        valid_users = User.objects.filter(
            organization=user_org, user_type__in=["Admin", "Accountant"]
        )
        return Response(
            UserSerializer(
                instance=valid_users, many=True,
                context={'request': self.request}
                ).data,
            status=status.HTTP_200_OK
        )


class PayrollView(viewsets.ModelViewSet):
    """API View for payroll"""
    queryset = Payroll.objects.filter(
    ).order_by("-date_created")
    serializer_class = PayrollSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'date_created',
        ]
    search_fields = [
        'staff__user__first_name', 'staff__user__last_name',
        'staff__user__organization__name'
        ]

    def get_queryset(self):
        return self.queryset.filter(
            staff__user__organization=self.request.user.organization,
            staff__is_active=True
            )

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class RecentTransactions(APIView):
    """Recent transactions: combine income/expenditure"""
    @extend_schema(responses={
        (200, 'application/json'): {
                'description': 'Recent Transactions',
                'type': 'json',
                'example': {
                    "date_created": "2023-08-28T15:03:09.095765Z",
                    "id": "76c722b6-d844-442f-a4a6-16711713faa5",
                    "amount": "75859",
                    "user": "442f-a4a6-16711713faa5-76c722b6-d844"
                }
            },
        })
    def get(self, request):
        recent_income = Income.objects.filter(
            academic_term__is_active=True
        ).order_by("-date_created")[:10].values(
            "id", "date_created", "user", "amount", "purpose",
            "student", "student__first_name", "student__last_name"
            )
        recent_expense = Expenditure.objects.filter(
            academic_term__is_active=True
        ).order_by("-date_created")[:10].values(
            "id", "date_created", 'user', "amount", "purpose"
            )
        recent_income = recent_income.annotate(
            model_type=Value("Income", output_field=CharField())
            )
        recent_expense = recent_expense.annotate(
            model_type=Value("Expenditure", output_field=CharField())
            )
        recent_expense = recent_expense.annotate(
                student=Value(
                    None, output_field=UUIDField(null=True, blank=True)
                    )
            )
        # print(recent_expense)
        recent_ten = list(chain(recent_income, recent_expense))
        return Response(
            {
                "recent_transactions": recent_ten
            },
            status=status.HTTP_200_OK
        )


class HomePage(generic.ListView):
    """Home page for the finance admin"""
    model = Income
    paginate_by = 10
    template_name = "finance/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


def dashboardview(request):
    """Dashboard view"""
    if request.user.is_authenticated:
        income = Income.objects.all()
        expenses = Expenditure.objects.all()
        ctxt = {
            "income": income,
            "expenses": expenses
        }
        return render(request, "finance/dashboard.html", ctxt)
    return redirect("/login?next=%s" % request.path)


def LoginView(request):
    """Login View for django template"""
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(request.GET.get("next", "/"))
            else:
                return redirect("/login?next=%s" % request.path)
        else:
            return redirect("/login?next=%s" % request.path)
    user_login_form = UserLogin
    return render(
        request, "auth/login.html", {"user_login_form": user_login_form}
        )
