from api.models import Line
from api.serializers import LineSerializer
from api.services import policy

from .generic_model_view import FullCRUDListModelViewSet


class LineViewSet(FullCRUDListModelViewSet):
    permission_classes = [policy.IsAdminOrReadOnly]
    serializer_class = LineSerializer

    def get_queryset(self):
        return Line.objects.all()
