from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from .serializers import (
    StudentSerializer,
    PlaySerializer,
    GameSerializer,
    SanctionSerializer,
)
from .models import Student, Play, Game, Sanction
from main.permissions import IsActive, IsInAdminGroupOrStaff, AdminWriteUserRead
from rest_framework_simplejwt.authentication import JWTAuthentication


class StudentListCreateView(generics.ListCreateAPIView):
    """Create and Read Students"""

    queryset = Student.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]
    serializer_class = StudentSerializer


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, Update and Delete Student(id)"""

    queryset = Student.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]
    serializer_class = StudentSerializer


class GameListCreateView(generics.ListCreateAPIView):
    """Create and Read Games"""

    queryset = Game.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, AdminWriteUserRead]
    serializer_class = GameSerializer

class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, Update and Delete Game(id)"""

    queryset = Game.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, AdminWriteUserRead]
    serializer_class = GameSerializer

class GameEndAllPlaysView(generics.GenericAPIView):
    """End all plays of a game"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive]

    def post(self, request, pk):
        game = generics.get_object_or_404(Game, pk=pk)
        game._end_all_plays()
        return Response(GameSerializer(game).data, status=status.HTTP_200_OK)
