from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer, UserReadSerializer
from main.permissions import IsActive, IsSameUserOrStaff, IsInAdminGroupOrStaff
from .models import User
from drf_spectacular.utils import extend_schema
import logging

transaction_logger = logging.getLogger("transactions")


class UserListCreateView(generics.GenericAPIView):
    """Create and Read Users"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]

    def get_serializer_class(self):
        return UserReadSerializer if self.request.method == "GET" else UserSerializer

    def get_queryset(self):
        return User.objects.all()

    @extend_schema(operation_id="list_users")
    def get(self, request):
        users = self.get_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        transaction_logger.info(
            f"{request.user.email} created user {serializer.data['email']}"
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDetailView(generics.GenericAPIView):
    """Read and Update User(id)"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsSameUserOrStaff]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserReadSerializer
        else:
            return UserSerializer

    def get_object(self):
        obj = generics.get_object_or_404(User, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        transaction_logger.info(
            f"{request.user.email} updated user {serializer.data['email']} fields {serializer.validated_data.keys()}"
        )
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        transaction_logger.info(
            f"{request.user.email} updated user {serializer.data['email']} fields {serializer.validated_data.keys()}"
        )
        return Response(serializer.data)

class UserMeDetails(generics.RetrieveAPIView):
    """ Read User(me) """
    serializer_class = UserReadSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
