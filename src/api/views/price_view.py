from api.models import Price
from api.serializers import PriceSerializer
from api.services import policy

from .generic_model_view import FullCRUDListModelViewSet


class PriceViewSet(FullCRUDListModelViewSet):
    permission_classes = [policy.IsAdminOrReadOnly]
    serializer_class = PriceSerializer

    def get_queryset(self):
        return Price.objects.all()
