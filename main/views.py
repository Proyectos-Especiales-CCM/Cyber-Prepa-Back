from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import HealthCheckSerializer
from main.permissions import IsActive, IsInAdminGroupOrStaff
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
import re


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


class LogsView(APIView):
    """Read logs"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]

    def get(self, request):
        # Get the number of lines from the end of the file from query parameters
        try:
            # Use default value of 10 if 'lines' is not provided or not a valid integer
            N = int(request.query_params.get("lines", 10))
        except ValueError:
            return Response(
                {"detail": "'lines' parameter must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that N is non-negative
        if N < 0:
            return Response(
                {"detail": "'lines' parameter must be non-negative."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Limit the maximum number of lines to prevent potential abuse
        MAX_LINES = 1000  # Set a reasonable maximum limit
        if N > MAX_LINES:
            return Response(
                {
                    "detail": f"'lines' parameter exceeds the maximum limit of {MAX_LINES}."
                },
                status=400,
            )

        # Variable to implement exponential search
        pos = N + 1
        # List to store last N lines
        lines = []

        # Open the file using with() so that it gets closed automatically
        with open(f"{settings.BASE_DIR}/logs/transactions_logs.log", "r") as f:
            # Loop runs until the size of the list becomes equal to N
            while len(lines) <= N:
                # Try block to move the cursor to the pos line from the end of the file
                try:
                    f.seek(-pos, 2)

                # Exception block to handle any runtime error (e.g., IOError)
                except IOError:
                    f.seek(0)
                    break

                # Finally block to add lines to the list after each iteration
                finally:
                    lines = list(f)

                # Increase the value of the variable exponentially
                pos *= 2

        # Return the whole list which stores the last N lines
        lines = lines[-N:]

        # Strip the line into the individual fields {timestamp, user, action} using regex
        response = []
        log_pattern = re.compile(
            r"(?P<level>\w+) (?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (?P<logger>\w+) (?P<user>\S+) (?P<action>.+)$"
        )

        # Parse each line and extract the fields
        for i, line in enumerate(lines):
            match = log_pattern.match(line)
            if match:
                fields = match.groupdict()
                response.append(
                    {
                        "line": i + 1,
                        "timestamp": fields["timestamp"]
                        .replace(" ", "T")
                        .replace(",", ".")
                        + "Z",
                        "user": fields["user"],
                        "action": fields["action"],
                    }
                )

        return Response(response, status=status.HTTP_200_OK)
