from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Student, Play, Game, Sanction


class StudentSerializer(ModelSerializer):
    played_today = SerializerMethodField()
    weekly_plays = SerializerMethodField()
    sanctions_number = SerializerMethodField()

    class Meta:
        model = Student
        fields = "__all__"
        extra_kwargs = {
            "hash": {"write_only": True},
            "played_today": {"read_only": True},
            "weekly_plays": {"read_only": True},
            "sanctions_number": {"read_only": True},
        }

    def get_played_today(self, obj):
        return obj._get_played_today()

    def get_weekly_plays(self, obj):
        return obj._get_weekly_plays()

    def get_sanctions_number(self, obj):
        return obj._get_sanctions_number()


class PlaySerializer(ModelSerializer):
    class Meta:
        model = Play
        fields = "__all__"


class GameSerializer(ModelSerializer):
    plays = SerializerMethodField()

    class Meta:
        model = Game
        fields = "__all__"
        extra_kwargs = {
            "plays": {"read_only": True},
        }

    def get_plays(self, obj):
        return PlaySerializer(obj._get_plays(), many=True).data


class SanctionSerializer(ModelSerializer):
    class Meta:
        model = Sanction
        fields = "__all__"
