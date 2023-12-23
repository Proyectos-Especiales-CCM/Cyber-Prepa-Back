from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    healthy = serializers.BooleanField()
