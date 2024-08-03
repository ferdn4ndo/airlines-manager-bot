from .custom_pagination import CustomPagination

class StandardResultsSetPagination(CustomPagination):
    default_limit = 10
    max_limit = 100
