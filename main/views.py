from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import HealthCheckSerializer


class HealthCheck(APIView):
    serializer_class = HealthCheckSerializer
    authentication_classes = []

    @extend_schema(
        description="Health check endpoint",
        responses={200: HealthCheckSerializer},
        tags=["Health Check"],
    )
    def get(self, request):
        return Response({"healthy": True}, status=200)
