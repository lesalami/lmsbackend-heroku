"""
Helper functions for fee payment
"""
from uuid import uuid4
from django.db.models import Sum
from core.models import (
    # Student,
    StudentClass,
    Payment,
    # Fee
)


def fee_payment_breakdown(student_id: uuid4) -> list:
    """Find payment and owing per fee in fee group for student"""
    student_class = StudentClass.objects.get(
        student__id=student_id,
        academic_year__is_active=True
    )
    all_fees = student_class.fee_assigned.fees.all()
    # all_payments = Payment.objects.filter(
    #     academic_year__is_active=True,
    #     student__id=student_id
    # ).values("fee").annotate(Sum("amount"))
    # payment_breakdown_list = []
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


def payment_aggregate(student_id: uuid4):
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
