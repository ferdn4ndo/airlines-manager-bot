from rest_framework import exceptions, status

from api.services import translation


class PreconditionFailedException(exceptions.APIException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = translation.Messages.MSG_PRECONDITION_FAILED
    default_code = 'precondition_failed'
