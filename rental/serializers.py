from typing import List
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from supabasecon.client import supabase
from .models import Student, Play, Game, Sanction, Image, Notice, Material, OwedMaterial


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
        return obj.get_played_today()

    @extend_schema_field(int)
    def get_weekly_plays(self, obj):
        return obj.get_weekly_plays()

    @extend_schema_field(int)
    def get_sanctions_number(self, obj):
        return obj.get_sanctions_number()


class NoticeSerializer(ModelSerializer):
    class Meta:
        model = Notice
        fields = "__all__"


class NoticeGameSerializer(ModelSerializer):
    class Meta:
        model = Notice
        fields = ["cause", "play", "created_at"]
        read_only_fields = ["cause", "play", "created_at"]


class MaterialSerializer(ModelSerializer):

    class Meta:
        model = Material
        fields = "__all__"


class OwedMaterialSerializer(ModelSerializer):
    material_name = CharField(source="material.name", read_only=True)
    class Meta:
        model = OwedMaterial
        fields = "__all__"


class PlaySerializer(ModelSerializer):
    class Meta:
        model = Play
        fields = "__all__"


class PlayGameSerializer(PlaySerializer):
    owed_materials = SerializerMethodField()
    notices = SerializerMethodField()

    @extend_schema_field(NoticeSerializer(many=True))
    def get_notices(self, obj: Play) -> List[dict]:
        return NoticeGameSerializer(obj.student.get_notices(), many=True).data

    @extend_schema_field(OwedMaterialSerializer(many=True))
    def get_owed_materials(self, obj: Play) -> List[dict]:
        return OwedMaterialSerializer(obj.student.get_owed_material(), many=True).data


class GameUnauthenticatedSerializer(ModelSerializer):
    plays = SerializerMethodField()
    image = SerializerMethodField()

    class Meta:
        model = Game
        fields = "__all__"

    @extend_schema_field(int)
    def get_plays(self, obj: Game) -> int:
        return obj.get_plays().count()

    def get_image(self, obj: Game) -> str:
        image = obj.image
        if image is None:
            return None
        return supabase.storage.from_("Cyberprepa").get_public_url(image.image.name)


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
        return PlaySerializer(obj.get_plays(), many=True).data


class GameSerializerImageUrl(ModelSerializer):
    """Serializer for reading the game via an authenticated user"""
    plays = SerializerMethodField()
    image = SerializerMethodField()

    class Meta:
        model = Game
        fields = "__all__"
        extra_kwargs = {
            "plays": {"read_only": True},
            "image": {"read_only": True},
        }

    @extend_schema_field(PlayGameSerializer(many=True))
    def get_plays(self, obj: Game) -> List[dict]:
        return PlayGameSerializer(obj.get_plays(), many=True).data

    def get_image(self, obj: Game) -> str:
        image = obj.image
        if image is None:
            return None
        return supabase.storage.from_("Cyberprepa").get_public_url(image.image.name)


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
        return supabase.storage.from_("Cyberprepa").get_public_url(obj.image.name)
