from rest_framework.permissions import IsAuthenticated


class IsLoggedIn(IsAuthenticated):
    def has_permission(self, request, view):
        # Always allow OPTIONS requests to ensure proper CORS checking
        if request.method == 'OPTIONS':
            return True

        return bool(request.user and request.user.is_authenticated)
