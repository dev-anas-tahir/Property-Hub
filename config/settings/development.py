"""Development settings for the Property-Hub project."""

from config.settings.base import *

DEBUG = True

INTERNAL_IPS = [
    "127.0.0.1",
]

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
