from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrStaffOrReadOnly(BasePermission):
    """ Object-level permission to only allow everybody to read an object, but only admins or staff to update it. """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        if not request.user or type(request.user) is AnonymousUser:
            return False

        return bool(request.user.is_admin or request.user.is_staff)
