from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from hashtag_monitor.apps.monitor import routing as monitor_routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            monitor_routing.websocket_urlpatterns
        )
    ),
})