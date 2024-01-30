from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
import logging

transaction_logger = logging.getLogger("transactions")


class HealthCheck(TestCase):
    """Tests for Health Check"""

    def setUp(self) -> None:
        # Initialize client and sample users
        self.client = Client()

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health-check/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"healthy": True})


class LogsTests(TestCase):
    """Tests for Logs"""

    def setUp(self) -> None:
        # Initialize client, sample users and sample logs
        self.client = Client()
        
        for _ in range(10):
            transaction_logger.info(f"example@email.com did some action")

        self.user = get_user_model().objects.create_user(
            email="A01656583@tec.mx",
            password="Mypass123!",
        )

        self.admin_user = get_user_model().objects.create_superuser(
            email="diegoDev@tec.mx",
            password="MyStrongPass123!!!",
        )

        self.inactive_admin_user = get_user_model().objects.create_superuser(
            email="leo@tec.mx", password="MyStrongPass123!!!", is_active=False
        )

    def test_logs_success(self):
        """Test logs endpoint"""
        # Test: View logs as admin
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            "/logs/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)

        # Test: View logs with 'lines' parameter
        response = self.client.get(
            "/logs/?lines=5",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

        """
        Important: In case you ask for more lines than the ones that exist,
        the endpoint will return only the existing ones.

        Example: If you ask for 15 lines but there are only 10, the
        len(response.data) will be 10.
        """

    def test_logs_fail(self):
        """Test logs endpoint"""
        # Test: View logs without authentication
        response = self.client.get("/logs/")
        self.assertEqual(response.status_code, 401)

        # Test: View logs as user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            "/logs/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {"detail": "You do not have permission to perform this action."},
        )

        # Test: View logs as inactive admin
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.get(
            "/logs/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"code": "user_inactive", "detail": "User is inactive"},
        )

        # Test: View logs with invalid 'lines' parameter
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            "/logs/?lines=abc",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"detail": "'lines' parameter must be a valid integer."},
        )

        # Test: View logs with negative 'lines' parameter
        response = self.client.get(
            "/logs/?lines=-1",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"detail": "'lines' parameter must be non-negative."},
        )
