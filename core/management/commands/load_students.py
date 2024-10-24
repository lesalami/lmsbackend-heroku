"""
Load Student data for the 2024/2025 academic year
"""
import csv
from pathlib import Path
from decimal import Decimal
from typing import Optional, Any
from django.core.management.base import BaseCommand, CommandParser
from django.db.utils import IntegrityError

from core.models import (
    Student, Class, AcademicYear,
    AcademicTerm, StudentClass,
    StudentFeeGroup,
    Fee,
    User,
    Payment
)
from utils.utils import generate_studentid

_academic_year: str = "2024/2025"
class_names = {
    "NURSERY 1": 100, "NURSERY 2": 0, "KINDERGARTEN 1": 0, "KINDERGARTEN 2": 0,
    "BASIC 1": 0, "BASIC 2": 0, "BASIC 3": 0, "BASIC 4": 0, "BASIC 5": 0, "BASIC 6": 0,
    "JHS 1": 0, "JHS 2": 0, "JHS 3": 0, "CRECHE": 0
}

class_group_map: dict[str, list[str]] = {
    "Pre School": ["NURSERY 1", "NURSERY 2", "KINDERGARTEN 1", "KINDERGARTEN 2", "CRECHE"],
    "Primary": ["BASIC 1", "BASIC 2", "BASIC 3", "BASIC 4", "BASIC 5", "BASIC 6"],
    "JHS": ["JHS 1", "JHS 2", "JHS 3"]
}

fee_group_map: dict[str, list[str]] = {
    "JHS": ["JHS -Term 1", "JHS -Term 2", "JHS-Term 3"],
    "Pre School": ["Pre School-Term 1", "Pre School-Term 2", "Pre School-Term 3"],
    "Primary": ["Primary-Term 1", "Primary-Term 2", "Primary-Term 3"]
}


class Command(BaseCommand):
    help = "Create Students from initial data"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "file_path",
            help="Path to the CSV File containing the fee data in the correct format e.g student.csv"
        )
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        """Create students and Classes/levels, then add students"""
        filename = options["file_path"]
        type_of_file = Path(filename).suffix

        if type_of_file == ".xlsx":
            self.stdout.write(
                self.style.ERROR(
                    "Wrong File Format, Excel. Expected a CSV"
                    )
                )
            return
        elif type_of_file == ".csv":
            acad_year, _ = AcademicYear.objects.get_or_create(
                year=_academic_year
            )
            create_fees()
            create_fee_groups()
            acad_term = AcademicTerm.objects.get(
                academic_year=acad_year,
                term="First Term"
            )
            finance_user = User.objects.get(first_name="Florence", last_name="Ametepe")

            with open(filename, newline="") as csvfile:
                spamreader = csv.DictReader(csvfile, delimiter=",", quotechar="|")
                for row in spamreader:
                    my_class, _ = Class.objects.get_or_create(
                        name=row.get("class_name")
                    )
                    middle_name = row.get("middle_name", "")
                    if not middle_name:
                        middle_name: str = ""
                    studentID = generate_studentid(
                            row.get("first_name"), middle_name, row.get("last_name")
                    )

                    try:
                        student = Student.objects.get(
                            first_name=row.get("first_name"),
                            last_name=row.get("last_name"),
                            middle_name=middle_name
                        )
                    except Student.DoesNotExist:
                        try:
                            student = Student.objects.create(
                                student_id=studentID,
                                gender=row.get("gender"),
                                first_name=row.get("first_name"),
                                last_name=row.get("last_name"),
                                middle_name=middle_name,
                            )
                        except IntegrityError:
                            studentID = generate_studentid(
                                row.get("first_name"), middle_name, row.get("last_name")
                                )
                            student = Student.objects.create(
                                student_id=studentID,
                                gender=row["gender"],
                                first_name=row.get("first_name"),
                                last_name=row.get("last_name"),
                                middle_name=middle_name,
                            )
                    print(row.get("class_name"))
                    fee_group: list[str] = [key for key, value in class_group_map.items() if row.get("class_name") in value]

                    fee_group_obj = StudentFeeGroup.objects.get(
                        name=fee_group[0],
                        academic_year=acad_year
                    )

                    student_class = StudentClass.objects.create(
                        student=student,
                        academic_year=acad_year,
                        student_class=my_class,
                        fee_assigned=fee_group_obj
                    )
                    fees_obj = student_class.fee_assigned.fees.all()
                    first_term_amount = row.get("term_1_fees")
                    if first_term_amount.isnumeric() and not float(first_term_amount) <= 0.00:
                        first_term_payment = Payment.objects.create(
                            academic_year=acad_year,
                            academic_term=acad_term,
                            user=finance_user,
                            student=student,
                            fee=fees_obj.get(academic_term=acad_term),
                            amount=Decimal(row.get("term_1_fees")),
                            payment_method=row.get("term_1_payment_type")
                        )
            self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully created Students'
                        )
                    )


def read_from_csv_file() -> Any:
    """Read data from CSV file uploaded"""


# def create_academic_terms() -> Any:
#     """Create the 3 terms for the academic year"""
#     _term_vals = ["First Term", "Second Term", "Third Term"]
#     new_acad_year = AcademicYear.objects.get(year=_academic_year)
#     for item in _term_vals:
#         AcademicTerm.objects.get_or_create(
#             academic_year=new_acad_year,
#             term=item
#         )
#     return "Successfully created Academic terms"


def create_fees(academic_year_val: str = _academic_year) -> Any:
    """Create the fees for the current academic year"""
    _term_vals = ["First Term", "Second Term", "Third Term"]
    new_acad_year = AcademicYear.objects.get(year=academic_year_val)
    for obj, val in class_group_map.items():
        # for class_item in val:
        for term_item in _term_vals:
            my_acad_term, _ = AcademicTerm.objects.get_or_create(
                academic_year=new_acad_year,
                term=term_item
            )
            # print(obj, my_acad_term.term)
            prev_term_fee = Fee.objects.get(
                    name__icontains=obj,
                    academic_year=AcademicYear.objects.get(year="2023/2024"),
                    academic_term__term=my_acad_term.term
                )
            Fee.objects.get_or_create(
                academic_year=new_acad_year,
                academic_term=my_acad_term,
                name=prev_term_fee.name,
                amount=prev_term_fee.amount
            )


def create_fee_groups() -> Any:
    new_acad_year = AcademicYear.objects.get(year=_academic_year)
    """Create the student fee groups to be assigned to the Student"""
    for obj, val in fee_group_map.items():
        my_fee_group, created = StudentFeeGroup.objects.get_or_create(
            academic_year=new_acad_year,
            name=obj
        )
        if created:
            for fee_obj in val:
                _fee_obj = Fee.objects.get(name=fee_obj, academic_year=new_acad_year)
                my_fee_group.fees.add(_fee_obj)
