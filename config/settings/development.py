"""
Development settings for Property-Hub project.
"""

from .base import *  # noqa: F403, F401
from .base import (  # noqa: F401
    AWS_HOST_NAME,
    AWS_MEDIA_BUCKET_NAME,
    AWS_STATIC_BUCKET_NAME,
    LOGGING,
    MIDDLEWARE,
    STORAGES,
    USE_S3_MEDIA,
    USE_S3_STATIC,
    env,
    timedelta,
)

# ============================================================================
# DEBUG & DEVELOPMENT
# ============================================================================

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])  # noqa: F405

# CSRF trusted origins for development
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://propertyhub.loca.lt",
]

# ============================================================================
# DEVELOPMENT TOOLS
# ============================================================================

INSTALLED_APPS += [  # noqa: F405
    "debug_toolbar",
    "django_extensions",
]

MIDDLEWARE.insert(  # noqa: F405
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,  # noqa: F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# ============================================================================
# SECURITY (Relaxed for development)
# ============================================================================

# Disable HTTPS requirements in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ============================================================================
# AWS S3 (LocalStack for development)
# ============================================================================

# Override S3 settings for LocalStack
if USE_S3_MEDIA or USE_S3_STATIC:  # noqa: F405
    AWS_HOST_NAME = env.str("AWS_HOST_NAME", "localhost")  # noqa: F405
    AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", f"http://{AWS_HOST_NAME}:4566")  # noqa: F405
    AWS_S3_VERIFY = False

    # Update custom domains for LocalStack
    if USE_S3_MEDIA:  # noqa: F405
        AWS_S3_CUSTOM_DOMAIN = f"{AWS_HOST_NAME}:4566/{AWS_MEDIA_BUCKET_NAME}"  # noqa: F405
        STORAGES["default"]["OPTIONS"]["custom_domain"] = AWS_S3_CUSTOM_DOMAIN  # noqa: F405
        STORAGES["default"]["OPTIONS"]["endpoint_url"] = AWS_S3_ENDPOINT_URL  # noqa: F405
        MEDIA_URL = f"http://{AWS_S3_CUSTOM_DOMAIN}/"  # noqa: F405

    if USE_S3_STATIC:  # noqa: F405
        AWS_S3_STATIC_CUSTOM_DOMAIN = f"{AWS_HOST_NAME}:4566/{AWS_STATIC_BUCKET_NAME}"  # noqa: F405
        STORAGES["staticfiles"]["OPTIONS"]["custom_domain"] = (
            AWS_S3_STATIC_CUSTOM_DOMAIN  # noqa: F405
        )
        STORAGES["staticfiles"]["OPTIONS"]["endpoint_url"] = AWS_S3_ENDPOINT_URL  # noqa: F405
        STATIC_URL = f"http://{AWS_S3_STATIC_CUSTOM_DOMAIN}/"  # noqa: F405

# ============================================================================
# AXES (Relaxed for development)
# ============================================================================

AXES_FAILURE_LIMIT = 10
AXES_COOLOFF_TIME = timedelta(seconds=10)  # noqa: F405

# ============================================================================
# LOGGING (More verbose in development)
# ============================================================================

LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["django.db.backends"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "INFO",  # Set to DEBUG to see SQL queries
    "propagate": False,
}

# ============================================================================
# EMAIL (Console backend for development)
# ============================================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
