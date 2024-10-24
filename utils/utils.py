"""
Any helper functions
"""
import secrets
import string
import logging
from datetime import datetime

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


def generate_studentid(*args) -> str:
    """Generate Student ID"""
    # student_initial
    characters = string.ascii_uppercase + string.digits
    current_year: str = str(datetime.now().year)
    initials = get_initials(*args)

    random_string: str = ''.join(secrets.choice(characters) for _ in range(3))

    return "HHA" + random_string + initials + current_year


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
    return first_letter.upper()


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
