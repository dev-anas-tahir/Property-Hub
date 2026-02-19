"""
Base settings for Property-Hub project.
Contains settings common to all environments.
"""

from datetime import timedelta
from pathlib import Path

from django.contrib import messages
from django.templatetags.static import static
from environs import Env
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = Env()
# Read .env file from project root
env.read_env(str(BASE_DIR / ".env"), recurse=False)
# Also try environment-specific files if they exist
if (BASE_DIR / ".env.dev").exists():
    env.read_env(str(BASE_DIR / ".env.dev"), recurse=False)
elif (BASE_DIR / ".env.prod").exists():
    env.read_env(str(BASE_DIR / ".env.prod"), recurse=False)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", [])

# ============================================================================
# CORE DJANGO SETTINGS
# ============================================================================

INSTALLED_APPS = [
    # Channels must be before Django apps for proper ASGI support
    "daphne",
    # Third-party admin theme
    "unfold",
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "channels",
    "axes",
    "storages",
    # Local apps
    "apps.chat.apps.ChatConfig",
    "apps.properties.apps.PropertiesConfig",
    "apps.shared.apps.SharedConfig",
    "apps.users.apps.UsersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ============================================================================
# DATABASE
# ============================================================================

DATABASES = {
    "default": dj_database_url.parse(
        env.str("DATABASE_URL"),
        conn_max_age=env.int("DATABASE_CONN_MAX_AGE", 600),
    )
}

# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "users:login"

# Django Axes - Brute force protection
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 10
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCK_OUT_AT_FAILURE = True
AXES_RESET_ON_SUCCESS = True
AXES_DISABLE_ACCESS_LOG = False
AXES_LOCKOUT_TEMPLATE = None
AXES_LOCKOUT_URL = None
AXES_VERBOSE = True
AXES_USERNAME_FORM_FIELD = "email"

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ============================================================================

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ============================================================================
# MEDIA FILES (User uploads)
# ============================================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ============================================================================
# DJANGO CHANNELS & REDIS
# ============================================================================

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (
                    env.str("REDIS_HOST", "127.0.0.1"),
                    env.int("REDIS_PORT", 6379),
                )
            ],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# ============================================================================
# AWS S3 STORAGE CONFIGURATION
# ============================================================================

USE_S3_MEDIA = env.bool("USE_S3_MEDIA", False)
USE_S3_STATIC = env.bool("USE_S3_STATIC", False)

# AWS credentials and configuration
AWS_HOST_NAME = env.str("AWS_HOST_NAME", "")
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", "")
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", None)
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "public-read"
AWS_S3_VERIFY = env.bool("AWS_S3_VERIFY", True)
AWS_QUERYSTRING_AUTH = False

# S3 bucket names
AWS_MEDIA_BUCKET_NAME = env.str("AWS_MEDIA_BUCKET_NAME", "propertyhub-media")
AWS_STATIC_BUCKET_NAME = env.str("AWS_STATIC_BUCKET_NAME", "propertyhub-static")

# Storage backends configuration
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# Configure S3 for media files if enabled
if USE_S3_MEDIA:
    AWS_S3_CUSTOM_DOMAIN = env.str(
        "AWS_S3_CUSTOM_DOMAIN",
        f"{AWS_MEDIA_BUCKET_NAME}.s3.amazonaws.com",
    )
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": AWS_MEDIA_BUCKET_NAME,
            "custom_domain": AWS_S3_CUSTOM_DOMAIN,
            "file_overwrite": AWS_S3_FILE_OVERWRITE,
            "default_acl": AWS_DEFAULT_ACL,
            "querystring_auth": AWS_QUERYSTRING_AUTH,
        },
    }
    if AWS_S3_ENDPOINT_URL:
        STORAGES["default"]["OPTIONS"]["endpoint_url"] = AWS_S3_ENDPOINT_URL
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

# Configure S3 for static files if enabled (typically production only)
if USE_S3_STATIC:
    AWS_S3_STATIC_CUSTOM_DOMAIN = env.str(
        "AWS_S3_STATIC_CUSTOM_DOMAIN",
        f"{AWS_STATIC_BUCKET_NAME}.s3.amazonaws.com",
    )
    STORAGES["staticfiles"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STATIC_BUCKET_NAME,
            "custom_domain": AWS_S3_STATIC_CUSTOM_DOMAIN,
            "file_overwrite": True,
            "default_acl": AWS_DEFAULT_ACL,
            "querystring_auth": False,
        },
    }
    if AWS_S3_ENDPOINT_URL:
        STORAGES["staticfiles"]["OPTIONS"]["endpoint_url"] = AWS_S3_ENDPOINT_URL
    STATIC_URL = f"https://{AWS_S3_STATIC_CUSTOM_DOMAIN}/"

# ============================================================================
# MESSAGES FRAMEWORK
# ============================================================================

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# ============================================================================
# LOGGING
# ============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ============================================================================
# THIRD-PARTY: UNFOLD ADMIN
# ============================================================================

UNFOLD = {
    "SITE_TITLE": "PropertyHub Admin",
    "SITE_HEADER": "PropertyHub",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("images/favicon.svg"),
        },
    ],
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 244 255",
            "200": "216 207 255",
            "300": "192 190 255",
            "400": "165 155 255",
            "500": "139 122 255",
            "600": "120 84 255",
            "700": "102 58 255",
            "800": "85 36 255",
            "900": "70 13 255",
        },
    },
}

# ============================================================================
# MISCELLANEOUS
# ============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
