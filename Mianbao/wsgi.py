"""
WSGI config for Mianbao project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""
import sys

import os

from django.core.wsgi import get_wsgi_application

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Mianbao.settings")

application = get_wsgi_application()
