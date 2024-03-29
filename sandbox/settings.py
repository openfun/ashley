"""
Django settings for sandbox project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import json
import os
import tempfile

import sentry_sdk
from configurations import Configuration, values
from machina import MACHINA_MAIN_STATIC_DIR, MACHINA_MAIN_TEMPLATE_DIR
from sentry_sdk.integrations.django import DjangoIntegration

from ashley import ASHLEY_MAIN_TEMPLATE_DIR

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join("/", "data")


def get_release():
    """Get the current release of the application.

    By release, we mean the release from the version.json file à la Mozilla [1]
    (if any). If this file has not been found, it defaults to "NA".

    [1]
    https://github.com/mozilla-services/Dockerflow/blob/master/docs/version_object.md
    """
    # Try to get the current release from the version.json file generated by the
    # CI during the Docker image build
    try:
        with open(os.path.join(BASE_DIR, "version.json"), encoding="utf8") as version:
            return json.load(version)["version"]
    except FileNotFoundError:
        return "NA"  # Default: not available


# Disable pylint error "W0232: Class has no __init__ method", because base Configuration
# class does not define an __init__ method.
# pylint: disable = C0209, W0232


class Base(Configuration):
    """
    This is the base configuration every configuration (aka environnement) should inherit from. It
    is recommended to configure third-party applications by creating a configuration mixins in
    ./configurations and compose the Base configuration with those mixins.
    It depends on an environment variable that SHOULD be defined:
    * DJANGO_SECRET_KEY
    You may also want to override default configuration by setting the following environment
    variables:
    * DJANGO_SENTRY_DSN
    * DB_NAME
    * DB_HOST
    * DB_PASSWORD
    * DB_USER
    """

    DEBUG = False

    # Security
    ALLOWED_HOSTS = []
    SECRET_KEY = values.Value(None)

    AUTH_USER_MODEL = "ashley.User"

    # SECURE_PROXY_SSL_HEADER allows to fix the scheme in Django's HttpRequest
    # object when you application is behind a reverse proxy.
    #
    # Keep this SECURE_PROXY_SSL_HEADER configuration only if :
    # - your Django app is behind a proxy.
    # - your proxy strips the X-Forwarded-Proto header from all incoming requests
    # - Your proxy sets the X-Forwarded-Proto header and sends it to Django
    #
    # In other cases, you should comment the following line to avoid security issues.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Disable Samesite flag in session and csrf cookies, because ashley is meant to
    # run in an iframe on external websites.
    # Note : The better solution is to send a flag Samesite=none, because
    # modern browsers are considering Samesite=Lax by default when the flag is
    # not specified.
    CSRF_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SAMESITE = "None"

    # Modern browsers require to have the `secure` attribute on cookies with `Samesite=none`
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    # Privacy
    SECURE_REFERRER_POLICY = "same-origin"

    # Application definition
    ROOT_URLCONF = "urls"
    WSGI_APPLICATION = "wsgi.application"

    # Database
    DATABASES = {
        "default": {
            "ENGINE": values.Value(
                "django.db.backends.postgresql_psycopg2",
                environ_name="DB_ENGINE",
                environ_prefix=None,
            ),
            "NAME": values.Value("ashley", environ_name="DB_NAME", environ_prefix=None),
            "USER": values.Value("fun", environ_name="DB_USER", environ_prefix=None),
            "PASSWORD": values.Value(
                "pass", environ_name="DB_PASSWORD", environ_prefix=None
            ),
            "HOST": values.Value(
                "localhost", environ_name="DB_HOST", environ_prefix=None
            ),
            "PORT": values.Value(5432, environ_name="DB_PORT", environ_prefix=None),
        }
    }

    # Static files (CSS, JavaScript, Images)
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(DATA_DIR, "static")
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(DATA_DIR, "media")
    STATICFILES_DIRS = (MACHINA_MAIN_STATIC_DIR,)

    # AWS
    AWS_ACCESS_KEY_ID = values.SecretValue()
    AWS_LOCATION = values.Value("media/")
    AWS_S3_CUSTOM_DOMAIN = values.Value()
    AWS_S3_REGION_NAME = values.Value()
    AWS_S3_URL_PROTOCOL = values.Value("https")
    AWS_SECRET_ACCESS_KEY = values.SecretValue()
    AWS_STORAGE_BUCKET_NAME = values.Value()
    AWS_QUERYSTRING_AUTH = False
    DEFAULT_FILE_STORAGE = values.Value("storages.backends.s3boto3.S3Boto3Storage")

    # Internationalization
    TIME_ZONE = "UTC"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # Templates
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [ASHLEY_MAIN_TEMPLATE_DIR, MACHINA_MAIN_TEMPLATE_DIR],
            "OPTIONS": {
                "context_processors": [
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "django.template.context_processors.csrf",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.template.context_processors.request",
                    "django.template.context_processors.tz",
                    "ashley.context_processors.site_metas",
                    "machina.core.context_processors.metadata",
                ],
                "loaders": [
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ],
            },
        },
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "dockerflow.django.middleware.DockerflowMiddleware",
        "ashley.machina_extensions.forum_permission.middleware.ForumPermissionMiddleware",
    ]

    AUTHENTICATION_BACKENDS = [
        "ashley.auth.backend.LTIBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]

    # Django applications from the highest priority to the lowest
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Django machina dependencies
        "mptt",
        "haystack",
        "widget_tweaks",
        # Ashley
        "ashley",
        "ashley.machina_extensions.forum",
        "ashley.machina_extensions.forum_conversation",
        "ashley.machina_extensions.forum_moderation",
        "ashley.machina_extensions.forum_permission",
        "ashley.machina_extensions.forum_search",
        # Django LTI Toolbox
        "lti_toolbox",
        # Third party apps
        "dockerflow.django",
        # Django machina
        "machina",
        "machina.apps.forum_conversation.forum_attachments",
        "machina.apps.forum_conversation.forum_polls",
        "machina.apps.forum_feeds",
        "machina.apps.forum_member",
        "machina.apps.forum_tracking",
        "rest_framework",
    ]

    # Languages
    LANGUAGE_CODE = "en-us"

    # Cache
    CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
        "machina_attachments": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": values.Value(
                tempfile.gettempdir(),
                environ_name="TMP_ATTACHMENT_DIR",
                environ_prefix=None,
            ),
        },
    }

    # Search engine
    HAYSTACK_CONNECTIONS = {
        "default": {
            "ENGINE": "haystack.backends.elasticsearch5_backend.Elasticsearch5SearchEngine",
            "URL": "{:s}:{!s}".format(
                values.Value(
                    "elasticsearch",
                    environ_name="ELASTICSEARCH_HOST",
                    environ_prefix=None,
                ),
                values.Value(
                    9200, environ_name="ELASTICSEARCH_PORT", environ_prefix=None
                ),
            ),
            "INDEX_NAME": values.Value(
                "ashley", environ_name="ELASTICSEARCH_INDEX_NAME", environ_prefix=None
            ),
        },
    }

    # Machina
    MACHINA_MARKUP_LANGUAGE = ("ashley.editor.draftjs_renderer", {})
    MACHINA_MARKUP_MAX_LENGTH_VALIDATOR = (
        "ashley.validators.MarkupNullableMaxLengthValidator"
    )
    MACHINA_MARKUP_WIDGET = "ashley.editor.widgets.DraftEditor"
    MACHINA_PROFILE_AVATARS_ENABLED = False
    MACHINA_USER_DISPLAY_NAME_METHOD = "get_public_username_with_default"

    MAX_UPLOAD_FILE_MB = values.PositiveIntegerValue(5)
    IMAGE_TYPE_ALLOWED = values.ListValue(["gif", "jpeg", "jpg", "png", "svg"])

    # Sentry
    SENTRY_DSN = values.Value(None, environ_name="SENTRY_DSN")

    REST_FRAMEWORK = {
        "ALLOWED_VERSIONS": ("1.0",),
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
        ),
        "DEFAULT_VERSION": "1.0",
        "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    }

    @classmethod
    def post_setup(cls):
        """Post setup configuration.
        This is the place where you can configure settings that require other
        settings to be loaded.
        """
        super().post_setup()

        # The SENTRY_DSN setting should be available to activate sentry for an environment
        if cls.SENTRY_DSN is not None:
            sentry_sdk.init(
                dsn=cls.SENTRY_DSN,
                environment=cls.__name__.lower(),
                release=get_release(),
                integrations=[DjangoIntegration()],
            )
            with sentry_sdk.configure_scope() as scope:
                scope.set_extra("application", "backend")


class Development(Base):
    """
    Development environment settings
    We set DEBUG to True and configure the server to respond from all hosts.
    """

    DEBUG = True
    ALLOWED_HOSTS = ["*"]

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(levelname)s] [%(asctime)s] [%(module)s] "
                "%(process)d %(thread)d %(message)s"
            },
            "gelf": {
                "()": "logging_gelf.formatters.GELFFormatter",
                "null_character": True,
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "gelf": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "gelf",
            },
        },
        "loggers": {
            "oauthlib": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
            "ashley": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
            "lti_toolbox": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": True,
            },
            "django": {"handlers": ["console"], "level": "INFO", "propagate": True},
            # This formatter is here as an example to what is possible to do
            # with xapi loggers.
            "xapi": {"handlers": ["gelf"], "level": "INFO", "propagate": True},
        },
    }

    INSTALLED_APPS = Base.INSTALLED_APPS + ["dev_tools"]

    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    CSRF_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SECURE = False

    DEFAULT_FILE_STORAGE = values.Value("django.core.files.storage.FileSystemStorage")


class Test(Base):
    """Test environment settings"""


class ContinuousIntegration(Test):
    """
    Continous Integration environment settings
    nota bene: it should inherit from the Test environment.
    """


class Production(Base):
    """Production environment settings
    You must define the DJANGO_ALLOWED_HOSTS environment variable in Production
    configuration (and derived configurations):
    DJANGO_ALLOWED_HOSTS="foo.com,foo.fr"
    """

    # Session storage engine
    SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

    # Security
    ALLOWED_HOSTS = values.ListValue(None)
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    # System check reference:
    # https://docs.djangoproject.com/en/2.2/ref/checks/#security
    SILENCED_SYSTEM_CHECKS = values.ListValue(
        [
            # Allow to disable django.middleware.clickjacking.XFrameOptionsMiddleware
            # It is necessary since ashley wil be displayed in an iframe on external LMS sites.
            "security.W002",
            # SECURE_SSL_REDIRECT is not defined in the base configuration
            "security.W008",
            # No value is defined for SECURE_HSTS_SECONDS
            "security.W004",
        ]
    )

    # For static files in production, we want to use a backend that includes a hash in
    # the filename, that is calculated from the file content, so that browsers always
    # get the updated version of each file.
    STATICFILES_STORAGE = (
        "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
    )


class Feature(Production):
    """
    Feature environment settings

    nota bene: it should inherit from the Production environment.
    """


class Staging(Production):
    """
    Staging environment settings

    nota bene: it should inherit from the Production environment.
    """


class PreProduction(Production):
    """
    Pre-production environment settings

    nota bene: it should inherit from the Production environment.
    """
