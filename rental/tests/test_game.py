import os
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from ..models import Game, Student, Play, Image
from PIL import Image as PILImage
from django.conf import settings
from django.utils import timezone
import pytz
import json


class GameTests(TestCase):
    """
    TODO: Add tests for the following:
    - Add more tests for unconsidered cases
    - Assure behavior when inactive user tries to use the API
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

        # Create sample Image
        image_path = os.path.join(settings.MEDIA_ROOT, "images/", "game_card_image_test.png")
        image2_path = os.path.join(settings.MEDIA_ROOT, "images/", "game_card_image_test_2.png")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        os.makedirs(os.path.dirname(image2_path), exist_ok=True)
        PILImage.new("RGB", (100, 100), color="red").save(image_path)
        PILImage.new("RGB", (100, 100), color="red").save(image2_path)
    
        self.red_image = Image.objects.create(image=image_path)
        self.red_image_2 = Image.objects.create(image=image2_path)

        # Create sample games
        self.xbox_game = Game.objects.create(
            name="Xbox",
            image=self.red_image,
        )

        self.futbolito_1 = Game.objects.create(
            name="Futbolito 1",
            image=self.red_image,
        )

        self.futbolito_2 = Game.objects.create(
            name="Futbolito 2",
        )

        # Create sample plays

        # Old play
        Play.objects.create(
            student=Student.objects.get(id="A01656585"),
            game=Game.objects.get(name="Xbox"),
            ended=True,
        )

        play_1 = Play.objects.create(
            student=Student.objects.get(id="A01656583"),
            game=Game.objects.get(name="Xbox"),
        )

        Play.objects.create(
            student=Student.objects.get(id="A01656584"),
            game=Game.objects.get(name="Xbox"),
        )

        self.xbox_game.start_time = play_1.time
        self.xbox_game.save()

        play_1 = Play.objects.create(
            student=Student.objects.get(id="A01656585"),
            game=Game.objects.get(name="Futbolito 1"),
        )

        self.futbolito_1.start_time = play_1.time
        self.futbolito_1.save()

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

    def test_game_created(self):
        # Test: Check if games were correctly created
        self.assertEqual(Game.objects.count(), 3)

        game = Game.objects.get(name="Xbox")
        self.assertEqual(game.name, "Xbox")
        self.assertTrue(game.show)
        self.assertEqual(game._get_plays().count(), 2)
        self.assertEqual(
            game.start_time, Play.objects.filter(game=game, ended=False)[0].time
        )
        self.assertEqual(game.image, self.red_image)

        game = Game.objects.get(name="Futbolito 1")
        self.assertEqual(game._get_plays().count(), 1)
        self.assertEqual(game.start_time, Play.objects.filter(game=game)[0].time)

        game = Game.objects.get(name="Futbolito 2")
        self.assertEqual(game._get_plays().count(), 0)
        self.assertIsNone(game.start_time)

    def test_game__get_plays(self):
        # Test: Check if _get_plays returns the correct plays
        game = Game.objects.get(name="Xbox")
        self.assertEqual(game._get_plays().count(), 2)

        game = Game.objects.get(name="Futbolito 1")
        self.assertEqual(game._get_plays().count(), 1)

        game = Game.objects.get(name="Futbolito 2")
        self.assertEqual(game._get_plays().count(), 0)

    def test_game__end_all_plays(self):
        # Test: Check if _end_all_plays ends all plays
        game = Game.objects.get(name="Xbox")
        self.assertEqual(game._get_plays().count(), 2)
        game._end_all_plays()
        self.assertEqual(game._get_plays().count(), 0)

        game = Game.objects.get(name="Futbolito 1")
        self.assertEqual(game._get_plays().count(), 1)
        game._end_all_plays()
        self.assertEqual(game._get_plays().count(), 0)

        game = Game.objects.get(name="Futbolito 2")
        self.assertEqual(game._get_plays().count(), 0)
        game._end_all_plays()
        self.assertEqual(game._get_plays().count(), 0)

    def test_games_api_read_list_success(self):
        # Test: List all games via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            "/rental/games/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(len(response.json()[0]["plays"]), 2)

        # Test: List all games via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            "/rental/games/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(len(response.json()[0]["plays"]), 2)

        # Test: List all games via an unauthenticated user
        response = self.client.get("/rental/games/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.json()[0]["plays"], 2)

    def test_games_api_read_list_fail(self):
        # Test: List all games via an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.get(
            "/rental/games/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 401)

    def test_games_api_create_success(self):
        # Test: Create a game via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/games/",
            json.dumps(
                {
                    "name": "Billar 1",
                    "show": False,
                    "image": self.red_image.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response["name"], "Billar 1")
        self.assertFalse(response["show"])
        self.assertEqual(response["image"], self.red_image.pk)
        self.assertEqual(Game.objects.count(), 4)

    def test_games_api_create_fail(self):
        # Test: Create a game via an unauthenticated user
        response = self.client.post(
            "/rental/games/",
            json.dumps(
                {
                    "name": "Billar 1",
                    "show": False,
                    "file_route": "assets/games_cards/billar_1.png",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # Test: Create a game via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/games/",
            json.dumps(
                {
                    "name": "Billar 1",
                    "show": False,
                    "file_route": "assets/games_cards/billar_1.png",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Create a game with an existing name
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/games/",
            json.dumps(
                {
                    "name": "Xbox",
                    "show": False,
                    "file_route": "assets/games_cards/billar_1.png",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Create a game with no name
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            "/rental/games/",
            json.dumps(
                {
                    "show": False,
                    "file_route": "assets/games_cards/billar_1.png",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Create a game via an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.post(
            "/rental/games/",
            json.dumps(
                {
                    "name": "Billar 1",
                    "show": False,
                    "file_route": "assets/games_cards/billar_1.png",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

    def test_games_api_read_detail_success(self):
        # Test: Read a game via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            f"/rental/games/{self.xbox_game.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["name"], "Xbox")
        self.assertTrue(response["show"])
        self.assertEqual(response["image"], self.red_image.image.url)
        self.assertEqual(
            response["start_time"],
            timezone.localtime(Game.objects.get(name="Xbox").start_time)
            .astimezone(pytz.timezone(settings.TIME_ZONE))
            .isoformat(),
        )
        self.assertEqual(len(response["plays"]), 2)

        # Test: Read a game via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            f"/rental/games/{self.xbox_game.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["name"], "Xbox")
        self.assertTrue(response["show"])
        self.assertEqual(response["image"], self.red_image.image.url)
        self.assertEqual(
            response["start_time"],
            timezone.localtime(Game.objects.get(name="Xbox").start_time)
            .astimezone(pytz.timezone(settings.TIME_ZONE))
            .isoformat(),
        )
        self.assertEqual(len(response["plays"]), 2)

        # Test: Read a game via an unauthenticated user
        response = self.client.get(f"/rental/games/{self.xbox_game.pk}/")
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["name"], "Xbox")
        self.assertTrue(response["show"])
        self.assertEqual(response["image"], self.red_image.image.url)
        self.assertEqual(
            response["start_time"],
            timezone.localtime(Game.objects.get(name="Xbox").start_time)
            .astimezone(pytz.timezone(settings.TIME_ZONE))
            .isoformat(),
        )
        self.assertEqual(response["plays"], 2)

    def test_games_api_read_detail_fail(self):
        # Test: Read a game with an invalid id
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            "/rental/games/100/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 404)

        # Test: Read a game via an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.get(
            f"/rental/games/{self.xbox_game.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

    def test_games_api_update_success(self):
        # Test: Update all game fields via an admin user using PUT
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.put(
            f"/rental/games/{self.xbox_game.pk}/",
            json.dumps(
                {
                    "name": "Xbox 360",
                    "show": False,
                    "image": self.red_image_2.pk,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["name"], "Xbox 360")
        self.assertFalse(response["show"])
        self.assertEqual(response["image"], self.red_image_2.pk)

        # Test: Update single game fields via an admin user using PATCH
        response = self.client.patch(
            f"/rental/games/{self.xbox_game.pk}/",
            json.dumps({"show": True}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["show"])

        # Confirm that the game was updated and not created
        self.assertEqual(Game.objects.count(), 3)

    def test_games_api_update_fail(self):
        # Test: Update a game via an unauthenticated user
        response = self.client.put(
            f"/rental/games/{self.xbox_game.pk}/",
            json.dumps(
                {
                    "name": "Xbox 360",
                    "show": False,
                    "file_route": "assets/games_cards/xbox_360.png",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # Test: Update a game via a non-admin user using PUT
        access_token = AccessToken.for_user(self.user)
        response = self.client.patch(
            f"/rental/games/{self.xbox_game.pk}/",
            json.dumps(
                {
                    "name": "Xbox 360",
                    "show": False,
                    "file_route": "assets/games_cards/xbox_360.png",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Update a game via a non-admin user using PATCH
        response = self.client.patch(
            f"/rental/games/{self.xbox_game.pk}/",
            json.dumps(
                {
                    "name": "Xbox 360",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Update a game with an existing name
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.patch(
            f"/rental/games/{self.xbox_game.pk}/",
            json.dumps(
                {
                    "name": "Futbolito 1",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Update a game with no name
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.patch(
            f"/rental/games/{self.xbox_game.pk}/",
            json.dumps(
                {
                    "name": "",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Update a game via an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.patch(
            f"/rental/games/{self.xbox_game.pk}/",
            json.dumps(
                {
                    "name": "Xbox 360",
                    "show": False,
                    "file_route": "assets/games_cards/xbox_360.png",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

    def test_games_api_delete_success(self):
        # Test: Delete a game via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            f"/rental/games/{self.futbolito_2.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Game.objects.count(), 2)

    def test_games_api_delete_fail(self):
        # Test: Delete a game via an unauthenticated user
        response = self.client.delete(f"/rental/games/{self.futbolito_2.pk}/")
        self.assertEqual(response.status_code, 401)

        # Test: Delete a game via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.delete(
            f"/rental/games/{self.futbolito_2.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Delete a game with an invalid id
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            "/rental/games/100/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 404)

        # Test: Delete a game via an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.delete(
            f"/rental/games/{self.futbolito_2.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

        # Test: Delete a game with plays
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            f"/rental/games/{self.xbox_game.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Confirm that the game was not deleted
        self.assertEqual(Game.objects.count(), 3)

    def test_games_api_end_all_plays_success(self):
        # Test: End all plays of a game via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.post(
            f"/rental/games/{self.xbox_game.pk}/end-all-plays/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["name"], "Xbox")
        self.assertTrue(response["show"])
        self.assertEqual(response["image"], self.red_image.pk)
        self.assertEqual(
            response["start_time"],
            timezone.localtime(Game.objects.get(name="Xbox").start_time)
            .astimezone(pytz.timezone(settings.TIME_ZONE))
            .isoformat(),
        )
        self.assertEqual(len(response["plays"]), 0)
        game = Game.objects.get(pk=self.xbox_game.pk)
        self.assertEqual(game._get_plays().count(), 0)

        # Test: End all plays of a game via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            f"/rental/games/{self.futbolito_1.pk}/end-all-plays/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["name"], "Futbolito 1")
        self.assertTrue(response["show"])
        self.assertEqual(response["image"], self.red_image.pk)
        self.assertEqual(
            response["start_time"],
            timezone.localtime(Game.objects.get(pk=self.futbolito_1.pk).start_time)
            .astimezone(pytz.timezone(settings.TIME_ZONE))
            .isoformat(),
        )
        self.assertEqual(len(response["plays"]), 0)
        game = Game.objects.get(pk=self.xbox_game.pk)
        self.assertEqual(game._get_plays().count(), 0)

    def test_games_api_end_all_plays_fail(self):
        # Test: End all plays of a game via an unauthenticated user
        response = self.client.post(
            f"/rental/games/{self.xbox_game.pk}/end-all-plays/",
        )
        self.assertEqual(response.status_code, 401)

        # Test: End all plays of a game via an inactive user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.post(
            f"/rental/games/{self.xbox_game.pk}/end-all-plays/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

    def test_games_api_read_null_image(self):
        # Test: Read a game with no image
        game = Game.objects.get(name="Futbolito 2")
        self.assertIsNone(game.image)
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            f"/rental/games/{game.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIsNone(response["image"])