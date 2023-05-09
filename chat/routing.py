# chat/routing.py
from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<channel_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
    # path('ws/chat/<str:channel_id>/$', consumers.ChatConsumer.as_asgi()),
]