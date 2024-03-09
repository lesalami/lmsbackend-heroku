"""
Any helper functions
"""
import secrets
import string
import logging
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from core.models import Payment, AcademicTerm
# from finance.models import Income, IncomeType

logger = logging.getLogger(__name__)


def generate_random_string(length=15):
    """
    Define the characters to use in the random string
    """
    # You can customize this as needed
    characters = string.ascii_letters + string.digits

    # Generate a random string of the specified length
    random_string = ''.join(secrets.choice(characters) for _ in range(length))

    return random_string


def generate_random_receipt_number(length=10):
    """Generating receipt number"""

    chars = string.digits

    random_string = "".join(secrets.choice(chars) for _ in range(length))
    return random_string


# @receiver(post_save, sender=Payment)
# def update_income(sender, instance, **kwargs):
#     """The payment object records an instance on the Income table"""

#     if instance:
#         try:
#             income_type = IncomeType.objects.get(name__icontains="Tuition")
#         except IncomeType.DoesNotExist:
#             income_type = IncomeType.objects.create(name="Tuition")
#         acad_term = instance.academic_term
#         if not acad_term:
#             acad_term = AcademicTerm.objects.get(is_active=True)
#         try:
#             purpose = f"Fee Payment for {instance.student.first_name}"
#             income_obj, _ = Income.objects.get_or_create(
#                 academic_year=instance.academic_year,
#                 student=instance.student,
#                 amount=instance.amount,
#                 income_type=income_type,
#                 user=instance.user,
#                 academic_term=acad_term,
#                 payment_id=instance.id,
#                 purpose=purpose
#                 )
#             logger.info(f"Income created successfully: {income_obj}")
#         except Exception as exc:
#             logger.error(exc.__str__())
