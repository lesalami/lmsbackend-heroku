"""
Test user API flows
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")
# RESET_PASSWORD = reverse("user:api-password-reset:reset-password-request")
# RESET_PASSWORD_VALIDATE = reverse(
#     "user:api-password-reset:reset-password-validate"
#     )
# RESET_PASSWORD_CONFIRM = reverse(
#     "user:api-password-reset:reset-password-confirm"
#     )
# CHANGE_PASSWORD = reverse("user:api-change-password")


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class UserSignupFlowTests(TestCase):
    """Test the User Signup Flow"""

    def setUp(self):
        """Initial setup for test cases"""
        self.client = APIClient()

    # def test_retrieving_info_for_validation(self):
    #     """Test email validation"""
    #     user_payload = {
    #         "email": "test@example.com",
    #         "password": "testpass123",
    #         "first_name": "Test",
    #         "last_name": "Name",
    #         "user_type": "Admin",
    #     }
    #     res = self.client.post(CREATE_USER_URL, user_payload)

    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    #     email_body = mail.outbox[0].body
    #     new_str = email_body.split("validation")[-1]
    #     uid = new_str.split("=")[1][:-6]
    #     uid = uid.split("&")[0]
    #     token = new_str.split("=")[2].split("\n")[0]
    #     response = self.client.post(
    #         reverse("user:account-validation"),
    #         {
    #             "uid": uid,
    #             "token": token
    #         }
    #     )

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["data"]["email"], user_payload["email"])

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            "email": "test43@example.com",
            "password": "pw",
            "first_name": "Test",
            "last_name": "Name",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model().objects.filter(email=payload["email"]).exists()
        )
        self.assertFalse(user_exists)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            "email": "test12@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "Name",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_as_staff(self):
        """Test creating a user is successful."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "Name",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        """Set a company instance for the user"""
        self.client = APIClient()

    def test_signup_as_researcher(self):
        """Signup as a Researcher"""
        user_details = {
            "email": "test@example.com",
            "password": "test-user-password123ß",
            "first_name": "Test",
            "last_name": "Name",
        }
        response = self.client.post(
            CREATE_USER_URL,
            user_details
        )
        # print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["user_type"],
            "Admin"
        )
        self.assertEqual(response.data["email"], user_details["email"])

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            "email": "test@example.com",
            "password": "test-user-password123ß",
            "first_name": "Test",
            "last_name": "Name",
        }
        created_user = create_user(**user_details)
        created_user.is_active = True
        created_user.save()

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("access_token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        # create_user(email="testuser@example.com", password="goodpass")

        payload = {"email": "test@example.com", "password": "badpass123"}
        res_bad = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("access_token", res_bad.data)
        self.assertEqual(res_bad.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_email_not_found(self):
        """Test error returned if user not found for given email."""
        payload = {"email": "customuser@example.com", "password": "pass123"}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("access_token", res.data)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {"email": "test@example.com", "password": ""}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("access_token", res.data)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res.data.pop("id")
        # res.data.pop("profile")
        # res.data.pop("completion_rate")
        self.assertEqual(
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "user_type": "Admin",
            },
            res.data
        )

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {
            "first_name": "Updated",
            "last_name": "Name",
            "password": "newpassword123",
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertEqual(self.user.last_name, payload["last_name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PasswordResetTest(TestCase):
    """Test the password reset flow"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Name",
        )
        self.user.is_active = True
        self.user.save()

    # def test_password_reset_initiate(self):
    #     """Test the password reset flow"""
    #     payload = {
    #             "email": self.user.email
    #         }
    #     res = self.client.post(
    #         RESET_PASSWORD,
    #         payload
    #     )
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(res.data["status"], "OK")

    # def test_password_reset_token_validate(self):
    #     """Test reading link from email"""
    #     payload = {
    #             "email": self.user.email
    #         }
    #     res = self.client.post(
    #         RESET_PASSWORD,
    #         payload
    #     )
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     email_body = mail.outbox[0].body
    #     # print(email_body.split("token")[1].split("\n")[0].lstrip("="))
    #     token = email_body.split("token")[1].split("\n")[0].lstrip("=")
    #     # token = token[1:]
    #     # print(token)

    #     response = self.client.post(
    #         RESET_PASSWORD_VALIDATE,
    #         {"token": token}
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["status"], "OK")

    # def test_password_reset_success(self):
    #     """Confirm password reset"""
    #     payload = {
    #             "email": self.user.email
    #         }
    #     res = self.client.post(
    #         RESET_PASSWORD,
    #         payload
    #     )
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     email_body = mail.outbox[0].body
    #     token = email_body.split("token")[1].split("\n")[0].lstrip("=")
    #     # token = token[1:]

    #     user_creds = {
    #         "email": self.user.email,
    #         "password": "newPasswd23"
    #     }

    #     response = self.client.post(
    #         RESET_PASSWORD_CONFIRM,
    #         {"token": token, "password": user_creds["password"]}
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["status"], "OK")

    #     login_user = self.client.login(**user_creds)
    #     self.assertEqual(login_user, True)


# class ChangePasswordTests(TestCase):
#     """Test scenarios for change password"""

#     def setUp(self) -> None:
#         self.client = APIClient()
#         user = create_user(
#             email="test@example.com",
#             password="testpass123",
#             first_name="Test",
#             last_name="Name",
#         )
#         self.client.force_authenticate(user)

#     def test_initiate_change(self):
#         """Success change password"""
#         payload = {
#             "old_password": "testpass123",
#             "new_password": "newpasswd123"
#         }

#         res = self.client.patch(
#             CHANGE_PASSWORD,
#             payload
#         )
#         self.assertEqual(res.status_code, status.HTTP_200_OK)

#     def test_wrong_existing_password(self):
#         """Wrong existing password"""
#         payload = {
#             "old_password": "wrongpass123",
#             "new_password": "newpasswd123"
#         }
#         res = self.client.patch(
#             CHANGE_PASSWORD,
#             payload
#         )
#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
