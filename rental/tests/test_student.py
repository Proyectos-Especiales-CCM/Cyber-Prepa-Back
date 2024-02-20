from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from ..models import Student, Play, Game, Sanction
from django.utils import timezone
import json


class StudentTests(TestCase):
    """
    TODO: Improve the test cases
    - test_student__get_played_today. Add more plays to the student and check if the function returns the correct value
    - test_student__get_weekly_plays. Add more plays to the student and check if the function returns the correct value
    - test_student__get_sanctions_number. Add more sanctions to the student and check if the function returns the correct value
    """
    def setUp(self):
        # Initialize client and sample data

        self.client = Client()

        self.user = get_user_model().objects.create_user(
            email="A01656583@tec.mx",
            password="Mypass123!",
        )

        self.admin_user = get_user_model().objects.create_superuser(
            email="diegoDev@tec.mx",
            password="MyStrongPass123!!!",
        )

        # Create sample students
        self.student_1 = Student.objects.create(
            id="A01656583",
            name="Diego Jacobo Martinez",
            hash="1234567890",
        )

        self.student_2 = Student.objects.create(
            id="A01656584",
            name="Jhon Doe",
            hash="1234567891",
        )

        self.student_3 = Student.objects.create(
            id="A01656585",
            name="Jane Doe",
            hash="1234567892",
        )

        # Create sample games, plays and sanctions
        game = Game.objects.create(
            name="Game 1",
        )

        Play.objects.create(
            student=self.student_1,
            game=game,
            ended=False,
        )

        play = Play.objects.create(
            student=self.student_3,
            game=game,
            ended=True,
        )

        Sanction.objects.create(
            cause="Romper una regla",
            play=play,
            student=self.student_3,
            end_time=timezone.now() + timezone.timedelta(days=1),
        )

    def test_setUp(self):
        # Test: Check if users were correctly created
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertEqual(Student.objects.count(), 3)
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(Play.objects.count(), 2)
        self.assertEqual(Sanction.objects.count(), 1)

    def test_student__is_playing(self):
        # Test: Check if _is_playing() works correctly
        self.assertTrue(self.student_1._is_playing())
        self.assertFalse(self.student_2._is_playing())
        self.assertFalse(self.student_3._is_playing())

    def test_student__get_played_today(self):
        # Test: Check if _get_played_today() works correctly
        self.assertEqual(self.student_1._get_played_today(), 1)
        self.assertEqual(self.student_2._get_played_today(), 0)
        self.assertEqual(self.student_3._get_played_today(), 1)

    def test_student__get_weekly_plays(self):
        # Test: Check if _get_weekly_plays() works correctly
        self.assertEqual(self.student_1._get_weekly_plays(), 1)
        self.assertEqual(self.student_2._get_weekly_plays(), 0)
        self.assertEqual(self.student_3._get_weekly_plays(), 1)

    def test_student__get_sanctions_number(self):
        # Test: Check if _get_sanctions_number() works correctly
        self.assertEqual(self.student_1._get_sanctions_number(), 0)
        self.assertEqual(self.student_2._get_sanctions_number(), 0)
        self.assertEqual(self.student_3._get_sanctions_number(), 1)

    def test_student_created(self):
        # Test: Check if students were correctly created
        self.assertEqual(Student.objects.count(), 3)

        student = Student.objects.get(id="A01656583")
        self.assertEqual(student.name, "Diego Jacobo Martinez")
        self.assertEqual(student.hash, "1234567890")
        self.assertFalse(student.forgoten_id)

        student = Student.objects.get(id="A01656584")
        self.assertEqual(student.name, "Jhon Doe")
        self.assertEqual(student.hash, "1234567891")
        self.assertFalse(student.forgoten_id)

    def test_students_api_read_list_success(self):
        # Test: List all students via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            "/rental/students/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_students_api_read_list_fail(self):
        # Test: List all students via an unauthenticated user
        response = self.client.get("/rental/students/")
        self.assertEqual(response.status_code, 401)

        # Test: List all students via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            "/rental/students/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 403)

    def test_students_api_create_success(self):
        # Test: Create a student via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/students/",
            {
                "id": "A01656590",
                "name": "Jane Doe",
                "hash": "1234567892",
            },
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response["id"], "A01656590")
        self.assertEqual(response["name"], "Jane Doe")
        self.assertEqual(response["forgoten_id"], False)
        self.assertEqual(Student.objects.count(), 4)

    def test_students_api_create_fail(self):
        # Test: Create a student via an unauthenticated user
        response = self.client.post(
            "/rental/students/",
            json.dumps(
                {
                    "id": "A01656590",
                    "name": "Jane Doe",
                    "hash": "1234567892",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # Test: Create a student via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/students/",
            json.dumps(
                {
                    "id": "A01656590",
                    "name": "Jane Doe",
                    "hash": "1234567892",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Create a student with an invalid id
        invalid_ids = [
            "A0165659",
            "",
            "A0165659A",
        ]

        access_token = AccessToken.for_user(self.admin_user)
        for id in invalid_ids:
            response = self.client.post(
                "/rental/students/",
                json.dumps(
                    {
                        "id": id,
                        "name": "Jane Doe",
                        "hash": "1234567892",
                    }
                ),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Bearer {access_token}",
            )
            self.assertEqual(response.status_code, 400)

        # Confirm that no student was created
        self.assertEqual(Student.objects.count(), 3)

    def test_students_api_read_detail_success(self):
        # Test: Read a student via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            f"/rental/students/{self.student_1.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["id"], "A01656583")
        self.assertEqual(response["name"], "Diego Jacobo Martinez")
        self.assertEqual(response["forgoten_id"], False)

    def test_students_api_read_detail_fail(self):
        # Test: Read a student via an unauthenticated user
        response = self.client.get(f"/rental/students/{self.student_1.pk}/")
        self.assertEqual(response.status_code, 401)

        # Test: Read a student via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            f"/rental/students/{self.student_1.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Read a student that does not exist
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            f"/rental/students/1000/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_students_api_delete_success(self):
        # Test: Delete a student via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            f"/rental/students/{self.student_2.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 204)

        # Confirm that the student was deleted from the database
        self.assertEqual(Student.objects.count(), 2)

    def test_students_api_delete_fail(self):
        # Test: Delete a student via an unauthenticated user
        response = self.client.delete(f"/rental/students/{self.student_2.pk}/")
        self.assertEqual(response.status_code, 401)

        # Test: Delete a student via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.delete(
            f"/rental/students/{self.student_2.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Delete a student that does not exist
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            f"/rental/students/1000/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 404)

        # Test: Delete a student that has plays
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            f"/rental/students/{self.student_1.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Delete a student that has sanctions
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            f"/rental/students/{self.student_3.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Confirm that no student was created
        self.assertEqual(Student.objects.count(), 3)
