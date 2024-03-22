""""
API endpoints to handle the Curriculum requests
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from curriculum import views

app_name = "curriculum"

router = DefaultRouter()

router.register(
    "academic-year", views.AcademicYearView, basename="academic-year"
    )
router.register(
    "academic-term", views.AcademicTermView, basename="academic-term"
)
router.register(
    "student", views.StudentView, basename="student"
)
router.register(
    "parent-or-guardian", views.ParentOrGuardianView,
    basename="parent-or-guardian"
)
router.register(
    "staff", views.StaffView, basename="staff"
)
router.register(
    "subject", views.SubjectView, basename="subject"
)
router.register(
    "class", views.ClassView, basename="class"
)
router.register(
    "student-fee-group", views.StudentFeeGroupView,
    basename="student-fee-group"
)
router.register(
    "subject-teacher", views.TeacherAssignmentView,
    basename="subject-teacher"
)
router.register(
    "student-class", views.StudentClassView, basename="student-class"
)
router.register(
    "teacher-class", views.TeacherClassView, basename="teacher-class"
)
router.register(
    "school-fees",
    views.FeeView,
    basename="school-fees"
)
router.register(
    "payment", views.PaymentView, basename="payment"
)
router.register(
    "fee-arrears", views.FeeArrearView, basename="fee-arrears"
)
router.register(
    "fee-arrears-payment", views.ArrearPaymentView, basename="fee-arrears-payment"
)


urlpatterns = [
    path("", include(router.urls)),
]
