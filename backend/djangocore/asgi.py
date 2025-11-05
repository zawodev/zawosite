"""
ASGI config for djangocore project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# Temporarily disable for development - CORS is handled by corsheaders
# from channels.security.websocket import AllowedHostsOriginValidator
from zawomons.routing import websocket_urlpatterns as zawomons_ws
from zawomons_gt.routing import websocket_urlpatterns as zawomons_gt_ws

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocore.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            zawomons_ws + zawomons_gt_ws
        )
    ),
})
