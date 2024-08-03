from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from api.serializers import HealthSerializer
from api.services import policy, throttling
from api.services.health import HealthService


class HealthView(APIView):
    permission_classes = [policy.AllowAll]

    def get(self, request):
        service = HealthService()
        serializer = HealthSerializer(service)

        return Response(serializer.data, status=status.HTTP_200_OK)
