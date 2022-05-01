"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from pathlib import Path

from django.urls import reverse_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOP_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hck+)fy3p9x789tx(x^-j*^!8ylg*e-n=lkh5*3zs^k&f$)h_='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# TODO: remove hard-coded front/backend IPs
ALLOWED_HOSTS = ['0.0.0.0', 'localhost', 'api.surgi.fyi', 'www.api.surgi.fyi', 'surgi.fyi', 'www.surgi.fyi', '206.189.218.129', '157.245.3.246', '167.172.201.138']
# For Algolia indexing
ALGOLIA_CASE_INDEX = 'cases-prod'
ALGOLIA_CLINIC_INDEX = 'clinics-brief-prod'
ALGOLIA_REVIEW_INDEX = 'reviews-prod'
ROOT_URL = 'https://api.surgi.fyi'



# CORS_REPLACE_HTTPS_REFERER = False
# HOST_SCHEME = "http://"
# SECURE_PROXY_SSL_HEADER = None

# SESSION_COOKIE_SECURE = False

# ----- open this for SSL ----
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# ----------------------------

# SECURE_HSTS_SECONDS = None
# SECURE_HSTS_INCLUDE_SUBDOMAINS = False
# SECURE_FRAME_DENY = False


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # --- django extensions ---
    'django_extensions',
    # 'phonenumber_field',
    # --- django REST framework ---
    'rest_framework',
    # --- REST documentation ---
    'rest_framework_swagger',
    # --- to solve CORS ---
    'corsheaders',
    # --- registration app ---
    'rest_framework.authtoken',
    'rest_auth',
    'django.contrib.sites',
    # --- act stream ---
    'actstream',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'allauth.socialaccount',
    # ... include the providers you want to enable:
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    # --- django imagekit package ---
    'imagekit',
    # --- django fileField auto clean up ---
    'django_cleanup.apps.CleanupConfig',
    # --- tagging system (django-taggit) ---
    # 'taggit',
    # --- tags app ---
    'tags',
    # --- users app ---
    'users',
    # --- cases app ---
    'cases',
    # --- reviews app ---
    'reviews',
    # --- comments app ---
    'comments',
    # --- hit come for cases ---
    'hitcount'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': 'cache:11211',
        'TIMEOUT': 86400,  # 1 day, default to 300 (5 mins)
        # 'OPTIONS': {
        #     'MAX_ENTRIES': 500
        # }
    }
}

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # specify dir to loop up templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'ENFORCE_SCHEMA': False,
        'NAME': 'core_db',
        # 'USER': os.environ.get('MONGO_USER'),
        # 'PASSWORD': os.environ.get('MONGO_PW'),
        'USER': 'fxehty2019',
        'PASSWORD': 'psgmvp2019',
        'HOST': 'mongo',
        'PORT': 27017,
        'AUTH_SOURCE': 'core_db',
        # 'AUTH_MECHANISM': 'SCRAM-SHA-1'
    }

    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(TOP_DIR, 'static')
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(TOP_DIR, 'backend/static/email_imgs')
]

# STATIC_ROOT = ''
#
# STATIC_URL = '/static/'
#
# STATICFILES_DIRS = ( os.path.join(TOP_DIR, 'static'), )


# print("dfd", os.path.join(TOP_DIR, 'static'))

# media storage configuration
MEDIA_ROOT = os.path.join(TOP_DIR, 'media')
MEDIA_URL = '/media/'

# for catalog
FIXTURE_ROOT = os.path.join(TOP_DIR, 'fixtures')

# Extended User Auth Model
AUTH_USER_MODEL = 'users.User'

SITE_ID = 1

# Django Email backend Settings.
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'tmp/email')

# TODO: WIP, not working

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'notifications@surgi.fyi'
# EMAIL_HOST_PASSWORD = 'jagp%%eh475'  # fill in the real pw  #TODO: read from env
EMAIL_HOST_PASSWORD = 'xkuoacxlivwyzttl'
# EMAIL_HOST_PASSWORD = 'zxnhvjvjttnbyjks' #past the key or password app here
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Surgi.fyi'
EMAIL_USE_SSL = False
# self defined
EMAIL_WITH_DISPLAY_NAME = 'Surgi <%s>' % EMAIL_HOST_USER
BCC_EMAIL = 'nancy@surgi.fyi'
###################################
#     django-alluth seetings
###################################
# disable default regis confirm email from django-alluth
# as we'll send out our own.
ACCOUNT_EMAIL_VERIFICATION = 'none'

