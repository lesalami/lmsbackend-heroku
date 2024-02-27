"""
All helper functions relating the finance model
including tax calculation, payroll, etc
"""
from typing import Union
from uuid import uuid4

from django.db.models import Sum
from core.models import Staff

from finance.models import (
    SalaryBand,
    PaymentDetail,
    # PayrollRun,
    Payroll
    )


residency_rate = {
    "Non-Resident": 25,
    "Resident-Part-Time": 10,
    "Resident-Casual": 5,
    "Resident-Full-Time": "Resident-Full-Time"
}


def summary_tax(staff_id, ssnit_rate, tier_three) -> dict:
    """
    Parent function to return the dict

    Args:
        staff_id: Primary key (UUID) for staff model
        ssnit_rate: Rate of SSNIT without tier_three on the org
        tier_three: SSNIT Tier three if it exists
    """
    try:
        pay_details = PaymentDetail.objects.get(staff__id=staff_id).salary_band
        salary_band = SalaryBand.objects.get(id=pay_details.id)
        benefits = salary_band.benefit_package
        employeessnit = employee_ssnit(salary_band.amount, ssnit_rate)
        cash_allowance = 0
        excess_bonus = 0
        bonus_income = 0
        vehicle_elements = 0
        non_cash_benefits = 0
        deductible_relief = 0
        if benefits is not None:
            cash_allowance = float(benefits.get("cash_allowance", 0))
            excess_bonus = float(benefits.get("excess_bonus", 0))
            bonus_income = float(benefits.get("bonus_income", 0))
            vehicle_elements = float(benefits.get("vehicle_elements", 0))
            non_cash_benefits = float(benefits.get("non_cash_benefits", 0))
            deductible_relief = float(benefits.get("deductible_relief", 0))
        totalcashamolument = total_cash_amolument(
            salary_band.amount, cash_allowance, excess_bonus
            )
        tier_threecontribute = tier_three_contribution(
            salary_band.amount, tier_three
        )
        accessible_income = totalcashamolument+vehicle_elements+non_cash_benefits
        total_relief = employeessnit + tier_threecontribute + deductible_relief
        chargeable_income = accessible_income - total_relief - cash_allowance

        tax_deductible = calculate_tax_deductible(
            staff_id, chargeable_income
        )
        overtime_tax = 0
        tax_payable_to_gra = bonus_income + tax_deductible + overtime_tax

        result = {
            "basic_salary": salary_band.amount,
            "total_cash_amolument": totalcashamolument,
            "ssnit_amount": employeessnit,
            "tier_three": tier_threecontribute,
            "cash_allowance": cash_allowance,
            "bonus_income": bonus_income,
            "excess_bonus": excess_bonus,
            "vehicle_elements": vehicle_elements,
            "non_cash_benefits": non_cash_benefits,
            "accessible_income": accessible_income,
            "deductible_relief": deductible_relief,
            "total_relief": total_relief,
            "chargeable_income": chargeable_income,
            "tax_deductible": tax_deductible,
            "tax_payable": tax_payable_to_gra,
        }
        return result
    except PaymentDetail.DoesNotExist:
        return None
    except SalaryBand.DoesNotExist:
        return None


def total_cash_amolument(basic, cash_allowance, excess_bonus):
    """Sum of basic, cash allowances and excess bonus"""
    if basic:
        if cash_allowance:
            if excess_bonus:
                return basic + cash_allowance + excess_bonus
            else:
                return basic + cash_allowance
        else:
            return basic
    else:
        return 0


def employee_ssnit(basic: float, ssnit: float):
    """Get the rate from org config to calculate on basic"""
    if basic:
        if ssnit:
            return (ssnit/100) * basic
        else:
            return basic
    else:
        return 0


def tier_three_contribution(basic, tier_three_rate):
    """Get the rate from org config to calculate on basic"""
    return (tier_three_rate/100) * basic


def calculate_tax_deductible(staff_id, chargeable):
    """Calculation for the tax deductible"""
    staff_residency = Staff.objects.get(id=staff_id).residency_status

    res_rate = residency_rate.get(staff_residency)
    if res_rate:
        if res_rate == "Resident-Full-Time":
            level_1, level_2, level_3, level_4, level_5 = 0, 0, 0, 0, 0
            level_6 = 0
            if chargeable - 402 > 0:
                level_1 = min(chargeable-402, 110) * 0.05
            if chargeable - 512 > 0:
                level_2 = min(chargeable - 512, 130) * 0.1
            if chargeable - 642 > 0:
                level_3 = min(chargeable - 642, 3000) * 0.175
            if chargeable - 3642 > 0:
                level_4 = min(chargeable - 3642, 16395) * 0.25
            if chargeable - 20037 > 0:
                level_5 = min(chargeable - 20037, 29963) * 0.3
            if chargeable - 50000 > 0:
                level_6 = chargeable - 50000
            tax_deduc = level_1 + level_2 + level_3 + level_4 + level_5+level_6
        else:
            tax_deduc = res_rate * chargeable
    else:
        tax_deduc = 0
    return tax_deduc


def update_payrun_basic(payrun_id: Union[str, uuid4]) -> Union[float, int]:
    """
    A function that updates total basic salary on payrun
    """
    result = Payroll.objects.filter(
        payrun__id=payrun_id
        ).aaggregate(total_sum=Sum("basic_salary"))

    return result.get("total_sum", 0)


def update_chargeable(payrun_id: Union[str, uuid4]) -> Union[float, int]:
    """
    Update the total chargeable income for the payrun
    """
    result = Payroll.objects.filter(
        payrun__id=payrun_id
        ).aaggregate(total_sum=Sum("chargeable_income"))

    return result.get("total_sum", 0)
