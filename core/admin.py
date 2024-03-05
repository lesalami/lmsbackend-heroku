"""
The administration of models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
# from django.urls import reverse

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""

    ordering = ["id"]
    list_display = ["email", "first_name", "last_name"]
    search_fields = ["email", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal Info"),
            {"fields": ("first_name", "last_name")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "email_confirmed",
                    "organization",
                    "groups"
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
        (_("Others"), {"fields": ("user_type",)})
    )
    readonly_fields = ["last_login"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_type",
                    "organization",
                    "groups"
                ),
            },
        ),
    )


class AcademicTermAdmin(admin.ModelAdmin):
    """Admin view for the academic term"""
    list_display = ["term", "academic_year"]
    list_per_page = 10


class StudentAdmin(admin.ModelAdmin):
    """Admin view for Student"""
    list_display = ["first_name", "last_name", "student_id"]
    search_fields = ["first_name", "last_name", "student_id"]
    list_per_page = 10


class StudentClassAdmin(admin.ModelAdmin):
    """Admin view for the student to class mapping"""
    list_display = ["student", "student_class"]
    search_fields = [
        "student__first_name", "student__last_name", "student_class__name"]
    list_per_page = 10
    readonly_fields = ("fee_paid", "fee_owing")


class SubjectAdmin(admin.ModelAdmin):
    """Admin view for the subject model"""
    list_display = ["name", "subject_id"]
    list_per_page = 10


class TeacherAssignmentAdmin(admin.ModelAdmin):
    """Admin view for the teacher assignment model"""
    list_display = [
        "teacher", "subject"
        ]
    list_per_page = 10


class StaffAdmin(admin.ModelAdmin):
    """Admin view for the teacher model"""
    list_display = ["staff_id", "gender", "staff_type"]
    list_per_page = 10
    search_fields = ["user__first_name", "user__last_name"]


class TeacherClassAdmin(admin.ModelAdmin):
    """Admin view for the teacher class"""
    list_display = ["teacher", "teacher_class"]
    search_fields = [
        "teacher__first_name", "teacher__last_name", "teacher_class__name"]
    list_per_page = 10


class PaymentAdmin(admin.ModelAdmin):
    """Admin view for the payment model"""
    search_fields = [
        "student__first_name", "student__last_name",
        "fee__name"
        ]


admin.site.register(models.OrganizationConfig)
admin.site.register(models.Fee)
admin.site.register(models.OrganizationDocument)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.AcademicYear)
admin.site.register(models.Student, StudentAdmin)
admin.site.register(models.ParentOrGuardian)
admin.site.register(models.Staff, StaffAdmin)
admin.site.register(models.Subject, SubjectAdmin)
# admin.site.register(models.NonTeachingStaff)
admin.site.register(models.Class)
admin.site.register(models.AcademicTerm, AcademicTermAdmin)
admin.site.register(models.TeacherAssignment, TeacherAssignmentAdmin)
admin.site.register(models.TeacherClass, TeacherClassAdmin)
admin.site.register(models.StudentClass, StudentClassAdmin)
admin.site.register(models.StudentFeeGroup)
admin.site.register(models.Payment, PaymentAdmin)
admin.site.register(models.PaymentReceipt)
