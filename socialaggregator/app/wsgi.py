"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from configurations.wsgi import get_wsgi_application
from raven.middleware import Sentry

application = Sentry(get_wsgi_application())
