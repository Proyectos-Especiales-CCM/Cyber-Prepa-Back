import json
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from ..models import Game, Student, Play, Sanction


class PlayTests(TestCase):
    """
    INFO:
    - For successfully creating a play, there are multiple cases to consider:
        - CASE 1: The game does not have any active plays, therefore the game.start_time
            should be set to the play.time of the first play to be created
        - CASE 2: The game has active plays, and the game.start_time hasn't overpassed
            more than 50 minutes, therefore the game time has not expired yet
            and more players can join the game (create plays).

    - An unsuccessful play creation should be considered when:
        RULES:
        - CASE 1: The student is already playing
        - CASE 2: The student has already played today
        - CASE 3: The student has already played 3 times this week      ------------------------- MISSING
        - CASE 4: The student has sanctions
        - CASE 5: The game has expired (50 minutes or more)
        LOGIC:
        - CASE 6: The game does not exist
        - CASE 7: The student id doesn't match the regex [a|l]{8}
        - CASE 8: The play is being created by an unauthenticated user
        - CASE 9: The play is being created by an inactive user

    - For successfully updating a play, there are multiple cases to consider:
        - CASE 1: The play game field is being updated to a game with no active plays
        - CASE 2: The play game field is being updated to a game with active
            plays and time under 50 minutes
        - CASE 3: The play hasn't ended yet, and the play time hasn't passed 50 minutes

    - An unsuccessful play update should be considered when:
        RULES:
        - CASE 1: The play game field is being updated to a game with active
            plays and time over 50 minutes
        - CASE 2: The play game field is being updated from a game with time
            over 50 minutes
        - CASE 3: The play time has passed 50 minutes
        LOGIC:
        - CASE 4: The play is being updated through PUT method

    TODO: Add tests for the following:
    - Fix and document the setUp method
        - Games
        - Students
        - Plays
    - Add more tests for unconsidered cases
    - Assure behavior when inactive user tries to use the API
    - Add assertion for the correct detail message when a play is not created at cases 1-3
    - Add tests for the update cases
    """

    def create_sample_students(self) -> None:
        """
        Create sample students\n
        Do not create the student A01656590 as it's used to create plays with a student
        that doesn't exist
        """
        Student.objects.create(
            id="a01656583",
            name="Diego Jacobo Martinez",
            hash="1234567890",
        )

        Student.objects.create(
            id="a01656584",
            name="Jhon Doe",
            hash="1234567891",
        )

        Student.objects.create(
            id="a01656585",
            name="Jane Doe",
            hash="1234567892",
        )

        Student.objects.create(
            id="a01656586",
            name="Juan Perez",
            hash="1234567893",
        )

        Student.objects.create(
            id="a01656587",
            name="Maria Perez",
            hash="1234567894",
        )

        Student.objects.create(
            id="a01656588",
            name="Pedro Perez",
            hash="1234567895",
        )

        Student.objects.create(
            id="a01656589",
            name="Luis Perez",
            hash="1234567896",
        )

        # Do not create the student A01656590 as it's used to create plays

    def create_sample_games(self) -> None:
        """Create sample games"""
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

    def create_sample_plays(self) -> None:
        """Create sample plays"""
        self.ten_minutes_ago = timezone.now() - timedelta(minutes=10)
        self.five_minutes_ago = timezone.now() - timedelta(minutes=5)
        play = Play.objects.create(
            student=Student.objects.get(id="a01656585"),
            game=Game.objects.get(name="Xbox 1"),
            ended=True,
        )
        play.time = self.ten_minutes_ago
        play.save()

        play_1 = Play.objects.create(
            student=Student.objects.get(id="a01656583"),
            game=Game.objects.get(name="Xbox 1"),
        )
        play_1.time = self.ten_minutes_ago
        play_1.save()

        play = Play.objects.create(
            student=Student.objects.get(id="a01656584"),
            game=Game.objects.get(name="Xbox 1"),
        )
        play.time = self.ten_minutes_ago
        play.save()

        self.xbox_1.start_time = play_1.time
        self.xbox_1.save()

        play_1 = Play.objects.create(
            student=Student.objects.get(id="a01656587"),
            game=Game.objects.get(name="Xbox 2"),
        )
        play_1.time = self.five_minutes_ago
        play_1.save()

        self.xbox_2.start_time = play_1.time
        self.xbox_2.save()

        self.one_hour_ago = timezone.now() - timedelta(hours=1)
        play_1 = Play.objects.create(
            student=Student.objects.get(id="a01656585"),
            game=Game.objects.get(name="Futbolito 1"),
        )
        play_1.time = self.one_hour_ago
        play_1.save()

        self.futbolito_1.start_time = play_1.time
        self.futbolito_1.save()

        play_1 = Play.objects.create(
            student=Student.objects.get(id="a01656586"),
            game=Game.objects.get(name="Futbolito 2"),
        )
        play_1.time = self.one_hour_ago
        play_1.save()

        self.futbolito_2.start_time = play_1.time
        self.futbolito_2.save()

        Play.objects.create(
            student=Student.objects.get(id="a01656585"),
            game=Game.objects.get(name="Billar 1"),
            ended=True,
        )

        play_1 = Play.objects.create(
            student=Student.objects.get(id="a01656589"),
            game=Game.objects.get(name="Xbox 1"),
            ended=True,
        )
        play_1.time = self.one_hour_ago
        play_1.save()

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

        self.create_sample_students()
        self.create_sample_games()
        self.create_sample_plays()

        # Create sample sanctions

        Sanction.objects.create(
            student=Student.objects.get(id="a01656588"),
            cause="No regresar el juego",
            end_time=timezone.now() + timedelta(days=1),
        )

        self.users_count = get_user_model().objects.count()
        self.games_count = Game.objects.count()
        self.students_count = Student.objects.count()
        self.plays_count = Play.objects.count()

    def test_setUp(self):
        # Test: Check if users were correctly created
        self.assertEqual(get_user_model().objects.count(), self.users_count)
        self.assertEqual(Game.objects.count(), self.games_count)
        self.assertEqual(Student.objects.count(), self.students_count)
        self.assertEqual(Play.objects.count(), self.plays_count)

        # Check if xboxs is correctly configure to test plays in a game with
        # - Simulated usage: Ended plays, 2 active plays where players are still on time
        game = Game.objects.get(pk=self.xbox_1.pk)
        self.assertEqual(game.get_plays().count(), 2)
        self.assertEqual(
            timezone.localtime(game.start_time),
            timezone.localtime(self.ten_minutes_ago),
        )

        game = Game.objects.get(pk=self.xbox_2.pk)
        self.assertEqual(game.get_plays().count(), 1)
        self.assertEqual(
            timezone.localtime(game.start_time),
            timezone.localtime(self.five_minutes_ago),
        )

        # Check if futbolitos is correctly configure to test plays in a game with
        # - Simulated usage: Ended plays, 1 active plays where players time is expired
        game = Game.objects.get(pk=self.futbolito_1.pk)
        self.assertEqual(game.get_plays().count(), 1)
        self.assertEqual(
            timezone.localtime(game.start_time), timezone.localtime(self.one_hour_ago)
        )

        game = Game.objects.get(pk=self.futbolito_2.pk)
        self.assertEqual(game.get_plays().count(), 1)
        self.assertEqual(
            timezone.localtime(game.start_time), timezone.localtime(self.one_hour_ago)
        )

        # Check if billars is correctly configure to test plays in a game with
        # - Simulated newly created game:
        game = Game.objects.get(pk=self.billar_1.pk)
        self.assertEqual(game.get_plays().count(), 0)
        self.assertIsNone(game.start_time)

        game = Game.objects.get(pk=self.billar_2.pk)
        self.assertEqual(game.get_plays().count(), 0)
        self.assertIsNone(game.start_time)

    def test_play_created(self):
        # Test: Check if the plays were correctly created
        self.assertEqual(Play.objects.count(), self.plays_count)

        play_1 = Play.objects.get(pk=1)
        self.assertEqual(play_1.student.id, "a01656585")
        self.assertEqual(play_1.game.pk, self.xbox_1.pk)
        self.assertTrue(play_1.ended)
        self.assertIsNotNone(play_1.time)

        play_2 = Play.objects.get(pk=2)
        self.assertEqual(play_2.student.id, "a01656583")
        self.assertEqual(play_2.game.pk, self.xbox_1.pk)
        self.assertFalse(play_2.ended)
        self.assertIsNotNone(play_2.time)

        play_3 = Play.objects.get(pk=3)
        self.assertEqual(play_3.student.id, "a01656584")
        self.assertEqual(play_3.game.pk, self.xbox_1.pk)
        self.assertFalse(play_3.ended)
        self.assertIsNotNone(play_3.time)

        play_4 = Play.objects.get(pk=4)
        self.assertEqual(play_4.student.id, "a01656587")
        self.assertEqual(play_4.game.pk, self.xbox_2.pk)
        self.assertFalse(play_4.ended)
        self.assertIsNotNone(play_4.time)

        play_5 = Play.objects.get(pk=5)
        self.assertEqual(play_5.student.id, "a01656585")
        self.assertEqual(play_5.game.pk, self.futbolito_1.pk)
        self.assertFalse(play_5.ended)
        self.assertIsNotNone(play_5.time)

        play_6 = Play.objects.get(pk=6)
        self.assertEqual(play_6.student.id, "a01656586")
        self.assertEqual(play_6.game.pk, self.futbolito_2.pk)
        self.assertFalse(play_6.ended)
        self.assertIsNotNone(play_6.time)

        play_7 = Play.objects.get(pk=7)
        self.assertEqual(play_7.student.id, "a01656585")
        self.assertEqual(play_7.game.pk, self.billar_1.pk)
        self.assertTrue(play_7.ended)
        self.assertIsNotNone(play_7.time)

    def test_plays_api_read_list_success(self):
        # Test: List all plays via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            "/rental/plays/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), self.plays_count)

        # Test: List all plays via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            "/rental/plays/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), self.plays_count)

    def test_plays_api_read_list_fail(self):
        # Test: List all plays via an unauthenticated user
        response = self.client.get("/rental/plays/")
        self.assertEqual(response.status_code, 401)

        # Test: List all plays via an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.get(
            "/rental/plays/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 401)

    def test_plays_api_create_success_case_1(self):
        """
        CASE 1: The game does not have any active plays, therefore the game.start_time
        should be set to the play.time of the first play to be created
        """
        # Test: Create a play via an admin user
        # and check all play and game data are correct
        previous_game_start_time = Game.objects.get(pk=self.billar_1.pk).start_time
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01606060",
                    "game": self.billar_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response["student"], "a01606060")
        self.assertEqual(response["game"], self.billar_1.pk)
        self.assertFalse(response["ended"])
        self.assertIsNotNone(response["time"])

        # Test: Check if the play were correctly created and the game.start_time
        # was set to the play.time of the first play to be created
        play = Play.objects.get(pk=response["id"])
        game = Game.objects.get(pk=self.billar_1.pk)
        self.assertEqual(game.get_plays().count(), 1)
        self.assertNotEqual(game.start_time, previous_game_start_time)
        self.assertAlmostEqual(
            timezone.localtime(game.start_time),
            timezone.localtime(play.time),
            delta=timezone.timedelta(seconds=1),
        )

        # Test: Create a play via a non-admin user
        # and check all play and game data are correct
        previous_game_start_time = Game.objects.get(pk=self.billar_2.pk).start_time
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01606061",
                    "game": self.billar_2.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response["student"], "a01606061")
        self.assertEqual(response["game"], self.billar_2.pk)
        self.assertFalse(response["ended"])
        self.assertIsNotNone(response["time"])

        # Test: Check if the play were correctly created and the game.start_time
        # was set to the play.time of the first play to be created
        play = Play.objects.get(pk=response["id"])
        game = Game.objects.get(pk=self.billar_2.pk)
        self.assertEqual(game.get_plays().count(), 1)
        self.assertNotEqual(game.start_time, previous_game_start_time)
        self.assertAlmostEqual(
            timezone.localtime(game.start_time),
            timezone.localtime(play.time),
            delta=timezone.timedelta(seconds=1),
        )

        # Check if the plays were correctly created
        self.assertEqual(Play.objects.count(), self.plays_count + 2)

    def test_plays_api_create_success_case_2(self):
        """
        CASE 2: The game has active plays, and the game.start_time hasn't overpassed
        more than 50 minutes, therefore the game time has not expired yet
        and more players can join the game (create plays).
        """
        # Test: Create a play via an admin user
        # and check all play and game data are correct
        previous_game_start_time = Game.objects.get(pk=self.xbox_1.pk).start_time
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01606062",
                    "game": self.xbox_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response["student"], "a01606062")
        self.assertEqual(response["game"], self.xbox_1.pk)
        self.assertFalse(response["ended"])
        self.assertIsNotNone(response["time"])

        # Test: Check if the play were correctly created and the game.start_time
        # was set to the play.time of the first play to be created
        play = Play.objects.get(pk=response["id"])
        game = Game.objects.get(pk=self.xbox_1.pk)
        self.assertEqual(game.get_plays().count(), 3)
        self.assertNotEqual(game.start_time, play.time)
        self.assertEqual(game.start_time, previous_game_start_time)

        # Test: Create a play via a non-admin user
        # and check all play and game data are correct
        previous_game_start_time = Game.objects.get(pk=self.xbox_2.pk).start_time
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01606063",
                    "game": self.xbox_2.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response["student"], "a01606063")
        self.assertEqual(response["game"], self.xbox_2.pk)
        self.assertFalse(response["ended"])
        self.assertIsNotNone(response["time"])

        # Test: Check if the play were correctly created and the game.start_time
        # was set to the play.time of the first play
        play = Play.objects.get(pk=response["id"])
        game = Game.objects.get(pk=self.xbox_2.pk)
        self.assertEqual(game.get_plays().count(), 2)
        self.assertNotEqual(game.start_time, play.time)
        self.assertEqual(game.start_time, previous_game_start_time)

        # Check if the plays were correctly created
        self.assertEqual(Play.objects.count(), self.plays_count + 2)

    def test_plays_api_create_fail_case_1(self):
        """
        CASE 1: The student is already playing
        - Example: Student A01656583 is already playing in the Xbox 1
        """

        # Test: Create a play via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01656583",
                    "game": self.xbox_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Student is already playing")

    def test_plays_api_create_fail_case_2(self):
        """
        CASE 2: The student has already played today
        - Example: Student a01656589 has already played today in the Xbox 1
        """
        # Test: Create a play via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01656589",
                    "game": self.xbox_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Student has already played today")

    def test_plays_api_create_fail_case_3(self):
        """
        CASE 3: The student has already played 3 times this week
        """
        # Delete after completing the test
        pass

    def test_plays_api_create_fail_case_4(self):
        """
        CASE 4: The student has sanctions
        """
        # Test: Create a play via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01656588",
                    "game": self.xbox_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Student has sanctions")

    def test_plays_api_create_fail_case_5(self):
        """
        CASE 5: The game has expired (50 minutes or more)
        """
        # Test: Create a play via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01656590",
                    "game": self.futbolito_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Game time has expired")

    def test_plays_api_create_fail_case_6(self):
        """
        CASE 6: The game does not exist
        """
        # Test: Create a play via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01656590",
                    "game": 100,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Game does not exist")

    def test_plays_api_create_fail_case_7(self):
        """
        CASE 7: The student id doesn't match the regex [a|l]{8}
        """
        # Test: Create a play via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a0165658O",
                    "game": self.xbox_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "Invalid student id",
        )

    def test_plays_api_create_fail_case_8(self):
        """
        CASE 8: The play is being created by an unauthenticated user
        """
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01656590",
                    "game": self.xbox_1.pk,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_plays_api_create_fail_case_9(self):
        """
        CASE 9: The play is being created by an inactive user
        """
        # Test: Create a play via an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.post(
            "/rental/plays/",
            json.dumps(
                {
                    "student": "a01656590",
                    "game": self.xbox_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

    def test_plays_api_read_detail_success(self):
        # Test: Read a play via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            "/rental/plays/1/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["student"], "a01656585")
        self.assertEqual(response["game"], self.xbox_1.pk)
        self.assertTrue(response["ended"])
        self.assertIsNotNone(response["time"])

        # Test: Read a play via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            "/rental/plays/1/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["student"], "a01656585")
        self.assertEqual(response["game"], self.xbox_1.pk)
        self.assertTrue(response["ended"])
        self.assertIsNotNone(response["time"])

    def test_plays_api_read_detail_fail(self):
        # Test: Read a play via an unauthenticated user
        response = self.client.get("/rental/plays/1/")
        self.assertEqual(response.status_code, 401)

        # Test: Read a play via an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.get(
            "/rental/plays/1/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 401)

    def test_plays_api_update_success(self):
        # Test: Update a play game field via an admin user using PATCH
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.patch(
            "/rental/plays/2/",
            json.dumps(
                {
                    "game": self.xbox_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["student"], "a01656583")
        self.assertEqual(response["game"], self.xbox_1.pk)
        self.assertFalse(response["ended"])
        self.assertIsNotNone(response["time"])

        # Test: Update a play ended field via a non-admin user using PATCH
        access_token = AccessToken.for_user(self.user)
        response = self.client.patch(
            "/rental/plays/2/",
            json.dumps(
                {
                    "ended": True,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["student"], "a01656583")
        self.assertEqual(response["game"], self.xbox_1.pk)
        self.assertTrue(response["ended"])
        self.assertIsNotNone(response["time"])

        # Confirm that no new plays were created
        self.assertEqual(Play.objects.count(), self.plays_count)

    def test_plays_api_update_success_case_1(self):
        """
        CASE 1: The play game field is being updated to a game with no active plays
        """
        # Test: Update a play game field via an admin user using PATCH
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.patch(
            "/rental/plays/2/",
            json.dumps(
                {
                    "game": self.billar_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["student"], "a01656583")
        self.assertEqual(response["game"], self.billar_1.pk)
        self.assertFalse(response["ended"])
        self.assertIsNotNone(response["time"])

        # Confirm that the game.start_time was set to the play.time
        prev_game = Game.objects.get(pk=self.xbox_1.pk)
        new_game = Game.objects.get(pk=self.billar_1.pk)
        self.assertEqual(prev_game.start_time, new_game.start_time)

        # Confirm that no new plays were created
        self.assertEqual(Play.objects.count(), self.plays_count)

    def test_plays_api_update_success_case_2(self):
        """
        CASE 2: The play game field is being updated to a game with active
        plays and time under 50 minutes
        """
        # Test: Update a play game field via an admin user using PATCH
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.patch(
            "/rental/plays/2/",
            json.dumps(
                {
                    "game": self.xbox_2.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["student"], "a01656583")
        self.assertEqual(response["game"], self.xbox_2.pk)
        self.assertFalse(response["ended"])
        self.assertIsNotNone(response["time"])

        # Confirm that the game.start_time was set to the play.time
        prev_game = Game.objects.get(pk=self.xbox_1.pk)
        new_game = Game.objects.get(pk=self.xbox_2.pk)
        self.assertNotEqual(prev_game.start_time, new_game.start_time)

        # Confirm that no new plays were created
        self.assertEqual(Play.objects.count(), self.plays_count)

    def test_plays_api_update_success_case_3(self):
        """
        CASE 3: The play hasn't ended yet, and the play time hasn't passed 50 minutes
        """
        # Test: Update a play game field via an admin user using PATCH
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.patch(
            "/rental/plays/2/",
            json.dumps(
                {
                    "game": self.xbox_2.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["student"], "a01656583")
        self.assertEqual(response["game"], self.xbox_2.pk)
        self.assertFalse(response["ended"])
        self.assertIsNotNone(response["time"])

        # Confirm that no new plays were created
        self.assertEqual(Play.objects.count(), self.plays_count)

    def test_plays_api_update_fail(self):
        # Test: Update a play via an unauthenticated user
        response = self.client.put(
            "/rental/plays/1/",
            json.dumps(
                {
                    "student": "A01656583",
                    "game": self.xbox_2.pk,
                    "ended": False,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # Test: Update a play via an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.patch(
            "/rental/plays/2/",
            json.dumps(
                {
                    "ended": True,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

        # Confirm that no new plays were created
        self.assertEqual(Play.objects.count(), self.plays_count)

    def test_plays_api_update_fail_case_1(self):
        """
        CASE 1: The play game field is being updated to a game with active
        plays and time over 50 minutes
        """
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.patch(
            "/rental/plays/2/",
            json.dumps(
                {
                    "game": self.futbolito_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Game time has expired")

    def test_plays_api_update_fail_case_2(self):
        """
        CASE 2: The play game field is being updated from a game with time
        over 50 minutes
        """
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.patch(
            "/rental/plays/5/",
            json.dumps(
                {
                    "game": self.xbox_1.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Game time has expired")

    def test_plays_api_update_fail_case_3(self):
        """
        CASE 3: The play time has passed 50 minutes
        """
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.patch(
            "/rental/plays/8/",
            json.dumps(
                {
                    "game": self.xbox_2.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Play time has expired")
        #self.skipTest("Not implemented")

    def test_plays_api_update_fail_case_4(self):
        """
        CASE 4: The play is being updated through PUT method
        """
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.put(
            "/rental/plays/1/",
            json.dumps(
                {
                    "student": "a01656583",
                    "game": self.xbox_2.pk,
                    "ended": False,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["detail"], 'Method "PUT" not allowed.')
        self.assertEqual(Play.objects.count(), self.plays_count)

    def test_plays_api_delete_success(self):
        # Test: Delete a play via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            "/rental/plays/1/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 204)

        # Test: Delete a play via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.delete(
            "/rental/plays/2/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 204)

        # Confirm the play was deleted
        self.assertEqual(Play.objects.count(), self.plays_count - 2)

    def test_plays_api_delete_fail(self):
        # Test: Delete a play via an unauthenticated user
        response = self.client.delete("/rental/plays/1/")
        self.assertEqual(response.status_code, 401)

        # Test: Delete a play via an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.delete(
            "/rental/plays/1/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

        # Confirm the play was not deleted
        self.assertEqual(Play.objects.count(), self.plays_count)
