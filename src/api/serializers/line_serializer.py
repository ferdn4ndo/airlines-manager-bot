from api.models import Line

from .airport_serializer import AirportSerializer
from .demand_serializer import DemandSerializer
from .price_serializer import PriceSerializer
from .generic_audited_model_serializer import GenericAuditedModelSerializer


class LineSerializer(GenericAuditedModelSerializer):
    origin = AirportSerializer()
    destination = AirportSerializer()
    total_demand = DemandSerializer()
    ideal_cost = PriceSerializer()
    turnover = PriceSerializer()
    current_cost = PriceSerializer()

    class Meta:
        model = Line
        fields = '__all__'
