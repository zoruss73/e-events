from django.urls import re_path, path
from .consumers import ChatConsumer, NotificationConsumer

websocket_urlpatterns = [
     path('ws/messages/<int:room_id>/', ChatConsumer.as_asgi()),
]