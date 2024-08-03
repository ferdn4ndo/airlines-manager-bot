from api.models import Demand

from .generic_audited_model_serializer import GenericAuditedModelSerializer


class DemandSerializer(GenericAuditedModelSerializer):

    class Meta:
        model = Demand
        fields = '__all__'
