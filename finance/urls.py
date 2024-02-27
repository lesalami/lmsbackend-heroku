""""
API endpoints to handle the Finance Requests
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from finance import views

app_name = "finance"

router = DefaultRouter()

router.register(
    "tax-config", views.TaxConfigView, basename="tax-config"
)
router.register(
    "tax", views.TaxView, basename="tax"
)
router.register(
    "income-type", views.IncomeTypeView, basename="income-type"
)
router.register(
    "income", views.IncomeView, basename="income"
)
router.register(
    "expenditure-type", views.ExpenditureTypeView,
    basename="expenditure-type"
)
router.register(
    "expenditure", views.ExpenditureView, basename="expenditure"
)
router.register(
    "salary-band", views.SalaryBandView, basename="salary-band"
)
router.register(
    "payment-detail", views.PaymentDetailView, basename="payment-detail"
)
router.register(
    "supplier",
    views.SupplierView, basename="supplier"
)
router.register(
    "payroll", views.PayrollView, basename="payroll"
)
router.register(
    "payrun", views.PayrunView, basename="payrun"
)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "recent-transactions",
        views.RecentTransactions.as_view(),
        name="recent-transactions"
        ),
]
