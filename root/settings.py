"""
Django settings for root project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import raven
import zipfile
from common.utils import create_uuid_filename

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_TITLE = 'Feedmee'
PROJECT_TITLE_ABBR = 'FM'

UBER = {'clientid': 'eKsp3zbX6lPB_S1_aU4KDwWryKmMGWvt'}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

LOGIN_REDIRECT_URL = '/admin/'
HIJACK_LOGIN_REDIRECT_URL = '/api/dishes/'
HIJACK_ALLOW_GET_REQUESTS = True

# SECURITY WARNING: don't run with debug turned on in production!
if os.environ['DEPLOYMENT'] != 'PRODUCTION':
    DEBUG = True
    ALLOWED_HOSTS = [
        '.us-west-2.elasticbeanstalk.com',
        'localhost',
        'localhost:8000',
        '.localhost.com',
        '.feedmeetastycode.click',
    ]
else:
    ALLOWED_HOSTS = [
        '.us-west-2.elasticbeanstalk.com',
        '.feedmeeapp.com',
        'use.feedmeeapp.com',
    ]
    if os.environ.get('ROLE') == 'WORKER':
        ALLOWED_HOSTS += ['127.0.0.1', 'localhost', '.elasticbeanstalk.com']
    else:
        SECURE_SSL_REDIRECT = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_HSTS_SECONDS = 300

TMP_PATH = 'tmp/' if os.environ['DEPLOYMENT'] == 'LOCAL' else '/tmp/'

CITIES_DATA_DIR = TMP_PATH+'/cities/data'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'webapp',
    'blog',
    'crispy_forms',
    'main',
    'api',
    'data_entry',
    'django_social_share',
    'hijack',
    'hijack_admin',
    'compat',
    'fixture_magic',
    'bootstrap3',
    'timezone_field',
    'dbbackup',
    'storages',
    'rest_framework',
    'corsheaders',
    's3direct',
    'raven.contrib.django.raven_compat',
    'better_filter_widget',
    'ckeditor',
    'django_sqs_jobs',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.sites',
    'django.contrib.flatpages',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.authentication.FirebaseJWTBackend',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'PAGE_SIZE': 20
}

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'subdomains.middleware.SubdomainURLRoutingMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.middleware.useragent.CustomUserAgentMiddleware',
    'common.middleware.deeplink.DeeplinkMiddleware',
]

def get_git_sha_from_sourcebundle():
    if os.environ['DEPLOYMENT'] == 'LOCAL':
        return raven.fetch_git_sha(os.path.dirname(os.pardir))
    else:
        path = '/opt/elasticbeanstalk/deploy/appsource/source_bundle'
        with zipfile.ZipFile(path) as z:
            return z.comment


if os.environ['DEPLOYMENT'] != 'LOCAL':
    RAVEN_CONFIG = {
        'dsn': 'https://344e9f25ef874f9289508c808589fa29:b114a3d14ebc4e2b92eb1bafe0b0c76d@sentry.io/170522',
        'release': get_git_sha_from_sourcebundle(),
        'environment': os.environ['DEPLOYMENT'],
        'ignore_exceptions': ['django.exceptions.http.Http404']
    }

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',  # ERROR, WARNING, INFO, etc.
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }

DEEPLINKER = {
    'USER_AGENTS': {
        'device': {
            'family': ['iPhone', 'iOS-Device']
        }
    },
    'URL_MODULE': 'webapp.deeplinks',
    'PROTOCOL': 'feedmee://',
}

# CORS for select endpoints.
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/donations/$'

# GOOGLE API
GOOGLEMAPS_API = {
    'key': 'AIzaSyDRrMIIWKhaei6Orp5q6Cnhn0lWdJLgM0o'
}

ROOT_URLCONF = 'root.urls'

SUBDOMAIN_URLCONFS = {
    'www': 'webapp.urls',
    'api': 'api.urls',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'root.context_processors.project_config',
                'common.middleware.deeplink.context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'root.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD'],
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT']
    }
}


FIREBASE_JWT_BACKEND = {
    'target_audience': 'feedmee-appsppl-dev',
    'cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = (
    'ratelimitbackend.backends.RateLimitModelBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Worker jobs system
SQS_JOBS = {
    'access_key': os.environ.get('AWS_S3_STATIC_ID', 'AKIAIUW5JZYOGAZBWA5Q'),
    'secret_key': os.environ.get('AWS_S3_STATIC_KEY',
                                 'kJGEvPxtm9aeQnrG0zyG6iJlL3FbTYBY5KpEJe2z'),
    'region_name': 'us-west-2',
    'queue_name': os.environ.get('SQS_WORKER_QUEUE_NAME', 'TestQueue'),
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
if os.environ['DEPLOYMENT'] == 'PRODUCTION':
    AWS_STORAGE_BUCKET_NAME = 'fdme-static'
else:
    AWS_STORAGE_BUCKET_NAME = 'fdme-static-dev'
AWS_ACCESS_KEY_ID = os.environ['AWS_S3_STATIC_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_S3_STATIC_KEY']

AWS_STORAGE_RAWIMG_BUCKET_NAME = 'fdme-raw-img'
S3DIRECT_REGION = 'us-west-2'
S3DIRECT_DESTINATIONS = {
    'raw-img': {
        # REQUIRED
        'key': create_uuid_filename,
        # OPTIONAL
        'auth': lambda u: u.is_staff,
        'allowed': ['image/jpeg', 'image/png'],  # Default allow all mime types
        'bucket': 'fdme-raw-img',  # Default is 'AWS_STORAGE_BUCKET_NAME'
        'content_length_range': (5000, 20000000),  # Default allow any size
    }
}


# Tell django-storages that when coming up with the URL for an item in S3 storage,
# keep it simple - just use this domain plus the path. (If this isn't set,
# things get complicated).
# This controls how the `static` template tag from `staticfiles` gets expanded,
# if you're using it.
# We also use it in the next setting.
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# This is used by the `static` template tag from `static`, if you're using that.
#  Or if anything else refers directly to STATIC_URL. So it's safest to always set it
# STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

if os.environ['DEPLOYMENT'] != 'LOCAL':
    STATICFILES_LOCATION = 'static'
    STATICFILES_STORAGE = 'custom_storages.StaticStorage'
    if os.environ['DEPLOYMENT'] == 'PRODUCTION':
        STATIC_URL = 'https://cdn.feedmeeapp.com/%s/' % STATICFILES_LOCATION
    else:
        STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)

    MEDIAFILES_LOCATION = 'media'
    MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
    DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
else:
    STATIC_URL = '/static/'

STATICFILES_DIRS = (
    'common-static/',
)
CDN_URL = 'https://cdn.feedmeeapp.com/images/'
# Tell the staticfiles app to use S3Boto storage when writing the collected static
# files (when you run `collectstatic`).
# STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

DBBACKUP_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

DBBACKUP_STORAGE_OPTIONS = {
    'access_key': AWS_ACCESS_KEY_ID,
    'secret_key': AWS_SECRET_ACCESS_KEY,
    'bucket_name': 'fdme-dbbackup'
}

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

TEST_RUNNER = 'root.test_runner.FastTestRunner'
