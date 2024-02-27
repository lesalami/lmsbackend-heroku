"""
Create a test data for the financial transactions
Invoice, Income and Expenditure
"""
from typing import Optional, Any
from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model

from core.models import (
    Staff,
)
from finance.models import (
    SalaryBand,
    PaymentDetail
)


class Command(BaseCommand):
    help = "Create Students from initial data"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        """Create Salary band and Payment details for staff"""
        # A test user to own the creation of sample data
        test_user, user_created = get_user_model().objects.get_or_create(
            email="finance@email.com",
            password="Passwd12**",
        )
        if user_created:
            test_user.is_active = True
            test_user.save()
        try:
            salary_band = SalaryBand.objects.get(
                name="Basic"
            )
        except SalaryBand.DoesNotExist:
            salary_band = SalaryBand.objects.create(
                name="Basic", amount=1000, user=test_user,
                benefit_package={
                    "cash_allowance": 433
                }
            )
        # Create Payment Detail objects if there is none - 20
        for staff in Staff.objects.all():
            try:
                PaymentDetail.objects.get(
                    staff=staff,
                )
            except PaymentDetail.DoesNotExist:
                PaymentDetail.objects.create(
                    staff=staff,
                    salary_band=salary_band,
                    user=test_user
                )

        self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created some Payment detail data'
                    )
                )
