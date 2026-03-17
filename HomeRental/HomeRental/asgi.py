"""
ASGI config for HomeRental project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
import socketio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeRental.settings')

# Initialize Django ASGI app first to setup Django
django_asgi_app = get_asgi_application()

# Import sio_server AFTER Django setup to avoid AppRegistryNotReady
from chat.sio_server import sio

# Wrap Django app with Socket.IO
application = socketio.ASGIApp(sio, django_asgi_app)
