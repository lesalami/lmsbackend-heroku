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


def generate_random_string(length=15) -> str:
    """
    Define the characters to use in the random string
    """
    # You can customize this as needed
    characters = string.ascii_letters + string.digits

    # Generate a random string of the specified length
    random_string = ''.join(secrets.choice(characters) for _ in range(length))

    return random_string


def generate_random_receipt_number(length=10) -> str:
    """Generating receipt number"""

    chars = string.digits

    random_string: str = "".join(secrets.choice(chars) for _ in range(length))
    return random_string


def get_initials(*args) -> str:
    first_letter = ""
    for n in args:
        if n is not None and n != "":
            # print(f"This is the string {n}")
            first_letter += n.strip()[0]
    return first_letter


class_to_fee_group: dict[str, tuple[str]] = {
    "Primary": (
        "BASIC 1", "BASIC 2", "BASIC 3", "BASIC 4", "BASIC 5", "BASIC 6"
    ),
    "Pre School": (
        "NURSERY 1", "NURSERY 2", "KINDERGARTEN 1", "KINDERGARTEN 2", "CRECHE"
    ),
    "JHS": (
        "JHS1", "JHS 2", "JHS3"
    )
}
