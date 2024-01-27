from pathlib import Path
import os
from datetime import timedelta 
import dj_database_url
import environ
import boto3
from rest_framework_simplejwt import token_blacklist
import logging


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'RENDER' not in os.environ

SECRET_KEY = os.environ.get('SECRET_KEY', default=os.environ['SECRET_KEY'])

ALLOWED_HOSTS = [
    'https://www.softtennis-ace-review.com',
    'https://softtennis-ace-review.com',
    'https://www.soft-tennis-star-review.com',
    'https://soft-tennis-star-review.com',
    'softtennis-ace-review.com',
    'soft-tennis-star-review.com',
]

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'review',
    'account',
    'item',
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework_simplejwt.token_blacklist',
    'storages',
    'djoser',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CSRF_TRUSTED_ORIGINS = [
    'https://www.softtennis-ace-review.com',
    'https://softtennis-ace-review.com',
]

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = [
    'https://www.softtennis-ace-review.com',
    'https://softtennis-ace-review.com',
]

CORS_ALLOWED_ORIGINS = [
    'https://www.softtennis-ace-review.com',
    'https://softtennis-ace-review.com',
]

ROOT_URLCONF = 'reviewsite.urls'

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

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

WSGI_APPLICATION = 'reviewsite.wsgi.application'

DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DATETIME_FORMAT': '%Y/%m/%d %H:%M',
}


JWT_AUTH_SECURE = True
JWT_AUTH_SAMESITE = 'None'
SECURE_SSL_REDIRECT = True

JWT_AUTH = {
    'JWT_VERIFY_EXPIRATION': True,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_NAME': "HTTP_AUTHORIZATION",
    'AUTH_HEADER_TYPES': ('JWT','Bearer'),
    'AUTH_COOKIE_HTTP_ONLY': True,
}

AUTH_USER_MODEL = 'account.CustomUser'

# AWS-Settings
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_LOCATION = 'static' # s3バケット上のベースとなるファイルパス
AWS_S3_REGION_NAME=os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_URL = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_SIGNATURE_VERSION = 's3v4'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static'),
]

AWS_QUERYSTRING_AUTH = True
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
AWS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
}

STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_ROOT = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/{MEDIAFILES_LOCATION}/'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
STATIC_ROOT = 'https://%s/%s/static/' % (AWS_S3_CUSTOM_DOMAIN,STATICFILES_LOCATION)

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "file_overwrite": False,
            "default_acl": None,
            "querystring_auth": False,
            "object_parameters": {
                "CacheControl": "max-age=86400",
            },
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SUPERUSER_EMAIL = env('SUPERUSER_EMAIL')
SUPERUSER_PASSWORD = env('SUPERUSER_PASSWORD')

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logfile.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}

logger = logging.getLogger(__name__)
logger.debug(f"DEBUG mode is {'on' if DEBUG else 'off'}")