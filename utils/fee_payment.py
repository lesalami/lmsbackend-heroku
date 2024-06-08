"""
Helper functions for fee payment
"""
from uuid import uuid4
from decimal import Decimal
from django.db.models import Sum
from core.models import (
    # Student,
    StudentClass,
    Payment,
    FeeArrear,
    ArrearPayment
)


def fee_payment_breakdown(student_id: uuid4) -> list:
    """Find payment and owing per fee in fee group for student"""
    student_class = StudentClass.objects.get(
        student__id=student_id,
        academic_year__is_active=True
    )
    all_fees = student_class.fee_assigned.fees.all().order_by("date_created")
    fee_breakdown_list = []
    for fee in all_fees:
        paid_amount = 0
        fee_payment = Payment.objects.filter(
            academic_year__is_active=True,
            student__id=student_id,
            fee=fee
        )
        if fee_payment:
            paid_amount = fee_payment.aggregate(Sum("amount"))["amount__sum"]
        fee_breakdown_list.append(
            {
                "fee_name": fee.name,
                "fee_amount": fee.amount,
                "amount_paid": paid_amount,
                "amount_owing": fee.amount - paid_amount
            }
        )
    print(fee_breakdown_list)
    return fee_breakdown_list


def payment_aggregate(student_id: uuid4) -> tuple[Decimal, Decimal, Decimal]:
    """Get total amount paid and owing"""
    total_fees_assigned = StudentClass.objects.get(
        student__id=student_id, academic_year__is_active=True
    ).fee_assigned.fees.all().aggregate(
        Sum("amount")
    )["amount__sum"]
    total_paid = Payment.objects.filter(
        student__id=student_id, academic_year__is_active=True
    ).aggregate(
        Sum("amount")
    )["amount__sum"]
    total_owing = total_fees_assigned - total_paid
    return total_fees_assigned, total_paid, total_owing


def arrears_payment_aggregate(student_id: uuid4):
    """Get total amount paid and owing"""
    arrears_obj = FeeArrear.objects.filter(
        student__id=student_id,
        arrear_balance__gt=0
    )

    total_arrear_owing = arrears_obj.aggregate(Sum("amount"))["amount__sum"]

    arrears_balance = arrears_obj.aggregate(Sum("arrear_balance"))["arrear_balance__sum"]

    total_paid = ArrearPayment.objects.filter(
        fee_arrear__student__id=student_id
    ).aggregate(Sum("amount"))["amount__sum"]
    if not total_arrear_owing:
        total_arrear_owing = 0
    if not total_paid:
        total_paid = 0
    if not arrears_balance:
        arrears_balance = 0

    return total_arrear_owing, total_paid, arrears_balance
