"""
Backfill the Student Fee data from previous term before the deployment
"""
import csv
from pathlib import Path
from datetime import datetime
from typing import Optional, Any
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandParser
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
import openpyxl

from core.models import (
    Student, Class, AcademicYear,
    AcademicTerm, StudentClass,
    StudentFeeGroup,
    Fee,
    User,
    Payment,
    FeeArrear,
    ArrearPayment
)


class Command(BaseCommand):
    help = "Backfill with data from previous terms in the academic year"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "file_path",
            help="Path to the CSV File containing the fee data in the correct format e.g student.csv"
        )
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        """Handle student fee data population"""
        filename = options["file_path"]
        type_of_file = Path(filename).suffix
        academic_year = AcademicYear.objects.get(is_active=True)
        related_terms = AcademicTerm.objects.filter(academic_year=academic_year)
        cuurent_term = AcademicTerm.objects.get(is_active=True)
        second_term: AcademicTerm = cuurent_term.previous
        first_term = second_term.previous
        finance_user = User.objects.get(first_name="Florence", last_name="Ametepe")
        fee_map = {
            "Primary": ["BASIC 4", "BASIC 6", "BASIC 5", "BASIC 1", "BASIC 3", "BASIC 2", "	KINDERGARTEN 2", "KINDERGARTEN 1"],
            "Pre School": ["NURSERY 2", "NURSERY 1"],
            "JHS": ["JHS1", "JH3", "JHS 2"]
        }
        print(f"{academic_year}")
        if type_of_file == ".xlsx":
            self.stdout.write(
                self.style.ERROR(
                    "Wrong File Format, Excel. Expected a CSV"
                    )
                )
            dataframe = openpyxl.load_workbook(filename)
            name_list = dataframe.sheetnames
            print(name_list)
        elif type_of_file ==".csv":
            with open(filename, newline="") as csvfile:
                spamreader = csv.DictReader(csvfile, delimiter=",", quotechar="|")
                # headers = next(spamreader)
                for row in spamreader:
                    try:
                        std_obj = Student.objects.get(id=row["ID"])
                        print(f"Student with ID {std_obj.id} exists")
                        student_class = StudentClass.objects.get(student=std_obj)
                        fees_obj = student_class.fee_assigned.fees.all()
                        first_term_amount = row.get("term_1_fees")
                        second_term_amount = row.get("term_2_fees")
                        third_term_amount = row.get("term_3_fees")
                        std_arrears = row.get("arrears")
                        if first_term_amount.isnumeric() and not float(first_term_amount) <= 0.00:
                            first_term_payment = Payment.objects.create(
                                academic_year=academic_year,
                                academic_term=first_term,
                                user=finance_user,
                                student=std_obj,
                                fee=fees_obj.get(academic_term=first_term),
                                amount=Decimal(row.get("term_1_fees")),
                                payment_method=row.get("term_1_payment_type")
                            )
                        if second_term_amount.isnumeric() and not float(second_term_amount) <= 0.00:
                            second_term_payment = Payment.objects.create(
                                academic_year=academic_year,
                                academic_term=second_term,
                                user=finance_user,
                                student=std_obj,
                                fee=fees_obj.get(academic_term=second_term),
                                amount=Decimal(row.get("term_2_fees")),
                                payment_method=row.get("term_2_payment_type")
                            )
                        if third_term_amount.isnumeric() and not float(third_term_amount) <= 0.00:
                            third_term_payment = Payment.objects.create(
                                academic_year=academic_year,
                                academic_term=cuurent_term,
                                user=finance_user,
                                student=std_obj,
                                fee=fees_obj.get(academic_term=cuurent_term),
                                amount=Decimal(row.get("term_3_fees")),
                                payment_method=row.get("term_3_payment_type")
                            )
                        if std_arrears.isnumeric() and not float(std_arrears) <= 0.00:
                            arrear_obj = FeeArrear.objects.create(
                                academic_year=academic_year,
                                academic_term=cuurent_term,
                                student=std_obj,
                                amount=Decimal(std_arrears)
                            )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully created payment and arrears for {std_obj}"
                            )
                        )
                    except ValidationError as valid_error:
                        cleaned_str = valid_error.__str__().replace("['", "").replace("']", "").split(" ")
                        spx_term = " ".join(cleaned_str[-2:])
                        term_mapping = {
                            "First Term": first_term,
                            "Second Term": second_term,
                            "Third Term": cuurent_term
                        }
                        spx_amount = cleaned_str[-3]
                        print(spx_amount, spx_term)
                        assigned_fee_amount = fees_obj.get(academic_term=term_mapping.get(spx_term)).amount
                        print(assigned_fee_amount)
                        arrear_obj = FeeArrear.objects.create(
                                academic_year=academic_year,
                                academic_term=term_mapping.get(spx_term),
                                student=std_obj,
                                amount=Decimal(spx_amount) - assigned_fee_amount
                            )
                        spx_term_payment = Payment.objects.create(
                                academic_year=academic_year,
                                academic_term=term_mapping.get(spx_term),
                                user=finance_user,
                                student=std_obj,
                                fee=fees_obj.get(academic_term=term_mapping.get(spx_term)),
                                amount=assigned_fee_amount,
                                payment_method="Cash"
                            )
                        std_arrear_payment = ArrearPayment.objects.create(
                            user=finance_user,
                            fee_arrear=arrear_obj,
                            amount=Decimal(spx_amount) - assigned_fee_amount,
                            payment_method="Cash"
                        )

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully created payment and arrears for {std_obj}"
                            )
                        )
                    except Student.DoesNotExist:
                        print(f"Student: {row.get('first_name')} {row.get('last_name')} not Found")
                        continue
                    except StudentClass.DoesNotExist:
                        print(f"StudentClass for {row.get('first_name')} {row.get('last_name')} not Found")
                        continue

                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully loaded the backfill data"
                    )
                )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Wrong File Format: {type_of_file}. Expected CSV or Excel"
                    )
                )
