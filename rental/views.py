"""
Views for handling the Cyber rental API and the websocket updates.
"""

import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from main.permissions import IsActive, IsInAdminGroupOrStaff, AdminWriteAllRead
from .models import Student, Play, Game, Sanction, Image
from .serializers import (
    StudentSerializer,
    PlaySerializer,
    GameUnauthenticatedSerializer,
    GameSerializer,
    GameSerializerImageUrl,
    SanctionSerializer,
    ImageSerializer,
    ImageReadSerializer,
)

transaction_logger = logging.getLogger("transactions")


def send_update_message(message, sender, info=None, room_group_name="updates"):
    """Send a message to the websocket to inform about the or something else"""
    try:
        channel_layer = get_channel_layer()
        if message == "Plays updated":
            data = {
                "type": "plays_updated",
                "message": message,
                "info": info,
                "sender": sender,
            }
        else:
            data = {
                "type": "update_message",
                "message": message,
                "sender": sender,
            }
        async_to_sync(channel_layer.group_send)(room_group_name, data)
    except Exception as e:
        transaction_logger.error("Error sending message to websocket: %s", e)


class PlayListCreateView(generics.ListCreateAPIView):
    """Create and Read Plays"""

    queryset = Play.objects.all().order_by("pk")
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive]
    serializer_class = PlaySerializer

    def create(self, request, *args, **kwargs):
        """
        Create a play and return it
        Also modify the game to set the start_time if it is the first play
        """
        student_id = request.data["student"]
        try:
            RegexValidator(r"^[a|l][0-9]{8}$")(student_id)
        except ValidationError:
            return Response(
                {"detail": "Invalid student id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        student, created = Student.objects.get_or_create(id=student_id)
        if created is False:
            if student.is_playing() is True:
                return Response(
                    {"detail": "Student is already playing"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if student.get_played_today() >= 1:
                return Response(
                    {"detail": "Student has already played today"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if student.get_weekly_plays() >= 3:
                return Response(
                    {"detail": "Student has already played 3 times this week"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if student.get_sanctions_number() > 0:
                return Response(
                    {"detail": "Student has sanctions"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            game = Game.objects.get(pk=request.data["game"])
        except Game.DoesNotExist:
            return Response(
                {"detail": "Game does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If game has no plays, then this is the first play, and we should set
        # the game start_time to the play time to start counting the 50 minutes
        if game.get_plays().count() == 0:
            response = super().create(request, *args, **kwargs)
            play = Play.objects.get(pk=response.data["id"])
            game.start_time = play.time
            game.save()
            # Send a message to the websocket to inform about the new play
            send_update_message(
                "Plays updated",
                request.user.email,
                info=game.pk,
            )
            transaction_logger.info(
                "%s initiated play %s for student %s at game %s",
                request.user.email,
                play.pk,
                play.student.id,
                play.game.name,
            )
            return response
        else:
            # If game.start_time is 50 or more minutes ago, then the game time
            # has expired and we should not allow more plays
            if game.start_time + timezone.timedelta(minutes=50) < timezone.now():
                return Response(
                    {"detail": "Game time has expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                response = super().create(request, *args, **kwargs)
                play = Play.objects.get(pk=response.data["id"])

                # Send a message to the websocket to inform about the new play
                send_update_message(
                    "Plays updated",
                    request.user.email,
                    info=game.pk,
                )

                transaction_logger.info(
                    "%s initiated play %s for student %s at game %s",
                    request.user.email,
                    play.pk,
                    play.student.id,
                    play.game.name,
                )
                return response


class PlayDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, Update and Delete Play(id)"""

    queryset = Play.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive]
    serializer_class = PlaySerializer
    http_method_names = ["get", "patch", "delete"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.data.get("student", None) is not None:
            return Response(
                {"detail": "Cannot change student"}, status=status.HTTP_400_BAD_REQUEST
            )
        elif request.data.get("time", None) is not None:
            return Response(
                {"detail": "Cannot change time"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Check if the play time has expired
        new_game = None
        if request.data.get("game", None) is not None:
            new_game = Game.objects.get(pk=request.data["game"])

            # First if, checks if both the previous and the new game time has expired
            if (
                instance.game.start_time + timezone.timedelta(minutes=50)
                < timezone.now()
                or new_game.start_time is not None
                and new_game.get_plays().count() != 0
                and new_game.start_time + timezone.timedelta(minutes=50)
                < timezone.now()
            ):
                return Response(
                    {"detail": "Game time has expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Second if, checks if actual player has already played more than 50 minutes
            elif instance.time + timezone.timedelta(minutes=50) < timezone.now():
                return Response(
                    {"detail": "Play time has expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        response = super().update(request, *args, **kwargs)
        # Change the game start_time if the play is the first one
        if new_game is not None and new_game.get_plays().count() == 1:
            prev_game = Game.objects.get(pk=instance.game.pk)
            new_game.start_time = prev_game.start_time
            new_game.save()

        transaction_logger.info(
            "%s updated play %s fields %s",
            request.user.email,
            instance.pk,
            serializer.validated_data.keys(),
        )
        # Send a message to the websocket to inform about the updated play
        # IMPORTANT: We need to send the info of both the previous and the new game
        send_update_message(
            "Plays updated",
            request.user.email,
            info=instance.game.pk,
        )
        if new_game is not None:
            send_update_message(
                "Plays updated",
                request.user.email,
                info=new_game.pk,
            )
        return response

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            transaction_logger.info(
                "%s deleted play %s", request.user.email, instance.pk
            )
            response = super().destroy(request, *args, **kwargs)
            # Send a message to the websocket to inform about the deleted play
            send_update_message(
                "Plays updated",
                request.user.email,
                info=instance.game.pk,
            )
            return response
        except ProtectedError:
            return Response(
                {"detail": "Cannot delete play as it has sanctions associated"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class StudentListCreateView(generics.ListCreateAPIView):
    """Create and Read Students"""

    queryset = Student.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]
    serializer_class = StudentSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        transaction_logger.info(
            "%s created student %s", request.user.email, response.data["id"]
        )
        return response


class StudentDetailView(generics.RetrieveDestroyAPIView):
    """Read, Update and Delete Student(id)"""

    queryset = Student.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]
    serializer_class = StudentSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            transaction_logger.info(
                "%s deleted student %s", request.user.email, instance.id
            )
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "detail": "Cannot delete student as it has plays or sanctions associated"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class GameListCreateView(generics.ListCreateAPIView):
    """Create and Read Games"""

    queryset = Game.objects.all().order_by("pk")
    permission_classes = [AdminWriteAllRead]

    def get_serializer_class(self):
        if self.request.method == "GET" and not self.request.user.is_authenticated:
            return GameUnauthenticatedSerializer
        elif self.request.method == "GET" and self.request.user.is_authenticated:
            return GameSerializerImageUrl
        else:
            return GameSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        transaction_logger.info(
            "%s created game %s", request.user.email, response.data["name"]
        )
        # Send a message to the websocket to inform about the new game
        send_update_message(
            "Games updated",
            request.user.email,
        )
        return response


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, Update and Delete Game(id)"""

    queryset = Game.objects.all()
    permission_classes = [AdminWriteAllRead]

    def get_serializer_class(self):
        if self.request.method == "GET" and not self.request.user.is_authenticated:
            return GameUnauthenticatedSerializer
        elif self.request.method == "GET" and self.request.user.is_authenticated:
            return GameSerializerImageUrl
        else:
            return GameSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response = super().update(request, *args, **kwargs)
        # Log the transaction
        transaction_logger.info(
            "%s updated game %s fields %s",
            request.user.email,
            response.data["name"],
            serializer.validated_data.keys(),
        )
        # Send a message to the websocket to inform about the updated game
        send_update_message(
            "Games updated",
            request.user.email,
        )
        return response

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            response = super().destroy(request, *args, **kwargs)
            # Log the transaction
            transaction_logger.info(
                "%s deleted game %s", request.user.email, instance.name
            )
            # Send a message to the websocket to inform about the deleted game
            send_update_message(
                "Games updated",
                request.user.email,
            )
            return response
        except ProtectedError:
            return Response(
                {"detail": "Cannot delete game as it has plays associated"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GameEndAllPlaysView(generics.GenericAPIView):
    """End all plays of a game"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive]
    serializer_class = GameSerializer

    @extend_schema(request=None, description="Set all plays of a game ended to True")
    def post(self, request, pk):
        game = generics.get_object_or_404(Game, pk=pk)
        game.end_all_plays()
        serializer = self.get_serializer(game)
        # Log the transaction
        transaction_logger.info(
            "%s ended all plays of game %s", request.user.email, game.name
        )
        # Send a message to the websocket to inform about updated plays
        send_update_message(
            "Plays updated",
            request.user.email,
            info=game.pk,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SanctionListCreateView(generics.ListCreateAPIView):
    """Create and Read Sanctions"""

    queryset = Sanction.objects.all().order_by("pk")
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive]
    serializer_class = SanctionSerializer

    def create(self, request, *args, **kwargs):
        student_id = request.data.get("student")

        try:
            RegexValidator(r"^[a|l][0-9]{8}$")(student_id)
        except ValidationError:
            return Response(
                {
                    "detail": "Invalid student ID. It should start with an 'A-a' followed by 8 digits."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        student, created = Student.objects.get_or_create(id=student_id)

        response = super().create(request, *args, **kwargs)
        transaction_logger.info(
            "%s created sanction %s for student %s",
            request.user.email,
            response.data["id"],
            student.id,
        )
        return response


class SanctionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, Update and Delete Sanction(id)"""

    queryset = Sanction.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive]
    serializer_class = SanctionSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        transaction_logger.info(
            "%s updated sanction %s fields %s",
            request.user.email,
            instance.pk,
            serializer.validated_data.keys(),
        )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        transaction_logger.info(
            "%s deleted sanction %s of student %s",
            request.user.email,
            instance.pk,
            instance.student.id,
        )
        return super().destroy(request, *args, **kwargs)


class ImageListCreateView(generics.ListCreateAPIView):
    """Create and Read Images"""

    queryset = Image.objects.all().order_by("pk")
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ImageReadSerializer
        else:
            return ImageSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        transaction_logger.info(
            "%s uploaded image %s", request.user.email, response.data["image"]
        )
        return response


class ImageDetailView(generics.RetrieveDestroyAPIView):
    """Read and Delete Image(id)"""

    queryset = Image.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ImageReadSerializer
        else:
            return ImageSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        transaction_logger.info(
            "%s deleted image %s", request.user.email, instance.image
        )
        return super().destroy(request, *args, **kwargs)
