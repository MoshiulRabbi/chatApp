# chat/consumers.py
import json
from location.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_user(self, user_name):
        # Get the user object using the user id
        un = User.objects.get(username=user_name)
        return un.id





    async def connect(self):
        # Get the user id from the scope
        user_id = self.scope['user'].id

        # Get the other user id from the URL route
        other_user_id = self.scope['url_route']['kwargs']['other_user_id']



        uuid = await self.get_user(other_user_id)




        # Save the user id and other user id for later use
        self.user_id = user_id
        self.other_user_id = other_user_id
        self.uuid = uuid



        # Create a group for the chat
        if user_id > uuid:
            self.chat_group_name = f'{user_id}-{uuid}'
        else:
            self.chat_group_name = f'{uuid}-{user_id}'

        self.chat_group_name = 'chat_%s' % self.chat_group_name

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )




        # # Create a group for the chat, to do 
        # self.chat_group_name = 'chat_%s_%s' % (self.user_id, self.other_user_id)

        # self.chat_group_name = "chat_%s" % self.other_user_id

        # Join room group
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)

        print(self.chat_group_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        #now id
        username = text_data_json['username']

        # Send message to room group
        await self.channel_layer.group_send(
            self.chat_group_name, {"type": "chat_message", "message": message, 'username': username,}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, 'username': username}))