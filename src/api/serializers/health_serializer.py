from rest_framework import serializers

class HealthSerializer(serializers.Serializer):
    airports_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
