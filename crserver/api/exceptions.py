"""
Handled exceptions raised CustomValidationError.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.views import exception_handler


def _handle_generic_error(exc, context, response):
    response.data = {
        'success': False,
        'message': 'Validation error',
        'errors': response.data
    }

    return response


class CustomValidationError(APIException):
    default_detail = _('Validation error')  # or Invalid input

    def __init__(self, msg: str = default_detail, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        self.detail = {'success': False, 'message': msg}
