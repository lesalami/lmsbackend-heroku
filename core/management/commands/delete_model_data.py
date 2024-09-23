from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction


class Command(BaseCommand):
    help = "Delete all data from specified models"

    def add_arguments(self, parser):
        # Accept model names as command-line arguments
        parser.add_argument(
            'models',
            nargs='+',  # "+" means one or more model names can be passed
            type=str,
            help='Names of the models to delete data from (in the format app_label.ModelName)'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        models = options['models']

        for model_name in models:
            try:
                # Split the model name into app_label and model name
                app_label, model = model_name.split('.')

                # Get the model class dynamically
                model_class = apps.get_model(app_label, model)
                if model_class:
                    # Delete all data from the model's table
                    deleted_count, _ = model_class.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} records from {model_name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Model {model_name} not found"))
            except ValueError:
                self.stdout.write(self.style.ERROR(f"Invalid model format: {model_name}. Use 'app_label.ModelName'."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error deleting data from {model_name}: {str(e)}"))
