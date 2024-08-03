from rest_framework import exceptions, status

from api.services import translation


class PermissionDeniedException(exceptions.APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = translation.Messages.MSG_NOT_ENOUGH_PERMS
    default_code = 'permission_denied'
