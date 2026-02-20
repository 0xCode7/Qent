from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    # Validation Errors (serializer errors)
    if isinstance(exc, ValidationError):
        response.data = {
            "message": "Invalid Request",
            "errors": response.data
        }
        return response

    # (Authentication, Permission, NotFound, etc.)
    detail = response.data.get("detail")

    if detail:
        response.data = {
            "message": detail,
            "errors": {}
        }
    else:
        response.data = {
            "message": "Something went wrong",
            "errors": {}
        }

    return response