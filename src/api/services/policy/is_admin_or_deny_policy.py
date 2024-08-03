from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission


class IsAdminOrDeny(BasePermission):
    """
    Object-level permission to only allow admins to read/write it.
    Assumes the model instance has an `created_by` attribute.
    """
    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True

        if not request.user or type(request.user) is AnonymousUser:
            return False

        return bool(request.user.is_admin)
