from rest_framework import exceptions, status

from api.services import translation


class NotAuthenticatedException(exceptions.APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = translation.Messages.MSG_NOT_AUTHENTICATED
    default_code = 'not_authenticated'
