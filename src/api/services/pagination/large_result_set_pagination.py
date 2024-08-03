from .custom_pagination import CustomPagination

class LargeResultsSetPagination(CustomPagination):
    default_limit = 100
    max_limit = 1000
