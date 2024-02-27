"""
Rest framework serializers for the User management requests
"""
# Import required modules
# Order: Builtin, third-party, local modules, etc
import logging
from django.contrib.auth import (
    get_user_model,
    # authenticate
)
# For translating messages for serializer response
from django.utils.translation import gettext as _

# Rest framework imports here
from rest_framework import serializers

from core.serializers import (
    BaseModelSerializer,
    OrganizationConfigSerializer
)

# from core.models import (
#     AcademicYear, Student, Subject,
#     Teacher, NonTeachingStaff, Class
# )
from user.tokens import account_activate

# Any other local import here
from utils.mail import send_activation_link

# Declare the logger for the file
logger = logging.getLogger(__name__)


class UserSerializer(BaseModelSerializer):
    """Serializer for the user API"""
    organization_config = serializers.SerializerMethodField()

    def get_organization_config(self, instance):
        """Return the org config on the """
        request = self.context.get('request', None)
        if request and request.path == '/api/finance/payrun/approve-by-list/':
            return OrganizationConfigSerializer(
                instance=instance.organization,
                context=self.context
            ).data
        else:
            return {}

    class Meta:
        model = get_user_model()
        fields = [
            "id", "email", "password",
            "first_name", "last_name",
            "user_type", "organization_config"
        ]
        # Subset of fields above with special constraints
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}
        # Subset of fields from above that are read only
        read_only_fields = ["id"]

    def create(self, validated_data):
        """Creating the user object"""
        logger.info("Creating the user object")
        # Convert to lower case for email validation to prevent duplicates
        validated_data["email"] = validated_data["email"].lower()

        current_user = self.context["request"].get("user", None)
        if current_user.is_authenticated:
            validated_data["organization"] = current_user.organization

        # Create the user object
        created_user = get_user_model().objects.create_user(
            **validated_data
            )
        if created_user:
            send_activation_link(
                created_user.email,
                created_user.pk,
                account_activate.make_token(created_user)
            )
            logger.info(
                "User created successfully with email {}".format(
                    created_user.email
                ))
            logger.info(created_user)
            return created_user
        else:
            logger.error("User creation failed")
            # If serializing fails
            return serializers.ValidationError(
                _("User creation failed"), code="authorization"
            )

    def update(self, instance, validated_data):
        """Update and return user."""
        logger.info("Updating user Object")
        # Eliminating the password plaintext
        password = validated_data.pop("password", None)
        # Standard update without the password
        user = super().update(instance, validated_data)

        if password:
            logger.info("hashing the provided password")
            user.set_password(password)
            user.save()

        return user


class ChangePasswordSerializzer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        fields = ["old_password", "new_password"]
