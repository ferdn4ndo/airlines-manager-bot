from rest_framework import exceptions, status


class BaseError(exceptions.APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An internal error has occurred."
    default_code = 'internal_error'

    class Meta:
        abstract = True
