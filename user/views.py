"""
Views for the user API.
"""
from typing import List
import logging
from django.contrib.auth import authenticate
from rest_framework import (
    generics,
    # authentication,
    permissions, status
)
from django.dispatch import receiver
# from django.shortcuts import redirect
# from django.contrib import messages

# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authentication import TokenAuthentication
from rest_framework.settings import api_settings
from rest_framework.response import Response
# from rest_framework.decorators import api_view

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django_rest_passwordreset.signals import reset_password_token_created

from user.serializers import (
    UserSerializer,
    ChangePasswordSerializzer,
)
from core.models import User

from user.tokens import account_activate
from utils.mail import send_password_reset_link


logger = logging.getLogger(__name__)


class CreateUserView(generics.CreateAPIView):
    """Create a new user object"""

    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class CreateTokenView(TokenObtainPairView):
    """Create a new auth token for user."""
    # serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        logger.info("Obtaining the user tokens for authorization")
        email = request.data.get("email").lower()
        password = request.data.get("password")

        # Get user and check if email_confirmed and active status is false
        try:
            myuser = User.objects.get(email=email)
            # print("The user is ", myuser)
            # TODO: Implement a password confirmation screen for
            # first time users on frontend
            if not myuser.is_active and not myuser.email_confirmed:
                logger.info(f"User {myuser} is logging in for the first time")
                myuser.set_password(password)
                myuser.is_active = True
                myuser.email_confirmed = True
                myuser.save()

            user = authenticate(
                    email=email,
                    password=password,
                )
            if user:
                logger.info("User successfully authenticated")
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                }, status=status.HTTP_200_OK)
            logger.error("Invalid credentials. Could not obtail tokens")
            return Response({
                "message": "Invalid Email or Password"
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                "message": f"User with email {email} does not exist"
            }, status=status.HTTP_404_NOT_FOUND)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names: List[str] = ["get", "patch"]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class AccountValidationView(generics.GenericAPIView):
    """Validate, set password and activate"""
    serializer_class = UserSerializer
    http_method_names: list[str] = ["post"]

    def post(self, request, *args, **kwargs):
        logger.info("Initial Account validation for new signup/user")
        uid = self.request.data["uid"]
        token = self.request.data["token"]
        logger.info("Provided User ID: {}".format(uid))
        try:
            user = User.objects.get(pk=uid)
            if account_activate.check_token(user, token):
                logger.info("User details checks out")
                serializer = UserSerializer(user, context={'request': request})
                logger.info("User exists. Account activated")
                user.is_active = True
                user.email_confirmed = True
                user.save()
                return Response(
                    {
                        "message": "Account activated",
                        "data": serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                logger.info("Account activation link is expired")
                return Response({
                    "message": "Link is expired..."
                }, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            logger.error(
                "No User information for the provided link. Contact Admin"
                )
            return Response({
                "message": "User does not Exist"
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializzer
    model = User
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargsa):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        logger.info("Updating user's Password")

        if serializer.is_valid():
            logger.info("Serializer checks passed")
            # check old password
            old_pass = serializer.data.get("old_password")
            if not self.object.check_password(old_pass):
                logger.info("Exising password mismatch")
                return Response(
                    {"old_password": ["Current password is Wrong"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            logger.info("Existing password matched. Changing")
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            logger.info("User password updated successfully")
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
                "data": [],
            }
            return Response(response)


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    """Doing a proxy call so this lands on the MQ"""
    logger.info("Task received")
    print(reset_password_token)
    send_password_reset_link(
        reset_password_token.key,
        reset_password_token.user.email
    )
    logger.info("Sent email to Celery worker")
