from django.test import TestCase, AsyncClient
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import AccessToken
from ..models import Game
from ..consumers import UpdatesConsumer


class WebSocketTests(TestCase):
    """
    Test the websocket consumer for the updates of the systems data

    INFO:
    - Cases to be tested:
        - Case 1 => Consumer (Websocket) expected behavior
        - Case 2 => Websocket trigger on: new PLAY on GAME with 0 plays
        - Case 3 => Websocket trigger on: new PLAY on GAME with more than 0 plays
        - Case 4 => Websocket trigger on: update PLAY
        - Case 5 => Websocket trigger on: delete PLAY
        - Case 6 => Websocket trigger on: end-all-plays of a GAME

        - Case 7 => Websocket trigger on: new GAME
        - Case 8 => Websocket trigger on: update GAME
        - Case 9 => Websocket trigger on: delete GAME

    """
    def setUp(self) -> None:
        self.client = AsyncClient()

        self.user = get_user_model().objects.create_user(
            email="A01656583@tec.mx",
            password="Mypass123!",
        )

        self.admin = get_user_model().objects.create_superuser(
            email="admin@tec.mx",
            password="Mypass123!",
        )

        self.xbox_1 = Game.objects.create(
            name="Xbox 1",
        )

    async def test_consumer(self):
        # Connect and check functionality
        communicator = WebsocketCommunicator(UpdatesConsumer.as_asgi(), "/ws/updates/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        ### Test: Check functionality ###
        # TEST: Plays Update case
        # Successful message from websocket
        await communicator.send_json_to(
            {
                "message": "Plays updated",
                "sender": "diego",
                "info": 1,
            }
        )
        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {"message": "Plays updated", "sender": "diego", "info": 1},
        )

        # TEST: Other updates
        # Successful message from websocket
        await communicator.send_json_to(
            {
                "message": "Games updated",
                "sender": "diego",
            }
        )
        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response, {"message": "Games updated", "sender": "diego"}
        )

        # Disconnect websocket
        await communicator.disconnect()

    async def test_consumer_interaction_with_views_plays(self):
        # Connect and check functionality
        communicator = WebsocketCommunicator(UpdatesConsumer.as_asgi(), "/ws/updates/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # TEST: Plays Create: Case 2
        access_token = AccessToken.for_user(self.user)
        response = await self.client.post(
            "/rental/plays/",
            {
                "game": self.xbox_1.pk,
                "student": "A01656583",
            },
            content_type="application/json",
            Authorization=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)

        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {"message": "Plays updated", "sender": self.user.email, "info": self.xbox_1.pk},
        )

        # TEST: Plays Create: Case 3
        response = await self.client.post(
            "/rental/plays/",
            {
                "game": self.xbox_1.pk,
                "student": "A01656584",
            },
            content_type="application/json",
            Authorization=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)

        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {"message": "Plays updated", "sender": self.user.email, "info": self.xbox_1.pk},
        )

        play_id = response.data["id"]

        # TEST: Plays Update: Case 4
        response = await self.client.patch(
            f"/rental/plays/{play_id}/",
            {
                "ended": True
            },
            content_type="application/json",
            Authorization=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)

        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {"message": "Plays updated", "sender": self.user.email, "info": self.xbox_1.pk},
        )

        # TEST: Plays Delete: Case 5
        response = await self.client.delete(
            f"/rental/plays/{play_id}/",
            content_type="application/json",
            Authorization=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 204)

        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {"message": "Plays updated", "sender": self.user.email, "info": self.xbox_1.pk},
        )

        # TEST: Plays End All: Case 6
        response = await self.client.post(
            f"/rental/games/{self.xbox_1.pk}/end-all-plays/",
            content_type="application/json",
            Authorization=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)

        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {"message": "Plays updated", "sender": self.user.email, "info": self.xbox_1.pk},
        )

        # Disconnect websocket
        await communicator.disconnect()

    async def test_consumer_interaction_with_views_games(self):
        # Connect and check functionality
        communicator = WebsocketCommunicator(UpdatesConsumer.as_asgi(), "/ws/updates/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # TEST: Games Create: Case 7
        access_token = AccessToken.for_user(self.admin)
        response = await self.client.post(
            "/rental/games/",
            {
                "name": "Xbox 2",
            },
            content_type="application/json",
            Authorization=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)

        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {"message": "Games updated", "sender": self.admin.email},
        )

        # TEST: Games Update: Case 8
        response = await self.client.patch(
            f"/rental/games/{self.xbox_1.pk}/",
            {
                "name": "Xbox 3",
            },
            content_type="application/json",
            Authorization=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)

        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {"message": "Games updated", "sender": self.admin.email},
        )

        # TEST: Games Delete: Case 9
        response = await self.client.delete(
            f"/rental/games/{self.xbox_1.pk}/",
            content_type="application/json",
            Authorization=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 204)

        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {"message": "Games updated", "sender": self.admin.email},
        )

        # Disconnect websocket
        await communicator.disconnect()
