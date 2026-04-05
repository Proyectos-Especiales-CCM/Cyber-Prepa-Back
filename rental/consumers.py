import json
import logging
from collections import Counter

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


logger = logging.getLogger("django")


class OnlineUsersConsumer(WebsocketConsumer):
    group_name = "online_users"

    # Class-level counter shared by all instances in this server process
    user_counts = Counter()

    def connect(self):
        user = self.scope.get("user")

        if user and user.is_authenticated:
            email = user.email

            # 1. Increment tab count for this user
            self.user_counts[email] += 1

            # 2. Join the group and accept connection
            async_to_sync(self.channel_layer.group_add)(
                self.group_name, self.channel_name
            )
            self.accept()

            # 3. Broadcast the updated list to EVERYONE(including the new conn)
            # This handles both the 'initial_list' for the joiner and the
            # 'update' for existing users in one go.
            self.broadcast_user_list()
        else:
            self.close()

    def disconnect(self, code):
        user = self.scope.get("user")
        if user and user.is_authenticated:
            email = user.email

            # 1. Decrement tab count
            if email in self.user_counts:
                self.user_counts[email] -= 1

                # 2. If no more tabs are open, remove user and broadcast
                if self.user_counts[email] <= 0:
                    del self.user_counts[email]

                    # 3. Leave the group first
                    async_to_sync(self.channel_layer.group_discard)(
                        self.group_name, self.channel_name
                    )

                    # 4. Broadcast the new list to remaining users
                    self.broadcast_user_list()
                    return

            # If they still have other tabs open, just leave the group
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name, self.channel_name
            )

    def broadcast_user_list(self):
        """
        Helper method to trigger a group-wide update.
        We send the unique keys (emails) from our Counter.
        """
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "user_list_update",
                "users": list(self.user_counts.keys()),
            },
        )

    def user_list_update(self, event):
        """
        Handler for the 'user_list_update' event.
        Sends the full list of online emails to the React client.
        """
        self.send(text_data=json.dumps({"users": event["users"]}))


class UpdatesConsumer(WebsocketConsumer):
    """
    Websocket consumer for getting the updates of the systems data at the
    index page.
    TODO: Use this consumer to update the admin CRUD with the data updates

    Models interaction is restricted for these consumers.
    Only messages about data updates SHOULD be allowed.

    Example message:
    {
        'message': 'Plays updated',
        'sender': 'a01606010@tec.mx'
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = "updates"

    # CURRENT MESSAGES SUPPORTED:
    # - Plays updated
    #   - A play has been ended, created, deleted, or updated (A student
    #      changed games)
    # - Games updated
    #   - A game has been created, deleted, or updated at the admin CRUD
    # - Students updated
    #   - A student has been deleted, or updated at the admin CRUD

    def connect(self):
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        """Receive message from WebSocket with data update."""
        # Must contain 'message' and 'sender'
        # - sender is the username of the user who sent the message
        # - message is the update message describing the update the user made
        # - info is an optional field that contains the game id of the game
        # that was updated

        # Ignore messages from unauthenticated users — they can
        # still receive updates, but cannot send.
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            return

        try:
            text_data_json = json.loads(text_data)
        except Exception as e:
            logger.warning(
                'Failed to parse JSON message from raw text data: "%s" | Error: %s',
                text_data,
                str(e),
            )
            # If the message is not a valid JSON, ignore it
            return
        message = text_data_json["message"]

        if message == "Plays updated":
            data = {
                "type": "plays_updated",
                "message": message,
                "info": text_data_json["info"],
                "sender": user.email,
            }
        else:
            data = {
                "type": "update_message",
                "message": message,
                "sender": user.email,
            }

        # Send the update message to room group
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, data)

    # Generic update message handler
    def update_message(self, event):
        """Receive message from room group and send to WebSocket."""
        message = event["message"]
        sender = event["sender"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message, "sender": sender}))

    # Plays updated message handler
    # info is the game id of the game that was updated
    def plays_updated(self, event):
        """Receive message from room group and send to WebSocket."""
        message = event["message"]
        sender = event["sender"]
        info = event["info"]

        # Send message to WebSocket
        self.send(
            text_data=json.dumps(
                {"message": message, "info": info, "sender": sender}
            )
        )
