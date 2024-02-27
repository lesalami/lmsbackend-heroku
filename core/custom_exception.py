"""
Custom exception handler
"""
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == 405:
            response.status_code = 405
        elif response.status_code == 401:
            response.status_code = 401
        else:
            response.status_code = 400
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
