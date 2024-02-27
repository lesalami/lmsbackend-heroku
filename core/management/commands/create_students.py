"""
Create an initial data for students
"""
import random
# import string
from faker import Faker
from datetime import datetime
from typing import Optional, Any
from django.core.management.base import BaseCommand, CommandParser
from django.db.utils import IntegrityError
import openpyxl

from core.models import (
    Student, Class, AcademicYear,
    AcademicTerm, StudentClass
    # User
)


class Command(BaseCommand):
    help = "Create Students from initial data"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        """Create students and Classes/levels, then add students"""
        acad_year, created = AcademicYear.objects.get_or_create(
            year=f"{datetime.now().year} - {datetime.now().year+1}"
        )
        acad_term, created = AcademicTerm.objects.get_or_create(
            academic_year=acad_year,
            term="First Term"
        )

        blood_grps = ["A+", "AB+", "B+", "O+", "A-", "B-", "AB-", "O-"]

        class_list = ["creche", "nursery", "kindergarten", "basic", "jhs"]
        dataframe = openpyxl.load_workbook("HHA_Students_Enrolment.xlsx")

        name_list = dataframe.sheetnames
        # dataframe1 = dataframe[name_list[9]]
        for name in name_list:
            dataframe1 = dataframe[name_list[name_list.index(name)]]
            my_class, created = Class.objects.get_or_create(
                        name=name,
                        academic_year=acad_year,
                        academic_term=acad_term
                    )

            for row in range(0, dataframe1.max_row):
                for col in dataframe1.iter_cols(1, dataframe1.max_column):
                    # print(type(col[row].value), col[row].value)
                    if col[row].value is not None:
                        if not any(
                            s in col[row].value.lower() for s in class_list
                                ):
                            # print(col[row].value)
                            fake = Faker()
                            dob = fake.date_of_birth()
                            student_name = col[row].value.capitalize()
                            date_of_admission = fake.date()
                            [middle_name] = [
                                " ".join(
                                    student_name.split()[1:-1]
                                ).capitalize(
                                ) if len(student_name.split()) > 2 else ""
                                ]
                            studentID = "HHA_" + "".join(next(zip(
                                *student_name.split()
                                ))).upper() + str(
                                datetime.strptime(
                                    date_of_admission, "%Y-%m-%d"
                                ).strftime("%Y")
                                )
                            try:
                                student = Student.objects.get(
                                    first_name=student_name.split()[-1],
                                    last_name=student_name.split()[0],
                                    middle_name=middle_name
                                )
                            except Student.DoesNotExist:
                                try:
                                    student = Student.objects.create(
                                        student_id=studentID,
                                        gender=random.choice(["Male", "Female"]),
                                        first_name=student_name.split(
                                        )[-1].capitalize(),
                                        last_name=student_name.split(
                                        )[0].capitalize(),
                                        middle_name=middle_name,
                                        date_of_birth=dob,
                                        date_of_admission=date_of_admission,
                                        blood_type=random.choice(blood_grps)
                                    )
                                except IntegrityError:
                                    studentID = "HHA_02" + "".join(next(zip(
                                        *student_name.split()
                                        ))).upper() + str(
                                        datetime.strptime(
                                            date_of_admission, "%Y-%m-%d"
                                        ).strftime("%Y")
                                        )
                                    student = Student.objects.create(
                                        student_id=studentID,
                                        gender=random.choice(["Male", "Female"]),
                                        first_name=student_name.split(
                                        )[-1].capitalize(),
                                        last_name=student_name.split(
                                        )[0].capitalize(),
                                        middle_name=middle_name,
                                        date_of_birth=dob,
                                        date_of_admission=date_of_admission,
                                        blood_type=random.choice(blood_grps)
                                    )

                            student_class, created = StudentClass.objects.get_or_create(
                                student=student,
                                student_class=my_class
                            )
                            # print(f"{student} in {student_class}")
        self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created Students'
                    )
                )
