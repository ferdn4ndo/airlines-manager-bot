from rest_framework import exceptions, status

from api.services import translation


class BadRequestException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = translation.Messages.MSG_INVALID_INPUT_DATA
    default_code = 'invalid'

    def __init__(self, detail=None):
        if detail is None:
            detail = self.default_detail

        # For validation failures, we may collect many exception together,
        # so the details should always be coerced to a list if not already.
        if not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        if not isinstance(detail, dict):
            self.detail = detail
            return

        self.detail = [
            {
                "field": validation_error_field,
                "error": detail[validation_error_field]
            } for validation_error_field in detail.keys()
        ]
