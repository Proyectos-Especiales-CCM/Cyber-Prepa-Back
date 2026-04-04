"""
Test cases for the websocket functionality.
Tests:
 - UpdatesConsumer
    - Test: Check all update types (Games updates, Plays updates)
    - Test: Check unauthenticated user cannot send updates
    - Test: Check unauthenticated user can receive updates
    - Test: Check malformed JSON is ignored
 - OnlineUsersConsumer
    - Test: Check authenticated user can see connected users
    - Test: Check unauthenticated user cannot see connected users
    - Test: Check multiple connections from the same user
    - Test: Check last tab disconnect broadcasts to others
 - Test: Check consumers do not leak messages

Unused test case that fails due to Django current liminations.
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

from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import AsyncClient, TestCase

from ..consumers import OnlineUsersConsumer, UpdatesConsumer
from ..models import Game


class WebSocketTests(TestCase):
    def setUp(self) -> None:
        self.client = AsyncClient()
        # Clear the user_counts dictionary to ensure a clean state for each test
        OnlineUsersConsumer.user_counts.clear()

        self.user_a = get_user_model().objects.create_user(
            email="A01656583@tec.mx",
            password="Mypass123!",
        )

        self.user_b = get_user_model().objects.create_user(
            email="B01656583@tec.mx",
            password="Mypass123!",
        )

        self.xbox_1 = Game.objects.create(
            name="Xbox 1",
        )

    async def test_consumer_different_updates(self):
        """
        Tests that the UpdatesConsumer can receive and send the different types
        of updates.
        """
        # Connect and check functionality
        communicator = WebsocketCommunicator(
            UpdatesConsumer.as_asgi(),
            "/ws/updates/",
        )
        # Set the authenticated user in the scope
        communicator.scope["user"] = self.user_a
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        ### Test: Check functionality ###
        # TEST: Plays Update case
        # Successful message from websocket
        await communicator.send_json_to(
            {
                "message": "Plays updated",
                "info": 1,
            }
        )
        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {
                "message": "Plays updated",
                "sender": self.user_a.email,
                "info": 1,
            },
        )

        # TEST: Other updates
        # Successful message from websocket
        await communicator.send_json_to(
            {
                "message": "Games updated",
                "sender": self.user_a.email,
            }
        )
        webSocket_response = await communicator.receive_json_from()
        self.assertEqual(
            webSocket_response,
            {"message": "Games updated", "sender": self.user_a.email},
        )

        # Disconnect websocket
        await communicator.disconnect()

    async def test_unauthenticated_user_receives_updates(self):
        """
        Test that an unauthenticated user can receive updates from the websocket
        """
        # 1. Listener (Anonymous)
        listener = WebsocketCommunicator(
            UpdatesConsumer.as_asgi(), "/ws/updates/"
        )
        # We don't set a user in scope, so it's Anonymous
        connected_l, _ = await listener.connect()
        self.assertTrue(connected_l)

        # 2. Sender (Authenticated)
        sender = WebsocketCommunicator(
            UpdatesConsumer.as_asgi(), "/ws/updates/"
        )
        sender.scope["user"] = self.user_a
        connected_s, _ = await sender.connect()
        self.assertTrue(connected_s)

        # 3. Action: Authenticated user sends update
        await sender.send_json_to(
            {
                "message": "Plays updated",
                "info": self.xbox_1.id,
            }
        )

        # 4. Assert: Anonymous listener receives it
        response = await listener.receive_json_from()
        self.assertEqual(response["message"], "Plays updated")
        self.assertEqual(response["sender"], self.user_a.email)

        await listener.disconnect()
        await sender.disconnect()

    async def test_unauthenticated_user_cannot_send_updates(self):
        """
        Test that an unauthenticated user cannot send updates to the websocket
        """
        # 1. Listener (Anonymous)
        listener = WebsocketCommunicator(
            UpdatesConsumer.as_asgi(), "/ws/updates/"
        )
        connected_l, _ = await listener.connect()
        self.assertTrue(connected_l)

        # 2. Sender (Anonymous)
        sender = WebsocketCommunicator(
            UpdatesConsumer.as_asgi(), "/ws/updates/"
        )
        connected_s, _ = await sender.connect()
        self.assertTrue(connected_s)

        # 3. Action: Anonymous user sends update
        await sender.send_json_to(
            {
                "message": "Plays updated",
                "info": self.xbox_1.id,
            }
        )

        # 4. Assert: Anonymous listener doesn't receives it
        no_messages = await listener.receive_nothing()
        self.assertTrue(
            no_messages, "The listener received a message it shouldn't have!"
        )

        await listener.disconnect()
        await sender.disconnect()

    async def test_online_users_blocks_anonymous(self):
        communicator = WebsocketCommunicator(
            OnlineUsersConsumer.as_asgi(), "/ws/users/"
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_online_users_authenticated_can_see_connected_users(self):
        """
        Validates the functionality of the consumer, that allows for recentrly
        joined users to see current connected users. And all connected users to
        receive the updated list of connected users when a new user joins.
        """
        conn1 = WebsocketCommunicator(
            OnlineUsersConsumer.as_asgi(), "/ws/users/"
        )
        conn1.scope["user"] = self.user_a
        await conn1.connect()

        # User 1 receives the list [User A]
        resp1 = await conn1.receive_json_from()
        self.assertEqual(resp1["event"], "user_list_update")
        self.assertIn(self.user_a.email, resp1["users"])

        # 2. Second user joins
        conn2 = WebsocketCommunicator(
            OnlineUsersConsumer.as_asgi(), "/ws/users/"
        )
        conn2.scope["user"] = self.user_b
        await conn2.connect()

        # 3. BOTH should receive the updated list [User A, User B]
        resp_for_b = await conn2.receive_json_from()
        resp_for_a = await conn1.receive_json_from()

        self.assertEqual(len(resp_for_b["users"]), 2)
        self.assertIn(self.user_a.email, resp_for_b["users"])
        self.assertIn(self.user_b.email, resp_for_b["users"])
        self.assertEqual(resp_for_b["users"], resp_for_a["users"])

        await conn1.disconnect()
        await conn2.disconnect()

    async def test_multiple_connections_same_user(self):
        """
        Validates that when a user joins multiple times and leaves once, the
        consumer doesn't remove the user from the list of connected users.
        """
        # 1. User opens Tab 1
        tab1 = WebsocketCommunicator(
            OnlineUsersConsumer.as_asgi(), "/ws/users/"
        )
        tab1.scope["user"] = self.user_a
        await tab1.connect()
        await tab1.receive_json_from()  # Consume initial list

        # 2. User opens Tab 2
        tab2 = WebsocketCommunicator(
            OnlineUsersConsumer.as_asgi(), "/ws/users/"
        )
        tab2.scope["user"] = self.user_a
        await tab2.connect()
        await tab1.receive_json_from()  # Tab 1 sees update
        await tab2.receive_json_from()  # Tab 2 sees update

        # 3. User closes Tab 2
        await tab2.disconnect()

        # 4. Assert: Tab 1 should NOT have received a "left" update
        # because the user is still online on Tab 1.
        # We use receive_nothing to verify no broadcast happened.
        no_update = await tab1.receive_nothing()
        self.assertTrue(no_update)

        # Verify user is still in the class-level counter
        self.assertEqual(OnlineUsersConsumer.user_counts[self.user_a.email], 1)

        # 5. User closes Tab 1 (Last tab)
        await tab1.disconnect()

        # Verify user is gone from counter
        self.assertEqual(OnlineUsersConsumer.user_counts[self.user_a.email], 0)
        self.assertNotIn(self.user_a.email, OnlineUsersConsumer.user_counts)

    async def test_last_tab_disconnect_broadcasts_to_others(self):
        """
        Verify that when User A closes their only tab, User B receives
        an updated list that doesn't include User A.
        """
        # 1. User A joins
        conn_a = WebsocketCommunicator(
            OnlineUsersConsumer.as_asgi(), "/ws/users/"
        )
        conn_a.scope["user"] = self.user_a
        await conn_a.connect()
        await conn_a.receive_json_from()  # Initial list [A]

        # 2. User B joins
        conn_b = WebsocketCommunicator(
            OnlineUsersConsumer.as_asgi(), "/ws/users/"
        )
        conn_b.scope["user"] = self.user_b
        await conn_b.connect()
        await conn_a.receive_json_from()  # A sees [A, B]
        await conn_b.receive_json_from()  # B sees [A, B]

        # 3. User A disconnects
        await conn_a.disconnect()

        # 4. User B should receive an update list [User B only]
        resp = await conn_b.receive_json_from()
        self.assertEqual(resp["event"], "user_list_update")
        self.assertNotIn(self.user_a.email, resp["users"])
        self.assertIn(self.user_b.email, resp["users"])

        await conn_b.disconnect()

    async def test_updates_consumer_ignores_malformed_json(self):
        """
        Tests that sending invalid JSON doesn't crash the consumer.
        """
        communicator = WebsocketCommunicator(
            UpdatesConsumer.as_asgi(), "/ws/updates/"
        )
        communicator.scope["user"] = self.user_a
        await communicator.connect()

        # Send raw text instead of JSON
        await communicator.send_to(text_data="Hello World")

        # If the consumer didn't crash, it should still be able to disconnect
        await communicator.disconnect()

    async def test_consumers_do_not_leak_messages(self):
        """
        Ensures updates sent to /ws/updates/ are not received by /ws/users/.
        """
        update_conn = WebsocketCommunicator(
            UpdatesConsumer.as_asgi(), "/ws/updates/"
        )
        update_conn.scope["user"] = self.user_a
        await update_conn.connect()

        user_conn = WebsocketCommunicator(
            OnlineUsersConsumer.as_asgi(), "/ws/users/"
        )
        user_conn.scope["user"] = self.user_b
        await user_conn.connect()
        await user_conn.receive_json_from()  # Eat initial list

        # Send update
        await update_conn.send_json_to({"message": "Plays updated", "info": 1})

        # user_conn should receive nothing
        self.assertTrue(await user_conn.receive_nothing())

        await update_conn.disconnect()
        await user_conn.disconnect()
