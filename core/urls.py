""""
API endpoints to the dashboard requests solely
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from core import views

app_name = "dashboard"

router = DefaultRouter()

router.register(
    "file-upload",
    views.OrganizationDocumentView,
    basename="file-upload"
    )

router.register(
    "school-config",
    views.OrganizationConfigView,
    basename="school-config"
)


urlpatterns = [
    path("", include(router.urls)),
    path("metrics/", views.DashboardView.as_view(), name="metrics"),
]
