"""
Create a test data for the financial transactions
Invoice, Income and Expenditure
"""
import random
# import string
from faker import Faker
from datetime import datetime
from typing import Optional, Any
from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model

from core.models import (
    Student,
    # Class,
    AcademicYear, AcademicTerm,
    # StudentClass,
    # User
)
from finance.models import (
    IncomeType, Income,
    ExpenditureType, Expenditure
)


class Command(BaseCommand):
    help = "Create Students from initial data"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        """Create invoice, income and Expenses data"""
        # Academic year since a term is tied to academic year
        acad_year, year_created = AcademicYear.objects.get_or_create(
            year=f"{datetime.now().year} - {datetime.now().year+1}"
        )
        # Academic term since all expenses and income must be tied to term
        acad_term, term_created = AcademicTerm.objects.get_or_create(
            academic_year=acad_year,
            term="First Term"
        )

        # A test user to own the creation of sample data
        test_user, user_created = get_user_model().objects.get_or_create(
            email="finance@email.com",
            password="Passwd12**",
        )
        if user_created:
            test_user.is_active = True
            test_user.save()
        # Types of income names
        income_types = [
            "Tuition Fees"
            ]
        created_types = []
        # Types of expenses
        expend_types = [
            "Personnel", "Facility", "Educational",
            "Techonology", 'Administrative'
            ]
        created_expends = []
        # Create income types
        for item in income_types:
            type_income, it_created = IncomeType.objects.get_or_create(
                name=item
            )
            created_types.append(type_income)
        # Create expense types
        for item in expend_types:
            type_expend, et_created = ExpenditureType.objects.get_or_create(
                name=item
            )
            created_expends.append(type_expend)
        # initialize the faker
        fake = Faker()
        # Create Income objects if there is none - 20
        if not Income.objects.all():
            for r in range(20):
                Income.objects.create(
                    income_type=random.choice(created_types),
                    academic_year=acad_year,
                    academic_term=acad_term,
                    user=test_user,
                    amount=random.randrange(10000, 99999),
                    purpose="Tuition Fees",
                    payer=fake.name(),
                    student=random.choice(list(Student.objects.all()))
                )
        # Create expense objects if there is none - 20
        if not Expenditure.objects.all():
            for r in range(20):
                _created = Expenditure.objects.create(
                    expenditure_type=random.choice(created_expends),
                    user=test_user,
                    academic_year=acad_year,
                    academic_term=acad_term,
                    amount=random.randrange(100, 99999),
                    purpose=fake.sentence()
                )
                # _created.invoice.add(random.choice(created_invoices))

        self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created some financial data'
                    )
                )
