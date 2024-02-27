"""
Token generated for signup email email confirmation
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class SignupActivationTokenGenerate(PasswordResetTokenGenerator):
    """Generate token for signup confirmation"""

    def _make_hash_value(self, user, timestamp: int) -> str:
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.email_confirmed)
        )


account_activate = SignupActivationTokenGenerate()
