from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from ..models import Game, Student, Play, Sanction
from django.utils import timezone
from datetime import timedelta
import json


class SanctionTests(TestCase):
    """
    INFO:
    - For successfully creating a sanction, there are multiple cases to consider:
        - CASE 1: The student must have a valid ID
        - CASE 2: The sanction must include a proper reason
        - CASE 3: The student must not be currently sanctioned.

    - An unsuccessful sanction creation should be considered when:
        RULES:
        - CASE 1: The student's ID is in an invalid format
        - CASE 2:
        LOGIC:
        - CASE 1: The student is already in the sanctioned db

    - For successfully updating a sanction, there are multiple cases to consider:
        - CASE 1: The student must have a valid ID, and must already have an active sanction

    - An unsuccessful sanction update should be considered when:
        LOGIC:
        - CASE 1: The student is not already sanctioned


    Tests
    """

    def setUp(self) -> None:
        # Initialize client and sample data
        """
        The created objects are:
        3 Users: 1 admin, 1 inactive admin, 1 non-admin
        X Students
        6 Games:
            2 with active plays and time under 50 minutes
            2 with active plays and expired time (50 minutes or more)
            2 with no active plays
        X Sanctions
        """

        self.client = Client()

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

        # Create sample students
        Student.objects.create(
            id="A01656583",
            name="Diego Jacobo Martinez",
            hash="1234567890",
        )

        Student.objects.create(
            id="A01656584",
            name="Jhon Doe",
            hash="1234567891",
        )

        Student.objects.create(
            id="A01656585",
            name="Jane Doe",
            hash="1234567892",
        )

        Student.objects.create(
            id="A01656586",
            name="Juan Perez",
            hash="1234567893",
        )

        Student.objects.create(
            id="A01656587",
            name="Maria Perez",
            hash="1234567894",
        )

        Student.objects.create(
            id="A01656588",
            name="Pedro Perez",
            hash="1234567895",
        )

        # Do not create the student A01656590 as it's used to create plays

        # Create sample games
        # Games with active plays and time under 50 minutes
        self.xbox_1 = Game.objects.create(
            name="Xbox 1",
        )

        self.xbox_2 = Game.objects.create(
            name="Xbox 2",
        )

        # Games with active plays and expired time (50 minutes or more)
        self.futbolito_1 = Game.objects.create(
            name="Futbolito 1",
        )

        self.futbolito_2 = Game.objects.create(
            name="Futbolito 2",
        )

        # Games with no active plays
        self.billar_1 = Game.objects.create(
            name="Billar 1",
        )

        self.billar_2 = Game.objects.create(
            name="Billar 2",
        )

        # Create sample plays

        self.ten_minutes_ago = timezone.now() - timedelta(minutes=10)
        play = Play.objects.create(
            student=Student.objects.get(id="A01656585"),
            game=Game.objects.get(name="Xbox 1"),
            ended=True,
        )
        play.time = self.ten_minutes_ago
        play.save()

        play_1 = Play.objects.create(
            student=Student.objects.get(id="A01656583"),
            game=Game.objects.get(name="Xbox 1"),
        )
        play_1.time = self.ten_minutes_ago
        play_1.save()

        play = Play.objects.create(
            student=Student.objects.get(id="A01656584"),
            game=Game.objects.get(name="Xbox 1"),
        )
        play.time = self.ten_minutes_ago
        play.save()

        self.xbox_1.start_time = play_1.time
        self.xbox_1.save()

        play_1 = Play.objects.create(
            student=Student.objects.get(id="A01656587"),
            game=Game.objects.get(name="Xbox 2"),
        )
        play_1.time = self.ten_minutes_ago
        play_1.save()

        self.xbox_2.start_time = play_1.time
        self.xbox_2.save()

        self.one_hour_ago = timezone.now() - timedelta(hours=1)
        play_1 = Play.objects.create(
            student=Student.objects.get(id="A01656585"),
            game=Game.objects.get(name="Futbolito 1"),
        )
        play_1.time = self.one_hour_ago
        play_1.save()

        self.futbolito_1.start_time = play_1.time
        self.futbolito_1.save()

        play_1 = Play.objects.create(
            student=Student.objects.get(id="A01656586"),
            game=Game.objects.get(name="Futbolito 2"),
        )
        play_1.time = self.one_hour_ago
        play_1.save()

        self.futbolito_2.start_time = play_1.time
        self.futbolito_2.save()

        Play.objects.create(
            student=Student.objects.get(id="A01656585"),
            game=Game.objects.get(name="Billar 1"),
            ended=True,
        )

        # Create sample sanctions

        Sanction.objects.create(
            student=Student.objects.get(id="A01656588"),
            cause="No regresar el juego",
            end_time=timezone.now() + timedelta(days=1),
        )

        self.users_count = get_user_model().objects.count()
        self.games_count = Game.objects.count()
        self.students_count = Student.objects.count()
        self.plays_count = Play.objects.count()

    def test_sanctions_api_create_success(self):
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/sanctions/",
            json.dumps(
                {
                    "student": "A01656583",
                    "cause": "No entregó su credencial al jugar",
                    "end_time": "2024-02-15T12:34:56.789Z",
                },
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)

    def test_sanctions_api_create_fail(self):
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.post(
            "/rental/sanctions/",
            json.dumps(
                {
                    "student": "A01666283",
                    "cause": "No regresar el juego",
                    "end_time": "2024-01-15T12:34:56.789Z",
                },
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

    def test_sanctions_api_create_fail_invalid_id(self):
        # Test case for unsuccessfully creating a sanction (invalid student ID)
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/sanctions/",
            json.dumps(
                {
                    "student": "A0165627",
                    "cause": "No entregó su credencial al jugar",
                    "end_time": "2024-02-15T12:34:56.789Z",
                },
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_sanctions_update_fail_no_student(self):
        # Student updating is not already in the db
        access_token = AccessToken.for_user(self.user)

        existing_sanction = Sanction.objects.create(
            student=Student.objects.get(id="A01656583"),
            cause="No entregó su credencial al jugar",
            end_time=timezone.now() + timedelta(days=1),
        )

        response = self.client.patch(
            f"/rental/sanctions/A01656584/",
            json.dumps({"cause": "Nueva causa para la sanción"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_sanctions_update_fail_no_student(self):
        access_token = AccessToken.for_user(self.user)

        existing_sanction = Sanction.objects.create(
            student=Student.objects.get(id="A01656583"),
            cause="No entregó su credencial al jugar",
            end_time=timezone.now() + timedelta(days=1),
        )

        response = self.client.patch(
            f"/rental/sanctions/{existing_sanction.id}/",
            json.dumps({"cause": "Nueva causa para la sanción"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_sanction_success(self):
        # Delete a given sanction
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/sanctions/",
            json.dumps(
                {
                    "student": "A01656583",
                    "cause": "No entregó su credencial al jugar",
                    "end_time": "2024-02-15T12:34:56.789Z",
                },
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            f"/rental/sanctions/A01656583/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_sanction_fail(self):
        # Delete sanction off a student
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/sanctions/",
            json.dumps(
                {
                    "student": "A01656583",
                    "cause": "No entregó su credencial al jugar",
                    "end_time": "2024-02-15T12:34:56.789Z",
                },
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            f"/rental/sanctions/A01656583/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 404)
