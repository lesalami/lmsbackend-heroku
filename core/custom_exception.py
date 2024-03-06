"""
Custom exception handler
"""
from rest_framework.views import exception_handler
# from django.core.exceptions import ValidationError
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == 405:
            response.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        elif response.status_code == 401:
            response.status_code = status.HTTP_401_UNAUTHORIZED
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
        if "detail" in response.data:
            response.data = {
                "message": response.data["detail"],
                "error_message": "An exception occured"
            }
        else:
            response.data = {
                "message": response.data,
                "error_message": "An exception occured"
            }
            # response.status_code = 400
        return response