# django-rest-framework settings
ES_PAGE_SIZE = 16  # for ES pagination

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',  # must set this for django_rest_auth
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    # filtering settings
    # 'DEFAULT_FILTER_BACKENDS': (
    #     'django_filters.rest_framework.DjangoFilterBackend',
    # ),
    # pagination settings
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    # 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20  # TODO: to-be-decided
}

# django-rest-auth configuration
REST_AUTH_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'users.serializers.RegisterSerializerEx',
}

# django_rest_auth configuration
# Doc: http://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Login/logout url configuration
# LOGOUT_REDIRECT_URL = reverse_lazy('swagger-root')
LOGIN_URL = reverse_lazy('rest_login')
LOGOUT_URL = reverse_lazy('rest_logout')

# Swagger settings
# SWAGGER_SETTINGS = {
#     # A list URL namespaces to ignore
#     "exclude_namespaces": ["internal_apis"],
#     "exclude_url_names": ['swagger-root']
# }


###################################
#     Elastic Search Instance
###################################
# ES_HOST = os.environ.get('ES_HOST')
# ES_PORT = os.environ.get('ES_PORT')

ES_HOST = 'elasticsearch'
ES_PORT = 9200

# for cors (dev mode)
# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = [
#     "localhost:4200",
# ]

# for SSL/HTTPS
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ['surgi.fyi', 'api.surgi.fyi:443', '.surgi.fyi', 'api.surgi.fyi']

CORS_REPLACE_HTTPS_REFERER = True
CSRF_COOKIE_DOMAIN = 'surgi.fyi'
CORS_ORIGIN_WHITELIST = (
    'https://surgi.fyi/',
    'surgi.fyi',
    'https://api.surgi.fyi',
    'api.surgi.fyi',
    'https://167.172.201.138:1668',  # for Scully JK build
    'https://167.172.201.138:1864'   # for Scully JK build
)


###################################
#         activity stream
###################################
# set this to true to pass extra metadata in actions.
ACTSTREAM_SETTINGS = {
    'USE_JSONFIELD': True
}

###################################
#          3rd party api
###################################
# Google Map API key (project mvp1).
# You can enable more API services under this key in Google's console.
GOOGLE_MAP_API_KEY = 'AIzaSyDDbkqc3aU4LvKFU_78HgGoJMqY_5e-t1s'  # TODO: remove this

###################################
#            Celery
###################################
# CELERY_BROKER_URL = 'redis://:p6fd93ffd394f708a7a39d4b61715309ae6d6625e42ce95d3e8771507e2ede6a3@ec2-54-243-217-95.compute-1.amazonaws.com:22449'
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
# Try 5 times. Initially try again immediately, then add 0.5 seconds for each
# subsequent try (with a maximum of 3 seconds). This comes out to roughly 3
# seconds of total delay (0, 0.5, 1, 1.5).
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries': 4,
    'interval_start': 0,
    'interval_step': 0.5,
    'interval_max': 3,
}

######################################
#        Django Social Auth
######################################
# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': '121687132886949',
            'secret': '28add9a23fb07d0021f13cc0f5cf0593',
            'key': ''
        }
    },
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': '232549874732-20604rkt81d9rkkt6u57rhi1rmurv3b0.apps.googleusercontent.com',
            'secret': 'h7Z-XHmxvgfTS1peo9gitWLV',
            'key': ''
        }
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["file"]},
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/var/log/django.log",
            "formatter": "app",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True
        },
    },
    "formatters": {
        "app": {
            "format": (
                u"%(asctime)s [%(levelname)-8s] "
                "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}

ACCOUNT_EMAIL_REQUIRED = True

# frontend
URL_FRONT = 'surgi.fyi'


########################
#   Hit Count Config
########################
HITCOUNT_KEEP_HIT_ACTIVE = { 'minutes': 3 }


########################
#       Algolia
########################
ALGOLIA_APP_ID = '59Z1FVS3D5'
ALGOLIA_SECRET = '7a3a8ca34511873b56938d40f34b125d'
ALGOLIA_ANALYTIC_KEY = 'cd669799ffe33b273991d0c1495740e5'
