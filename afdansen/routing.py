from channels.routing import route
from afdansen import consumers

channel_routing = [
    route('websocket.connect', consumers.connectJury, path=r'^jury/socket/(?P<pk>[0-9]+)/$'),
    route('websocket.connect', consumers.connectLiveStream, path=r'^live/$'),
    route('websocket.receive', consumers.receiveJury, path=r'^jury/socket/(?P<pk>[0-9]+)/$'),
]