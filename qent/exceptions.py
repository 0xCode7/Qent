from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = "Invalid Request"
        errors = {}

        if isinstance(exc, ValidationError):
            for field, msgs in response.data.items():
                if not isinstance(msgs, list):
                    msgs = [msgs]

                field_messages = []
                for msg in msgs:
                    if msg.startswith("This field"):
                        field_name = field.replace("_", " ").capitalize()
                        field_messages.append(f"{field_name} is required")
                    else:
                        field_messages.append(msg)

                # If it’s login_error → collapse to single message
                if field == "login_error":
                    errors = {"message": field_messages[0] if len(field_messages) == 1 else field_messages}
                else:
                    errors[field] = field_messages
        else:
            detail = response.data.get("detail")
            if detail:
                errors = {"message": detail}
            else:
                errors = response.data

        response.data = {
            "message": message,
            "errors": errors
        }

    return response
