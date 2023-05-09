# chat/consumers.py
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Chat, Room, UserPreferences, User


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id: str = ''
        self.room_group_name = ''

    async def connect(self):
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.room_group_name = 'chat_%s' % self.channel_id

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json['type']
            room_id = text_data_json['room_id']

            if message_type == "chat_message":
                message = text_data_json['message']
                user_id = text_data_json['user_id']

                @database_sync_to_async
                def async_save_chat():
                    room: Room = Room.objects.filter(id=room_id).first()
                    user: User = User.objects.filter(id=user_id).first()
                    if not room:
                        raise RuntimeError('Room Missing')
                    return Chat.objects.create(room=room, message=message, user=user)

                chat = await async_save_chat()
                # await Chat.objects.acreate(message=message)

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'room_id': room_id,
                        'chat_id': chat.id,
                        'created': chat.created.isoformat(),
                        'user_id': user_id
                    }
                )
            elif message_type == "delete_message":
                chat = text_data_json['chat_id']

                @database_sync_to_async
                def async_delete_chat():
                    Chat.objects.filter(id=chat).delete()

                await async_delete_chat()

                # Send message to room group
                msg = {
                    'type': 'delete_message',
                    'chat_id': chat,
                    'room_id': room_id
                }
                await self.channel_layer.group_send(self.room_group_name, msg)
            elif message_type == "update_preferences":
                user_id = text_data_json['user_id']
                #breakpoint()
                @database_sync_to_async
                def async_update_preferences():
                    up: UserPreferences = UserPreferences.objects.get(id=user_id)
                    up.last_accessed_room_id = room_id
                    up.save()

                await async_update_preferences()
            elif message_type == "edit_message":
                chat_id = text_data_json['chat_id']
                message = text_data_json['message']

                @database_sync_to_async
                def async_update_chat():
                    up = Chat.objects.get(id=chat_id)
                    up.message = message
                    up.save()

                await async_update_chat()

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'edit_message',
                        'message': message,
                        'room_id': room_id,
                        'chat_id': chat_id
                    }
                )

        except Exception as ex:
            # handle error
            # Send message to room group
            breakpoint()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f"ERROR: {ex}",
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message_type = event['type']
        message = event['message']
        room_id = event['room_id']
        chat_id = event['chat_id']
        user_id = event['user_id']
        created = event['created']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'room_id': room_id,
            'chat_id': chat_id,
            'user_id': user_id,
            'created': created,
            'message': message,
            'type': message_type
        }))

    async def delete_message(self, event):
        chat_id = event['chat_id']
        room_id = event['room_id']
        await self.send(text_data=json.dumps({
            'chat_id': chat_id,
            "room_id": room_id,
            'type': 'delete_message'
        }))

    async def edit_message(self, event):
        chat_id = event['chat_id']
        room_id = event['room_id']
        message = event['message']
        await self.send(text_data=json.dumps({
            'chat_id': chat_id,
            "room_id": room_id,
            'message': message,
            'type': 'edit_message'
        }))