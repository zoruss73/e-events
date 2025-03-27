import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import *
from user.models import Notification
from django.contrib.auth.models import User, AnonymousUser
from channels.layers import get_channel_layer
from django.utils.timezone import now
from datetime import timedelta

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id=f"room_{self.scope['url_route']['kwargs']['room_id']}"
        await self.channel_layer.group_add(self.room_id, self.channel_name)
        await self.accept()
        
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_id, self.channel_name)
    
    async def receive(self, text_data):
        text_data_json=json.loads(text_data)
        messsage = text_data_json
        
        print(messsage)
        event = {
            'type':'send_message',
            'message':messsage
        }
        
        if text_data_json.get('message') and text_data_json.get('sender'):
            await self.create_message(data=text_data_json)
        
        await self.channel_layer.group_send(self.room_id, event)
        
    async def send_message(self, event):
        data = event['message']
        await self.create_message(data=data)
        response_data = {
            'sender': data['sender'],
            'message': data['message']
        }
        
        await self.send(text_data=json.dumps({'message':response_data}))
    
    @database_sync_to_async
    def create_message(self, data):
        get_room_by_id = Room.objects.get(id=data['room_id'])
        user_instance = User.objects.get(username=data['sender'])
        
        time_threshold = now() - timedelta(seconds=1)
        last_message = Message.objects.filter(
            room=get_room_by_id, 
            sender=user_instance,
            message=data['message'],  # Only check for duplicate text
            timestamp__gte=time_threshold  # Ensure time difference
        ).exists()
        
        if not last_message:
            new_message = Message(room=get_room_by_id, sender=user_instance, message=data['message'])
            new_message.save()

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
        else:
            self.user = self.scope["user"]
            self.group_name = f"notifications_{self.user.id}"
            
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            # Send unread notifications when the user connects
            await self.send_unread_notifications()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notifications(self, event):
        """
        WebSocket function that sends a notification to the frontend.
        """
        await self.send(text_data=json.dumps({"message": event["message"]}))

    async def send_unread_notifications(self):
        """
        Fetch unread notifications from the database when the user connects.
        """
        notifications = await database_sync_to_async(self.get_unread_notifications)()
        for notification in notifications:
            await self.send(text_data=json.dumps({"message": notification.message}))

    @database_sync_to_async
    def get_unread_notifications(self):
        return Notification.objects.filter(user=self.user, is_read=False)

