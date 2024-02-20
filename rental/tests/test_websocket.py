from django.test import TestCase, AsyncClient
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async
from ..models import Game
from ..consumers import UpdatesConsumer
import json

"""
from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

class WebSocketTests(ChannelsLiveServerTestCase):
    serve_static = True
    ""
    WebScoket tests: Redis server required!!!
    ""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        try:
            cls.driver = webdriver.Chrome()
        except:
            super().tearDownClass() 
            raise

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def test_consumer(self):
        return None
    """


class WebSocketTests(TestCase):
    def setUp(self) -> None:
        self.client = AsyncClient()

        self.user = get_user_model().objects.create_user(
            email="A01656583@tec.mx",
            password="Mypass123!",
        )

        self.xbox_1 = Game.objects.create(
            name="Xbox 1",
        )

    async def test_consumer(self):
        # Connect and check functionality
        communicator = WebsocketCommunicator(UpdatesConsumer.as_asgi(), "/ws/updates/")
        connected, subprotocol = await communicator.connect()
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
        self.assertEqual(webSocket_response, {"message": "Plays updated", "sender": "diego", "info": 1})

        # TEST: Other updates
        # Successful message from websocket
        await communicator.send_json_to(
            {
                "message": "Games updated",
                "sender": "diego",
            }
        )
        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(webSocket_response, {"message": "Games updated", "sender": "diego"})

        # Disconnect websocket
        await communicator.disconnect()
