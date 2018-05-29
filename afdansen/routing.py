from django.urls import path, re_path
from . import consumers

# channel_routing = [
#     route('websocket.connect', consumers.connectJury, path=r'^jury/socket/(?P<pk>[0-9]+)/$'),
#     route('websocket.connect', consumers.connectLiveStream, path=r'^live/$'),
#     route('websocket.receive', consumers.receiveJury, path=r'^jury/socket/(?P<pk>[0-9]+)/$'),
# ]

websocket_urlpatterns = [
    path('afdansen/jury/socket/<int:pk>/', consumers.JuryConsumer),
    path('afdansen/live/', consumers.LiveStreamConsumer),
]