from rest_framework import exceptions, status

from api.services import translation


class NotFoundException(exceptions.APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = translation.Messages.MSG_NOT_FOUND
    default_code = 'not_found'
