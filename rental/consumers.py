import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class OnlineUsersConsumer(WebsocketConsumer):
    """ 
    Websocket consumer for getting the online users at the index page.
    """

    def connect(self):
        return super().connect()


class UpdatesConsumer(WebsocketConsumer):
    """ 
    Websocket consumer for getting the updates of the systems data at the
    index page.
    TODO: Update to only messages from authenticated users
    TODO: Use this consumer to update the admin CRUD with the data updates
    
    Models interaction is restricted for these consumers.
    Only messages about data updates SHOULD be allowed.

    Example message:
    {
        'message': 'Plays updated',
        'sender': 'A01606010'
    }
    """

    # CURRENT MESSAGES SUPPORTED:
    # - Plays updated
    #   - A play has been ended, created, deleted, or updated (A student
    #      changed games)
    # - Games updated
    #   - A game has been created, deleted, or updated at the admin CRUD
    # - Students updated
    #   - A student has been deleted, or updated at the admin CRUD

    def connect(self):
        self.room_group_name = 'updates'

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

    def receive(self, text_data):
        """ Receive message from WebSocket with data update. """
        # Must contain 'message' and 'sender'
        # - sender is the username of the user who sent the message
        # - message is the update message describing the update the user made
         # - info is an optional field that contains the game id of the game that was updated
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']

        if message == 'Plays updated':
            data = {
                'type': 'plays_updated',
                'message': message,
                'info': text_data_json['info'],
                'sender': sender
            }
        else:
            data = {
                'type': 'update_message',
                'message': message,
                'sender': sender
            }

        # Send the update message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, data
        )

    # Generic update message handler
    def update_message(self, event):
        """ Receive message from room group and send to WebSocket. """
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    # Plays updated message handler
    # info is the game id of the game that was updated
    def plays_updated(self, event):
        """ Receive message from room group and send to WebSocket. """
        message = event['message']
        sender = event['sender']
        info = event['info']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'info': info,
            'sender': sender
        }))
