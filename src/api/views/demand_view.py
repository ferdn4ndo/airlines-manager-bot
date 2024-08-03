from api.models import Demand
from api.serializers import DemandSerializer
from api.services import policy

from .generic_model_view import FullCRUDListModelViewSet


class DemandViewSet(FullCRUDListModelViewSet):
    permission_classes = [policy.IsAdminOrReadOnly]
    serializer_class = DemandSerializer

    def get_queryset(self):
        return Demand.objects.all()
