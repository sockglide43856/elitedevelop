from pathlib import Path
import os
from dotenv import load_dotenv

from django.conf.global_settings import PASSWORD_HASHERS as DEFAULT_PASSWORD_HASHERS
from machina import MACHINA_MAIN_TEMPLATE_DIR


MACHINA_BASE_TEMPLATE_NAME = 'board_base.html'
PASSWORD_HASHERS = DEFAULT_PASSWORD_HASHERS + [
    'mfa.recovery.Hash', # <--- THIS IS WHAT ENCRYPTS THE RECOVERY CODES
]

PUSH_SUBSCRIPTION_MODEL = "chats.WebPushSubscription"



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# settings.py
EMAIL_FROM = 'EliteDevelop'

DEFAULT_FROM_EMAIL = 'EliteDevelop <elitedevelop.official@gmail.com>'

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")
MFA_ROOT = os.path.join(BASE_DIR, 'static', 'mfa')

PROXY_WORKER_SECRET = os.environ["PROXY_WORKER_SECRET"]

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_MAIL_REDIRECT_URI = os.environ["GOOGLE_MAIL_REDIRECT_URI"]
MAIL_TOKEN_ENCRYPTION_KEY = os.environ["MAIL_TOKEN_ENCRYPTION_KEY"]

EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

FIELD_ENCRYPTION_KEY = os.environ["FIELD_ENCRYPTION_KEY"]

SECRET_KEY = os.environ["SECRET_KEY"]

RECAPTCHA_PUBLIC_KEY = os.environ["RECAPTCHA_PUBLIC_KEY"]
RECAPTCHA_PRIVATE_KEY = os.environ["RECAPTCHA_PRIVATE_KEY"]

AI_WORKER_URL = os.getenv("AI_WORKER_URL")
AI_WORKER_SECRET = os.getenv("AI_WORKER_SECRET")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['elitedevelop.pythonanywhere.com']


# Application definition

INSTALLED_APPS = [
    #'unfold', # or jazzmin, or just comment this line out to use the default django admin.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oauth2_provider',
    'mfa',
    'chat',
    'elitedevelop',
    'qr_generator',
    'proxy',
    'ai',
    'eliteos',
    'gaming',
    'forms',
    'mptt',
    'haystack',
    'widget_tweaks',
    'machina',
    'machina.apps.forum',
    'machina.apps.forum_conversation',
    'machina.apps.forum_conversation.forum_attachments',
    'machina.apps.forum_conversation.forum_polls',
    'machina.apps.forum_feeds',
    'machina.apps.forum_moderation',
    'machina.apps.forum_search',
    'machina.apps.forum_tracking',
    'machina.apps.forum_member',
    'machina.apps.forum_permission',
    'django_recaptcha',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Configure Google Provider Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# MFA
MFA_DOMAIN = "elitedevelop.pythonanywhere.com"
MFA_FORCE_REGISTRATION = False
MFA_UNALLOWED_METHODS = []
MFA_LOGIN_NOT_ALLOWED_METHODS = []
MFA_ALWAYS_REAUTHENTICATE = False
MFA_REAUTHENTICATE_TIME = 3600
MFA_SUCCESS_REGISTRATION_MSG = "Method registered successfully!"
MFA_SUCCESS_LOGIN_MSG = "Logged in successfully using a passkey (MFA)!"
MFA_FAILED_REGISTRATION_MSG = "Registration failed. Please try again."
MFA_FAILED_LOGIN_MSG = "Passkey (MFA) login failed."
U2F_APPID = 'https://elitedevelop.pythonanywhere.com'
FIDO_SERVER_ID = "elitedevelop.pythonanywhere.com"
FIDO_SERVER_NAME = "EliteDevelop"
MFA_SITE_TITLE = "EliteDevelop"
MFA_OWN_DELETE = True
MFA_TRUSTED_DEVICE_COOKIE_NAME = "mfa_trusted_device"
MFA_TRUSTED_DEVICE_AGE = 30
MFA_REDIRECT_AFTER_REGISTRATION = "home"
TOKEN_ISSUER_NAME = "EliteDevelop"
MFA_LOGIN_CALLBACK = 'elitedevelop.views.login_view'
RECOVERY_COUNTERS = 5

UNFOLD = {
    "SITE_TITLE": "EliteDevelop Administration",
    "SITE_HEADER": "EliteDevelop",
    "SITE_URL": "/",
    "DASHBOARD_CALLBACK": "elitedevelop.admin_dashboard.get_dashboard_context",
}
OAUTH2_PROVIDER = {
    'PKCE_REQUIRED': False,
    'ERROR_RESPONSE_WITH_SCOPES': True,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 36000,
    'RESOURCE_SERVER_AUTH_TOKEN_INTROSPECTION_URL': 'https://elitedevelop.pythonanywhere.com/o/introspect/',
}
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'oauth2_provider': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "machina.apps.forum_permission.middleware.ForumPermissionMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "elitedevelop.middleware.RequestLoggerMiddleware",
]

ROOT_URLCONF = "elitedevelop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates'), MACHINA_MAIN_TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "machina.core.context_processors.metadata",
                "elitedevelop.cp.indev",
            ],
        },
    },
]
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'machina_attachments': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/machina_attachments',
    },
}

MACHINA_SETTINGS = {
    'FORUM_NAME': 'EliteDevelop Forum',
    'FORUM_AVATAR_MAX_SIZE': 102400,
    'FORUM_THEME_CSS': 'machina/build/css/machina.board_theme.min.css',
    'FORUM_THEME_VENDOR_CSS': [
        'machina/build/css/machina.board_theme.vendor.min.css',
        'machina/build/css/vendor/easymde.min.css',
    ],
}

MACHINA_FORUM_POLLS_ENABLED = True
MACHINA_FORUM_ATTACHMENTS_ENABLED = True

WSGI_APPLICATION = "elitedevelop.wsgi.application"

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# default static files settings for PythonAnywhere.
# see https://help.pythonanywhere.com/pages/DjangoStaticFiles for more info
MEDIA_ROOT = '/home/elitedevelop/elitedevelop/media'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'