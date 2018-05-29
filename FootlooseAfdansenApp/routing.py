from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter

import afdansen.routing

application = ProtocolTypeRouter({
    'websocket' : AuthMiddlewareStack(
        URLRouter(
            afdansen.routing.websocket_urlpatterns
        )
    )
})