"""
Implementing custom permissions on users
"""
from rest_framework.permissions import BasePermission


class SchoolAdmin(BasePermission):
    """Custom permission for School Admin"""

    def has_permission(self, request, view):
        if request.user and request.user.user_type == "Admin":
            return True

        return False


class SchoolAccountant(BasePermission):
    """Custom permission for Company Researcher"""

    def has_permission(self, request, view):
        if request.user and request.user.user_type == "Accountant":
            return True

        return False


class Staff(BasePermission):
    """Custom permission for Company Researcher"""

    def has_permission(self, request, view):
        if request.user and request.user.user_type == "Staff":
            return True

        return False


class Proprietor(BasePermission):
    """Custom permission for Company Researcher"""

    def has_permission(self, request, view):
        if request.user and request.user.user_type == "Proprietor":
            return True

        return False
