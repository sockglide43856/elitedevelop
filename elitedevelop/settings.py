import os
from pathlib import Path
from dotenv import load_dotenv

from django.conf.global_settings import PASSWORD_HASHERS as DEFAULT_PASSWORD_HASHERS
from machina import MACHINA_MAIN_TEMPLATE_DIR

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR.parent / ".env")

# Core Django Security & Environment Variables
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-env")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = ['elitedevelop.pythonanywhere.com', 'localhost', '127.0.0.1']

# App-Specific Environment Variables
PROXY_WORKER_SECRET = os.getenv("PROXY_WORKER_SECRET", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_MAIL_REDIRECT_URI = os.getenv("GOOGLE_MAIL_REDIRECT_URI", "")
MAIL_TOKEN_ENCRYPTION_KEY = os.getenv("MAIL_TOKEN_ENCRYPTION_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
FIELD_ENCRYPTION_KEY = os.getenv("FIELD_ENCRYPTION_KEY", "")
RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY", "")
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY", "")
AI_WORKER_URL = os.getenv("AI_WORKER_URL", "")
AI_WORKER_SECRET = os.getenv("AI_WORKER_SECRET", "")
COLLABS_API_URL = os.getenv("COLLABS_API_URL", "")
COLLABS_API_KEY = os.getenv("COLLABS_API_KEY", "")

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_FROM = 'EliteDevelop'
DEFAULT_FROM_EMAIL = f"EliteDevelop <{EMAIL_HOST_USER}>" if EMAIL_HOST_USER else 'EliteDevelop <noreply@elitedevelop.com>'

# Password Security & Custom Hashers
PASSWORD_HASHERS = DEFAULT_PASSWORD_HASHERS + [
    'mfa.recovery.Hash',  # Encrypts MFA recovery codes
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Custom Project Settings
MACHINA_BASE_TEMPLATE_NAME = 'board_base.html'
PUSH_SUBSCRIPTION_MODEL = "chats.WebPushSubscription"
AI_DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
MFA_ROOT = os.path.join(BASE_DIR, 'static', 'mfa')

# Installed Applications
INSTALLED_APPS = [
    # Admin Interface Styling
    'jazzmin',
    'django.contrib.admin',

    # Standard Django Apps
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-Party Packages
    'oauth2_provider',
    'mfa',
    'mptt',
    'haystack',
    'widget_tweaks',
    'django_recaptcha',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Machina Forum Apps
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

    # Local Apps
    'chat',
    'elitedevelop',
    'qr_generator',
    'proxy',
    'ai',
    'eliteos',
    'gaming',
    'collabs',
    'forms',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth & Social Account Setup
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# MFA Configuration
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
U2F_APPID = f"https://{MFA_DOMAIN}"
FIDO_SERVER_ID = MFA_DOMAIN
FIDO_SERVER_NAME = "EliteDevelop"
MFA_SITE_TITLE = "EliteDevelop"
MFA_OWN_DELETE = True
MFA_TRUSTED_DEVICE_COOKIE_NAME = "mfa_trusted_device"
MFA_TRUSTED_DEVICE_AGE = 30
MFA_REDIRECT_AFTER_REGISTRATION = "home"
TOKEN_ISSUER_NAME = "EliteDevelop"
MFA_LOGIN_CALLBACK = 'elitedevelop.views.login_view'
RECOVERY_COUNTERS = 5

# Unfold Admin Theme Settings
UNFOLD = {
    "SITE_TITLE": "EliteDevelop Administration",
    "SITE_HEADER": "EliteDevelop",
    "SITE_URL": "/",
    "DASHBOARD_CALLBACK": "elitedevelop.admin_dashboard.get_dashboard_context",
}

# OAuth2 Settings
OAUTH2_PROVIDER = {
    'PKCE_REQUIRED': False,
    'ERROR_RESPONSE_WITH_SCOPES': True,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 36000,
    'RESOURCE_SERVER_AUTH_TOKEN_INTROSPECTION_URL': 'https://elitedevelop.pythonanywhere.com/o/introspect/',
}

# Middleware Pipeline
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
    "elitedevelop.middleware.OrganizationIdentityMiddleware",
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

# Search & Caches
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

# Machina Forum Settings
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

# Authentication Redirects
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Localization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static & Media Files Configuration (PythonAnywhere & WhiteNoise Compatible)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Source directory for project-level static assets
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Output directory for collectstatic (WhiteNoise reads from here)
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = '/home/elitedevelop/elitedevelop/media'

# Django 4.2+ Storage Configuration for WhiteNoise
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging Configuration
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