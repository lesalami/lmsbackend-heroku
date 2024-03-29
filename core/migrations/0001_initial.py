# Generated by Django 5.0.2 on 2024-02-26 23:52

import core.utils
import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationConfig',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=500)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='organization')),
                ('address', models.CharField(blank=True, max_length=700, null=True)),
                ('currency', models.CharField(default='GHC', max_length=150)),
                ('ssnit_rate', models.DecimalField(decimal_places=2, default=Decimal('0'), help_text='Percentage rate for SSNIT without tier 3', max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('tier_three', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('add_cash_allowance_before_tax', models.BooleanField(default=False)),
                ('tax_identification_number', models.CharField(blank=True, help_text='TIN for the school/church/business', max_length=100, null=True)),
                ('payroll_approval_required', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('student_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=300, null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male', max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('date_of_admission', models.DateField(blank=True, null=True)),
                ('blood_type', models.CharField(blank=True, max_length=150, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='students')),
                ('address', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('subject_id', models.CharField(max_length=150)),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('user_type', models.CharField(choices=[('Parent', 'Parent'), ('Staff', 'Staff'), ('Admin', 'Admin'), ('Headmaster', 'Headmaster'), ('Proprietor', 'Proprietor'), ('Accountant', 'Accountant')], default='Admin', max_length=50)),
                ('email_confirmed', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='organizational_user', to='core.organizationconfig')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('year', models.CharField(max_length=50, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('previous', models.OneToOneField(blank=True, help_text='Pointer to previous academic year', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='next', to='core.academicyear')),
            ],
        ),
        migrations.CreateModel(
            name='AcademicTerm',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('term', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('previous', models.OneToOneField(blank=True, help_text='Pointer to previous academic term', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='next', to='core.academicterm')),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.academicyear')),
            ],
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=300)),
                ('academic_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.academicterm')),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.academicyear')),
            ],
            options={
                'verbose_name_plural': 'Classes',
            },
        ),
        migrations.CreateModel(
            name='DatabaseActionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(max_length=50)),
                ('model_name', models.CharField(max_length=100)),
                ('object_id', models.CharField(blank=True, max_length=300, null=True)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('name', models.CharField(max_length=300)),
                ('academic_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.academicterm')),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.academicyear')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationDocument',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(upload_to=core.utils.get_upload_path)),
                ('name', models.CharField(max_length=500)),
                ('description', models.TextField(blank=True, null=True)),
                ('file_type', models.CharField(blank=True, choices=[('Income', 'Income'), ('Expenditure', 'Expenditure'), ('Invoice', 'Invoice')], max_length=300, null=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.organizationconfig')),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('staff_id', models.CharField(max_length=200, unique=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male', max_length=150)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='staff')),
                ('staff_type', models.CharField(choices=[('Teaching', 'Teaching'), ('Non-Teaching', 'Non_Teaching')], default='Teaching', max_length=100)),
                ('address', models.CharField(blank=True, max_length=300, null=True)),
                ('role', models.CharField(default='Teacher', help_text='Position/Role', max_length=500)),
                ('employment_type', models.CharField(choices=[('Full Time', 'Full_Time'), ('Part Time', 'Part_Time'), ('Contract', 'Contract'), ('Internship', 'Internship'), ('Other', 'Other')], default='Full_Time', max_length=200)),
                ('residency_status', models.CharField(choices=[('Non-Resident', 'Non_Resident'), ('Resident-Part-Time', 'Resident_Part_Time'), ('Resident_Casual', 'Resident_Casual'), ('Resident-Full-Time', 'Resident_Full_Time')], max_length=200)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Staff',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('owing_after_payment', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('payment_method', models.CharField(choices=[('Money money', 'Mobile_money'), ('Bank', 'Bank'), ('Cash', 'Cash')], default='Bank', max_length=200)),
                ('academic_term', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.academicterm')),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.academicyear')),
                ('fee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.fee')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.student')),
            ],
        ),
        migrations.CreateModel(
            name='ParentOrGuardian',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('full_name', models.CharField(blank=True, max_length=500, null=True)),
                ('relationship_with_student', models.CharField(max_length=400)),
                ('mobile_number', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('home_care_giver_name', models.CharField(blank=True, max_length=400, null=True)),
                ('name_of_father', models.CharField(max_length=400)),
                ('father_telephone', models.CharField(blank=True, max_length=100, null=True)),
                ('name_of_mother', models.CharField(max_length=400)),
                ('mother_telephone', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(blank=True, max_length=300, null=True)),
                ('students', models.ManyToManyField(blank=True, to='core.student')),
            ],
        ),
        migrations.CreateModel(
            name='StudentFeeGroup',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('fees', models.ManyToManyField(to='core.fee')),
            ],
        ),
        migrations.CreateModel(
            name='StudentClass',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('fee_paid', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('fee_owing', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('owing', models.BooleanField(default=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_in_class', to='core.student')),
                ('student_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_of_student', to='core.class')),
                ('fee_assigned', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.studentfeegroup')),
            ],
            options={
                'verbose_name_plural': 'Student Classes',
            },
        ),
        migrations.CreateModel(
            name='TeacherAssignment',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('academic_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.academicterm')),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.academicyear')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.subject')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_teacher', to='core.staff')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherClass',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_teacher_class', to='core.staff')),
                ('teacher_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.class')),
            ],
        ),
        migrations.AddConstraint(
            model_name='class',
            constraint=models.UniqueConstraint(fields=('name', 'academic_term'), name='unique_classes'),
        ),
        migrations.AddConstraint(
            model_name='studentclass',
            constraint=models.UniqueConstraint(fields=('student', 'student_class'), name='unique_student_classes'),
        ),
        migrations.AddConstraint(
            model_name='teacherclass',
            constraint=models.UniqueConstraint(fields=('teacher', 'teacher_class'), name='unique_teacher_classes'),
        ),
    ]
