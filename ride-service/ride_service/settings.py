"""
Django settings for ride_service project (Microservice Ride).
"""

from pathlib import Path
import os

# -------------------------------
# BASE DIR
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------
# SECURITY
# -------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-51n-i1obuyx^8!dex)y0%0)tfbi3@qy6(8*+pcs!49_#%y$5%0')
DEBUG = os.getenv("DEBUG", "1") == "1"

ALLOWED_HOSTS = ["*"]

# -------------------------------
# INSTALLED APPS
# -------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',

    # Local apps
    'rides',
]

# -------------------------------
# MIDDLEWARE
# -------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 🔥 ADD JWT VERIFICATION MIDDLEWARE HERE
    'ride_service.auth_middleware.jwt_verification_middleware',
]

ROOT_URLCONF = 'ride_service.urls'

# -------------------------------
# TEMPLATES (not used but required)
# -------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ride_service.wsgi.application'

# -------------------------------
# DATABASE
# Default SQLite for dev
# Use PostgreSQL in production
# -------------------------------
DATABASES = {
    'default': {
        'ENGINE': os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        'NAME': os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        'USER': os.getenv("DB_USER", ""),
        'PASSWORD': os.getenv("DB_PASSWORD", ""),
        'HOST': os.getenv("DB_HOST", ""),
        'PORT': os.getenv("DB_PORT", ""),
    }
}

# -------------------------------
# PASSWORDS (not used)
# -------------------------------
AUTH_PASSWORD_VALIDATORS = []

# -------------------------------
# LANGUAGE + TIMEZONE
# -------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------------
# STATIC FILES
# -------------------------------
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# 🔵 MICROSERVICE COMMUNICATION CONFIG
# ============================================================

# -------------------------------
# AUTH SERVICE URL
# -------------------------------
# For Docker/Production: use service name
# AUTH_VERIFY_URL = "http://auth-service:8000/accounts/api/verify/"

# For Local Development: use localhost with port
AUTH_VERIFY_URL = os.getenv(
    "AUTH_VERIFY_URL",
    "http://localhost:8000/accounts/api/verify/"
)

# -------------------------------
# RABBITMQ (for later)
# -------------------------------
RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://guest:guest@rabbitmq:5672/"
)

# -------------------------------
# REST FRAMEWORK
# -------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Will be overridden per view
    ]
}