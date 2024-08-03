from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.services import policy


class CronJobView(APIView):
    permission_classes = [policy.AllowAll]

    def get(self, request, format=None):
        cron_class_names = getattr(settings, 'CRON_CLASSES', [])

        return Response("Crons executed: {}".format(", ".join(cron_class_names)))
