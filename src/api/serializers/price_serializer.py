from api.models import Price

from .generic_audited_model_serializer import GenericAuditedModelSerializer


class PriceSerializer(GenericAuditedModelSerializer):

    class Meta:
        model = Price
        fields = '__all__'
