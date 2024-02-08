from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from .serializers import (
    StudentSerializer,
    PlaySerializer,
    GameUnauthenticatedSerializer,
    GameSerializer,
    GameSerializerImageUrl,
    SanctionSerializer,
    ImageSerializer,
)
from .models import Student, Play, Game, Sanction, Image
from django.core.validators import RegexValidator
from main.permissions import IsActive, IsInAdminGroupOrStaff, AdminWriteAllRead
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models.deletion import ProtectedError
from django.utils import timezone
import logging
from drf_spectacular.utils import extend_schema
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

transaction_logger = logging.getLogger("transactions")


def send_update_message(message, sender, info=None, room_group_name="updates"):
    """Send a message to the websocket to inform about the or something else"""
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


class PlayListCreateView(generics.ListCreateAPIView):
    """Create and Read Plays"""

    queryset = Play.objects.all()
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
            RegexValidator(r"^[A|L][0-9]{8}$")(student_id)
        except:
            return Response(
                {"detail": "Invalid student id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        student, created = Student.objects.get_or_create(id=student_id)
        if created == False:
            if student._is_playing() == True:
                return Response(
                    {"detail": "Student is already playing"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if student._get_played_today() >= 1:
                return Response(
                    {"detail": "Student has already played today"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if student._get_weekly_plays() >= 3:
                return Response(
                    {"detail": "Student has already played 3 times this week"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if student._get_sanctions_number() > 0:
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
        if game._get_plays().count() == 0:
            response = super().create(request, *args, **kwargs)
            play = Play.objects.get(pk=response.data["id"])
            game.start_time = play.time
            game.save()
            transaction_logger.info(
                f"{request.user.email} initiated play {play.pk} for student {play.student.id} at game {play.game.name}"
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
                    f"{request.user.email} initiated play {play.pk} for student {play.student.id} at game {play.game.name}"
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
        if request.data.get("student", None) != None:
            return Response(
                {"detail": "Cannot change student"}, status=status.HTTP_400_BAD_REQUEST
            )
        elif request.data.get("time", None) != None:
            return Response(
                {"detail": "Cannot change time"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response = super().update(request, *args, **kwargs)
        transaction_logger.info(
            f"{request.user.email} updated play {instance.pk} fields {serializer.validated_data.keys()}"
        )
        # Send a message to the websocket to inform about the updated play
        send_update_message(
            "Plays updated",
            request.user.email,
            info=instance.game.pk,
        )
        return response

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            transaction_logger.info(f"{request.user.email} deleted play {instance.pk}")
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
            f"{request.user.email} created student {response.data['id']}"
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
                f"{request.user.email} deleted student {instance.id}"
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

    queryset = Game.objects.all()
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
            f"{request.user.email} created game {response.data['name']}"
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
            f"{request.user.email} updated game {response.data['name']} fields {serializer.validated_data.keys()}"
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
                f"{request.user.email} deleted game {instance.name}"
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
        game._end_all_plays()
        serializer = self.get_serializer(game)
        # Log the transaction
        transaction_logger.info(
            f"{request.user.email} ended all plays of game {game.name}"
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

    queryset = Sanction.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive]
    serializer_class = SanctionSerializer

    def create(self, request, *args, **kwargs):
        student_id = request.data.get("student")

        try:
            RegexValidator(r"^[A][0-9]{8}$")(student_id)
        except:
            return Response(
                {
                    "detail": "Invalid student ID format. It should start with 'A' followed by 8 digits."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        student, created = Student.objects.get_or_create(id=student_id)

        response = super().create(request, *args, **kwargs)
        transaction_logger.info(
            f"{request.user.email} created sanction {response.data['id']} for student {student.id}"
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
            f"{request.user.email} updated sanction {instance.pk} fields {serializer.validated_data.keys()}"
        )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        transaction_logger.info(
            f"{request.user.email} deleted sanction {instance.pk} of student {instance.student.id}"
        )
        return super().destroy(request, *args, **kwargs)


class ImageListCreateView(generics.ListCreateAPIView):
    """Create and Read Images"""

    queryset = Image.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]
    serializer_class = ImageSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        transaction_logger.info(
            f"{request.user.email} uploaded image {response.data['image']}"
        )
        return response


class ImageDetailView(generics.RetrieveDestroyAPIView):
    """Read and Delete Image(id)"""

    queryset = Image.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]
    serializer_class = ImageSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        transaction_logger.info(f"{request.user.email} deleted image {instance.image}")
        return super().destroy(request, *args, **kwargs)
