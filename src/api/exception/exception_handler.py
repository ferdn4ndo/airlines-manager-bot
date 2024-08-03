from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import set_rollback

from api.services.translation import Messages

from .bad_request_exception import BadRequestException
from .not_authenticated_exception import NotAuthenticatedException
from .not_found_exception import NotFoundException
from .permission_denied_exception import PermissionDeniedException


def custom_exception_handler(exc: Exception, context):
    # The context argument is not used by the default handler, but can be useful if the exception handler needs
    # further information such as the view currently being handled, which can be accessed as context['view'].

    if isinstance(exc, Http404):
        exc = NotFoundException()
    elif isinstance(exc, exceptions.PermissionDenied):
        exc = PermissionDeniedException()
    elif isinstance(exc, exceptions.NotAuthenticated):
        exc = NotAuthenticatedException()
    elif isinstance(exc, exceptions.ValidationError):
        exc = BadRequestException(detail=exc.detail)

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if hasattr(exc, 'auth_header'):
            headers['WWW-Authenticate'] = getattr(exc, 'auth_header')
        if hasattr(exc, 'wait'):
            headers['Retry-After'] = '%d' % getattr(exc, 'wait')

        if isinstance(exc.detail, (list, dict)):
            data = {
                'message': Messages.MSG_ONE_OR_MORE_ERRORS_OCCURRED,
                'exception': exc.detail
            }
        else:
            data = {'message': exc.detail}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None
