from django.urls import re_path
from . import consumers
from . import notifications_consumer
from . import simple_invitation_consumer

websocket_urlpatterns = [
    re_path(r'ws/battle/$', consumers.BattleConsumer.as_asgi()),
    re_path(r'ws/notifications/$', notifications_consumer.GlobalNotificationsConsumer.as_asgi()),
    re_path(r'ws/invitations/$', simple_invitation_consumer.SimpleInvitationConsumer.as_asgi()),
]