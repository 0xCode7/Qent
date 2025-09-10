from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = "Invalid Request"

        if isinstance(exc, ValidationError):
            errors = {}
            for field, msgs in response.data.items():
                # Ensure msgs is always a list
                if not isinstance(msgs, list):
                    msgs = [msgs]

                field_messages = []
                for msg in msgs:
                    if msg == "This field is required.":
                        field_messages.append(f"{field.capitalize()} is required")
                    else:
                        field_messages.append(msg)
                errors[field] = field_messages

            response.data = {
                "message": message,
                "errors": errors
            }
        else:
            detail = response.data.get("detail")
            response.data = {
                "message": message,
                "errors": {"message": detail} if detail else response.data
            }

    return response
