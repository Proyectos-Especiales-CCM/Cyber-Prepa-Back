import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


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

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        """ Receive message from WebSocket with data update. """
        # Must contain 'message' and 'sender'
        # - sender is the username of the user who sent the message
        # - message is the update message describing the update the user made
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']

        # Send the update message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                'type': 'update_message',
                'message': message,
                'sender': sender
            }
        )

    def update_message(self, event):
        """ Receive message from room group and send to WebSocket. """
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
