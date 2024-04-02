from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Student, Play, Game, Sanction, Image
from drf_spectacular.utils import extend_schema_field
from typing import List


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

    @extend_schema_field(int)
    def get_played_today(self, obj):
        return obj._get_played_today()

    @extend_schema_field(int)
    def get_weekly_plays(self, obj):
        return obj._get_weekly_plays()

    @extend_schema_field(int)
    def get_sanctions_number(self, obj):
        return obj._get_sanctions_number()


class PlaySerializer(ModelSerializer):
    class Meta:
        model = Play
        fields = "__all__"


class GameUnauthenticatedSerializer(ModelSerializer):
    plays = SerializerMethodField()
    image = SerializerMethodField()
    
    class Meta:
        model = Game
        fields = "__all__"

    @extend_schema_field(int)
    def get_plays(self, obj: Game) -> int:
        return obj._get_plays().count()
    
    def get_image(self, obj: Game) -> str:
        image = obj.image
        if image is None:
            return None
        return image.image.url


class GameSerializer(ModelSerializer):
    plays = SerializerMethodField()

    class Meta:
        model = Game
        fields = "__all__"
        extra_kwargs = {
            "plays": {"read_only": True},
        }

    @extend_schema_field(PlaySerializer(many=True))
    def get_plays(self, obj: Game) -> List[dict]:
        return PlaySerializer(obj._get_plays(), many=True).data


class GameSerializerImageUrl(ModelSerializer):
    plays = SerializerMethodField()
    image = SerializerMethodField()

    class Meta:
        model = Game
        fields = "__all__"
        extra_kwargs = {
            "plays": {"read_only": True},
            "image": {"read_only": True},
        }

    @extend_schema_field(PlaySerializer(many=True))
    def get_plays(self, obj: Game) -> List[dict]:
        return PlaySerializer(obj._get_plays(), many=True).data
    
    def get_image(self, obj: Game) -> str:
        image = obj.image
        if image is None:
            return None
        return image.image.url


class SanctionSerializer(ModelSerializer):
    class Meta:
        model = Sanction
        fields = "__all__"
        extra_kwargs = {
            "start_time": {"read_only": True},
        }


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class ImageReadSerializer(ModelSerializer):
    image = SerializerMethodField()
    class Meta:
        model = Image
        fields = "__all__"

    def get_image(self, obj: Image) -> str:
        return obj.image.url
