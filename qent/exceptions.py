from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(exc, ValidationError):
        errors = {}
        non_field_messages = []

        for field, msgs in response.data.items():
            if not isinstance(msgs, list):
                msgs = [msgs]

            # Global
            if field in ["non_field_errors", "login_error"]:
                non_field_messages.extend(msgs)
            else:
                errors[field] = msgs

        if non_field_messages:
            errors["message"] = (
                non_field_messages[0]
                if len(non_field_messages) == 1
                else non_field_messages
            )

        response.data = {
            "message": "Invalid Request",
            "errors": errors
        }

        return response

    # Other errors
    detail = response.data.get("detail")

    response.data = {
        "message": detail if detail else "Something went wrong",
        "errors": {}
    }

    return response