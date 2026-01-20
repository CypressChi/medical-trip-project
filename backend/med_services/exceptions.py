from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """Return errors in a unified JSON format."""
    response = exception_handler(exc, context)

    if response is None:
        return Response({'error': str(exc), 'status_code': 500}, status=500)

    detail = response.data
    if isinstance(detail, dict):
        message = detail.get('detail') or detail
    else:
        message = detail

    return Response(
        {'error': message, 'status_code': response.status_code},
        status=response.status_code
    )
