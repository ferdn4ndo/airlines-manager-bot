from api.models import Airport

from .generic_audited_model_serializer import GenericAuditedModelSerializer


class AirportSerializer(GenericAuditedModelSerializer):

    class Meta:
        model = Airport
        fields = '__all__'
