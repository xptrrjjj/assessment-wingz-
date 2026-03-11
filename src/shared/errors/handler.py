from rest_framework.response import Response
from rest_framework.views import exception_handler

from shared.errors.exceptions import ApplicationError


def custom_exception_handler(exc, context):
    if isinstance(exc, ApplicationError):
        return Response(
            {
                "error": {
                    "type": exc.__class__.__name__,
                    "detail": exc.detail,
                    "extra": exc.extra,
                }
            },
            status=exc.status_code,
        )

    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "error": {
                "type": exc.__class__.__name__,
                "detail": response.data,
                "extra": {},
            }
        }

    return response
