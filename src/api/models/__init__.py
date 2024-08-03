from django.db.models import QuerySet

from api.exception.not_found_exception import NotFoundException

from .airport_model import Airport
from .user_model import CustomUser
from .price_model import Price
from .demand_model import Demand
from .line_model import Line


def get_object_or_404(queryset: QuerySet, *args, **kwargs):
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise NotFoundException
