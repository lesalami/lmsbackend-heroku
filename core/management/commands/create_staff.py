"""
Create an initial data for staff
"""
import string
import random
from faker import Faker
from datetime import datetime
from typing import Optional, Any
from django.core.management.base import BaseCommand, CommandParser
import csv

from core.models import (
    Staff,
    TeacherAssignment,
    TeacherClass,
    Class, Subject,
    AcademicYear, AcademicTerm,
    # StudentClass
    User,
    OrganizationConfig
)


class Command(BaseCommand):
    help = "Create Teachers"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        """Create teachers, teacherassignement and teacherclass"""
        acad_year, created = AcademicYear.objects.get_or_create(
            year=f"{datetime.now().year} - {datetime.now().year+1}"
        )
        acad_term, created = AcademicTerm.objects.get_or_create(
            academic_year=acad_year,
            term="First Term"
        )
        organization, org_created = OrganizationConfig.objects.get_or_create(
            name="Higher Heights Academy"
        )

        with open("HHA_Teachers.csv") as csvfile:
            spamreader = csv.reader(csvfile)
            headers = next(spamreader, None)
            for row in spamreader:
                fake = Faker()
                dob = fake.date_of_birth()
                subject, sub_created = Subject.objects.get_or_create(
                    name=row[2],
                    subject_id=row[3]
                )
                first_name = row[0].split()[0].lower()
                last_name = row[0].split()[1].lower()
                email = first_name + "." + last_name + "@gmail.com"
                rand_str = "".join(random.sample(string.ascii_letters, 12))
                myuser, user_created = User.objects.get_or_create(
                    email=email, first_name=first_name, last_name=last_name,
                    user_type="Teacher",
                    organization=organization,
                    is_active=True
                )
                myuser.set_password(rand_str)
                try:
                    teacher = Staff.objects.get(
                        user=myuser,
                        gender=row[1]
                    )
                except Staff.DoesNotExist:
                    teacher = Staff.objects.create(
                        user=myuser,
                        staff_id=rand_str,
                        gender=row[1],
                        date_of_birth=dob,
                        start_date=fake.date(),
                        staff_type="Teaching",
                        role="Teacher",
                        employment_type="Full Time",
                        residency_status="Resident-Full-Time"
                    )
                tee_assigned, ta_created = TeacherAssignment.objects.get_or_create(
                    teacher=teacher,
                    subject=subject,
                    academic_year=acad_year,
                    academic_term=acad_term
                )
                t_class, class_created = Class.objects.get_or_create(
                    name=row[4],
                    academic_year=acad_year,
                    academic_term=acad_term
                )
                tee_class, tc_created = TeacherClass.objects.get_or_create(
                    teacher=teacher, teacher_class=t_class
                )

                # print(f"{tee_assigned} in {tee_class}")
        self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created Teachers and Subjects'
                    )
                )
