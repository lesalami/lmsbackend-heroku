""""
API endpoints to handle the Finance Requests
"""
from django.urls import path

# from rest_framework.routers import DefaultRouter

from finance import views

app_name = "finance-admin"


urlpatterns = [
    path(
        "",
        views.dashboardview,
        name="index"
        ),
    path(
        "login", views.LoginView, name="login"
    ),
    path(
        "dashboard", views.dashboardview,
        name="dashboard"
    ),
]
