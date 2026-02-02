"""Base settings for the Property-Hub project."""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from django.contrib import messages
from django.templatetags.static import static
from environs import Env

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize Env with Django support
env = Env()
env.read_env()

# Load environment-specific file
if Path(BASE_DIR / ".env.dev").exists():
    env.read_env(BASE_DIR / ".env.dev", override=True)
elif Path(BASE_DIR / ".env.prod").exists():
    env.read_env(BASE_DIR / ".env.prod", override=True)

DEBUG = env.bool("DEBUG")
print("DEBUG", DEBUG)

SECRET_KEY = env.str("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://propertyhub.loca.lt",
    "http://propertyhub.duckdns.org",
]

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",
    "storages",
    # Custom Apps
    "apps.properties.apps.PropertiesConfig",
    "apps.shared.apps.SharedConfig",
    "apps.users.apps.UsersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Add WhiteNoise only in production
if not DEBUG:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

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

# Database configuration
DATABASES = {"default": dj_database_url.parse(env.str("DATABASE_URL"))}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "users:login"

AXES_ENABLED = True
AXES_FAILURE_LIMIT = 10
AXES_COOLOFF_TIME = timedelta(seconds=10)
AXES_LOCK_OUT_AT_FAILURE = True
AXES_RESET_ON_SUCCESS = True
AXES_DISABLE_ACCESS_LOG = False
AXES_LOCKOUT_TEMPLATE = None
AXES_LOCKOUT_URL = None
AXES_VERBOSE = True
AXES_USERNAME_FORM_FIELD = "email"  # Use email field for axes tracking

# AWS S3 Configuration (LocalStack for both dev and prod)
AWS_HOST_NAME = env("AWS_HOST_NAME", "localhost")
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = f"http://{AWS_HOST_NAME}:4566"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_HOST_NAME}:4566/{AWS_STORAGE_BUCKET_NAME}"
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = False
AWS_QUERYSTRING_AUTH = DEBUG

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Custom User Model
AUTH_USER_MODEL = "users.User"

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar", "django_extensions"]
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
    INTERNAL_IPS = ["127.0.0.1"]

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
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
        "apps.properties": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

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
