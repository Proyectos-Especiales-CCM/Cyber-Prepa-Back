"""
Views for handling the Cyber rental API and the websocket updates.
"""

import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.strings import safe_ascii
from main.permissions import (
    IsActive,
    IsInAdminGroupOrStaff,
    AdminWriteAllRead,
    UsersWriteAllRead,
)
from .models import (
    Student,
    Play,
    Game,
    Sanction,
    Image,
    Notice,
    Material,
    OwedMaterial,
    Announcement,
)
from .pagination import PlayListPagination
from .serializers import (
    NoticeSerializer,
    StudentSerializer,
    PlaySerializer,
    GameUnauthenticatedSerializer,
    GameSerializer,
    GameSerializerImageUrl,
    SanctionSerializer,
    ImageSerializer,
    ImageReadSerializer,
    MaterialSerializer,
    OwedMaterialSerializer,
    PaginationMetadataSerializer,
    AnnouncementSerializer,
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

    queryset = Play.objects.all().order_by("-pk")
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive]
    serializer_class = PlaySerializer
    pagination_class = PlayListPagination

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


class PlayPaginationMetadataView(APIView):
    """View to return pagination metadata for Play objects."""

    def get(self, request, *args, **kwargs):
        # Pagination details
        page_size = request.query_params.get("page_size", 100)
        total_count = Play.objects.count()
        num_pages = (total_count // int(page_size)) + (
            1 if total_count % int(page_size) > 0 else 0
        )

        pagination_data = {
            "count": total_count,
            "num_pages": num_pages,
            "page_size": int(page_size),
        }

        serializer = PaginationMetadataSerializer(data=pagination_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


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

        student, _ = Student.objects.get_or_create(id=student_id)

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


class NoticeListCreateView(generics.ListCreateAPIView):
    """Create and Read Notices"""

    queryset = Notice.objects.all().order_by("pk")
    permission_classes = [UsersWriteAllRead]
    serializer_class = NoticeSerializer


class NoticeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, Update and Delete Notice(id)"""

    queryset = Notice.objects.all()
    permission_classes = [UsersWriteAllRead]
    serializer_class = NoticeSerializer


class StudentSetForgotIdView(generics.GenericAPIView):
    """Set a play to end and sets forgoten_id to True"""

    permission_classes = [IsActive]
    serializer_class = StudentSerializer

    @extend_schema(
        request=None,
        description="End the requested play and the student forgoten_id to True",
    )
    def post(self, request, pk):
        play = generics.get_object_or_404(Play, pk=pk)
        student = play.student
        student.forgoten_id = True
        student.save()
        serializer = self.get_serializer(student)
        # Log the transaction
        transaction_logger.info(
            "%s ended play for %s and forgotten id %s",
            request.user.email,
            play.game.name,
            student.pk,
        )
        # Send a message to the websocket to inform about the new play
        send_update_message(
            "Plays updated",
            request.user.email,
            info=play.game.pk,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentRemoveForgotIdView(generics.GenericAPIView):
    """Sets forgoten_id to False"""

    permission_classes = [IsActive]
    serializer_class = StudentSerializer

    @extend_schema(
        request=None,
        description="Set student forgoten_id to False",
    )
    def post(self, request, pk):
        student = generics.get_object_or_404(Student, pk=pk)
        student.forgoten_id = False
        student.save()
        serializer = self.get_serializer(student)
        # Log the transaction
        transaction_logger.info("%s returned id to %s", request.user.email, student.pk)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MaterialListCreateView(generics.ListCreateAPIView):
    """Creates and reads all available material"""

    queryset = Material.objects.all().order_by("pk")
    permission_classes = [AdminWriteAllRead]
    serializer_class = MaterialSerializer


class MaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, Update and Delete Material(id)"""

    queryset = Material.objects.all()
    permission_classes = [AdminWriteAllRead]
    serializer_class = MaterialSerializer


class OwedMaterialListCreateView(generics.ListCreateAPIView):
    """Creates and reads all available material"""

    queryset = OwedMaterial.objects.all().order_by("pk")
    permission_classes = [UsersWriteAllRead]
    serializer_class = OwedMaterialSerializer

    def create(self, request, *args, **kwargs):
        # Validate request data through regex and serializer
        try:
            student_id = request.data["student"]
        except KeyError:
            return Response(
                {"student": ["This field is required"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RegexValidator(r"^[a|l][0-9]{8}$")(student_id)
        except ValidationError:
            return Response(
                {"detail": "Invalid student id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        student = Student.objects.get_or_create(id=student_id)[0]

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        material = serializer.validated_data.get("material")

        # Get the owed material for the student and material if exists
        owed_material = OwedMaterial.objects.filter(
            student=student, material=material
        ).first()
        if owed_material is not None:
            amount = serializer.validated_data.get("amount")
            if not amount:
                return Response(
                    {"amount": ["This field is required"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            owed_material.amount += amount
            owed_material.delivered += serializer.validated_data.get("delivered", 0)
            # Update delivey_deadline with the closest date
            delivery_deadline = serializer.validated_data.get("delivery_deadline")
            if delivery_deadline is not None:
                if owed_material.delivery_deadline is None:
                    owed_material.delivery_deadline = delivery_deadline
                elif delivery_deadline < owed_material.delivery_deadline:
                    owed_material.delivery_deadline = delivery_deadline
            else:
                # Create an inmediate sanction if there is no delivery_deadline
                owed_material.delivery_deadline = None
                sanction = Sanction(
                    cause=f"Creando sanción por deber {owed_material.amount} {material.name}",
                    owed_material=owed_material,
                    student=student,
                    # Approx. 4 years duration
                    end_time=timezone.now() + timezone.timedelta(weeks=4 * 12 * 4),
                )
                sanction.save()
                transaction_logger.info(
                    "%s creo sancion para %s por deber %s %s",
                    request.user.email,
                    student.id,
                    owed_material.amount,
                    material.name,
                )
            # Reverify if student has already delivered material so we can update the amount
            if owed_material.delivered >= owed_material.amount:
                # Delete sanction if any
                sanction = Sanction.objects.filter(owed_material=owed_material).first()
                if sanction is not None:
                    sanction.delete()
                    transaction_logger.info(
                        "%s deleted sanction for student %s material fully delivered",
                        request.user.email,
                        student.id,
                    )
                # Reset the owed material to display no owed material
                owed_material.delivered -= owed_material.amount
                owed_material.amount = 0
                if owed_material.delivered == 0:
                    owed_material.delete()
                    transaction_logger.info(
                        "%s added %s owed %s for student %s and was fully delivered, deleting",
                        request.user.email,
                        amount,
                        material.name,
                        student.id,
                    )
                    return Response(status=status.HTTP_204_NO_CONTENT)

            owed_material.save()
            response = self.get_serializer(owed_material)
            transaction_logger.info(
                "%s added %s owed %s for student %s",
                request.user.email,
                amount,
                material.name,
                student.id,
            )
            return Response(response.data, status=status.HTTP_201_CREATED)
        else:
            response = super().create(request, *args, **kwargs)
            # Aqui crear la sanción en caso de que no haya fecha límite
            if response.data["delivery_deadline"] is None:
                sanction = Sanction(
                    cause=f"Creando sanción por deber {response.data['amount']} {material.name}",
                    owed_material=OwedMaterial.objects.filter(pk=response.data["id"]).first(),
                    student=student,
                    # Approx. 4 years duration
                    end_time=timezone.now() + timezone.timedelta(weeks=4 * 12 * 4),
                )
                sanction.save()
                transaction_logger.info(
                    "%s created sanction for student %s material %s",
                    request.user.email,
                    student.id,
                    response.data["id"],
                )
            transaction_logger.info(
                "%s created owed %s - %s for student %s",
                request.user.email,
                response.data["amount"],
                material.name,
                student.id,
            )
            return response


class OwedMaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, Update and Delete OwedMaterial(id)"""

    queryset = OwedMaterial.objects.all()
    permission_classes = [UsersWriteAllRead]
    serializer_class = OwedMaterialSerializer

    def update(self, request, *args, **kwargs):
        # Validate request data through regex and serializer
        try:
            student_id = request.data["student"]
            RegexValidator(r"^[a|l][0-9]{8}$")(student_id)
            _ = Student.objects.get_or_create(id=student_id)
        except KeyError:
            pass
        except ValidationError:
            return Response(
                {"detail": "Invalid student id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response = super().update(request, *args, **kwargs)
        transaction_logger.info(
            "%s updated owed material %s fields %s",
            request.user.email,
            response.data["id"],
            serializer.validated_data.keys(),
        )
        return response


class OwedMaterialReturnView(generics.GenericAPIView):
    """Return an OwedMaterial"""

    permission_classes = [IsActive]
    serializer_class = OwedMaterialSerializer

    @extend_schema(
        request=None,
        description="Return an OwedMaterial",
    )
    def post(self, request, pk):
        owed_material = generics.get_object_or_404(OwedMaterial, pk=pk)
        data = request.data
        amount = data.get("amount", None)
        if amount is None:
            return Response(
                {"amount": ["This field is required"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(amount, int) or amount <= 0:
            return Response(
                {"amount": ["Must be a positive number"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            owed_material.delivered += amount
            if owed_material.delivered >= owed_material.amount:
                # Delete sanction if any
                sanction = Sanction.objects.filter(owed_material=owed_material).first()
                if sanction is not None:
                    sanction.delete()
                    transaction_logger.info(
                        "%s deleted sanction for student %s material fully returned owmatid %s",
                        request.user.email,
                        owed_material.student.id,
                        owed_material.pk,
                    )
                # Reset the owed material to display no owed material
                owed_material.delivered -= owed_material.amount
                owed_material.amount = 0
                if owed_material.delivered == 0:
                    owed_material.delete()
                else:
                    owed_material.save()
            else:
                owed_material.save()
        serializer = self.get_serializer(owed_material)

        # Send a message to the websocket to inform about the returned material
        # only if the student is currently playing
        play = owed_material.student.get_active_play()
        if play is not None:
            send_update_message(
                "Plays updated",
                request.user.email,
                info=play.game.pk,
            )

        # Log the transaction
        transaction_logger.info(
            "%s returned material %s - %s for %s",
            request.user.email,
            amount,
            owed_material.material.name,
            owed_material.student.id,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnnouncementListCreateView(generics.ListCreateAPIView):
    """Create and Read Announcements"""

    permission_classes = [AdminWriteAllRead]
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        """Filter announcements based on query parameters"""
        queryset = Announcement.objects.all().order_by("start_at")
        # Show only announcements that have not ended
        only_active = self.request.query_params.get("only-active")
        if only_active:
            queryset = queryset.filter(end_at__gte=timezone.now())
        return queryset

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Send a message to the websocket to inform about the new announcement
        send_update_message(
            "Announcements updated",
            request.user.email,
        )
        # Log creation of announcement
        transaction_logger.info(
            "%s created announcement %s", request.user.email, safe_ascii(response.data["title"])
        )
        return response


class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, Update and Delete Announcement(id)"""

    queryset = Announcement.objects.all()
    permission_classes = [AdminWriteAllRead]
    serializer_class = AnnouncementSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response = super().update(request, *args, **kwargs)
        # Log the transaction
        transaction_logger.info(
            "%s updated announcement %s fields %s",
            request.user.email,
            safe_ascii(response.data["title"]),
            serializer.validated_data.keys(),
        )
        # Send a message to the websocket to inform about the updated announcement
        send_update_message(
            "Announcements updated",
            request.user.email,
        )
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        # Log the transaction
        transaction_logger.info(
            "%s deleted announcement %s %s",
            request.user.email,
            instance.pk,
            safe_ascii(instance.title),
        )
        # Send a message to the websocket to inform about the deleted announcement
        send_update_message(
            "Announcements updated",
            request.user.email,
        )
        return response
