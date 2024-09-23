"""
Management command to backup database
"""
import os
import subprocess
import boto3
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime


class Command(BaseCommand):
    help = "Back up the database and send the backup to an S3 bucket"

    def handle(self, *args, **options):
        # Define database backup file name and path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{timestamp}.sql"
        backup_file_path = os.path.join(settings.BASE_DIR, backup_file)

        # Create the database dump command based on the DB engine
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
            dump_command = f"PGPASSWORD={settings.DATABASES['default']['PASSWORD']} pg_dump -U {settings.DATABASES['default']['USER']} -h {settings.DATABASES['default']['HOST']} {settings.DATABASES['default']['NAME']} > {backup_file_path}"
        elif settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
            dump_command = f"mysqldump -u {settings.DATABASES['default']['USER']} -h {settings.DATABASES['default']['HOST']} {settings.DATABASES['default']['NAME']} > {backup_file_path}"
        else:
            self.stdout.write(self.style.ERROR("Unsupported database engine."))
            return

        # Run the command to back up the database
        try:
            subprocess.run(dump_command, shell=True, check=True)
            self.stdout.write(self.style.SUCCESS(f"Database backup created at {backup_file_path}"))

            # Upload to S3
            self.upload_to_s3(backup_file_path, backup_file)
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"Error during backup: {str(e)}"))

    def upload_to_s3(self, file_path, file_name):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        try:
            s3_client.upload_file(file_path, bucket_name, file_name)
            self.stdout.write(self.style.SUCCESS(f"Backup uploaded to S3 as {file_name}"))
            os.remove(file_path)  # Remove the local backup file after upload
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to upload to S3: {str(e)}"))
