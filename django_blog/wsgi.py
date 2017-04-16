"""
WSGI config for django_blog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
# from whitenoise.django import DjangoWhiteNoise
from dj_static import Cling


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_blog.settings")

application = Cling(get_wsgi_application())
# application = DjangoWhiteNoise(application)

