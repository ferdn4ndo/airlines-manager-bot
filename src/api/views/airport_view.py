from api.models import Airport
from api.serializers import AirportSerializer
from api.services import policy

from .generic_model_view import FullCRUDListModelViewSet


class AirportViewSet(FullCRUDListModelViewSet):
    permission_classes = [policy.IsAdminOrReadOnly]
    serializer_class = AirportSerializer

    def get_queryset(self):
        return Airport.objects.order_by('+code').all()
