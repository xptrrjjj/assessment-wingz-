import os

from django.core.wsgi import get_wsgi_handler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_handler()
