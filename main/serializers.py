from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    healthy = serializers.BooleanField()


class Log():
    def __init__(self, line, timestamp, user, action) -> None:
        self.line = line
        self.timestamp = timestamp
        self.user = user
        self.action = action

    def __str__(self) -> str:
        return f'{self.line} {self.timestamp} {self.user} {self.action}'


class LogSerializer(serializers.Serializer):
    line = serializers.IntegerField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
    user = serializers.CharField(read_only=True)
    action = serializers.CharField(read_only=True)

    def create(self, validated_data):
        return Log(**validated_data)

    def update(self, instance, validated_data):
        instance.line = validated_data.get('line', instance.line)
        instance.timestamp = validated_data.get('timestamp', instance.timestamp)
        instance.user = validated_data.get('user', instance.user)
        instance.action = validated_data.get('action', instance.action)
        return instance
