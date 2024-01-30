from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    healthy = serializers.BooleanField()


class LogSerializer(serializers.Serializer):
    line = serializers.IntegerField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
    user = serializers.CharField(read_only=True)
    action = serializers.CharField(read_only=True)
