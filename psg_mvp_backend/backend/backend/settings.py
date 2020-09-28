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
ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '206.189.218.129', '157.245.3.246']

# CORS_REPLACE_HTTPS_REFERER = False
# HOST_SCHEME = "http://"
# SECURE_PROXY_SSL_HEADER = None

SESSION_COOKIE_SECURE = False

# ----- open this for SSL ----
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
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
    'comments'
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

# media storage configuration
MEDIA_ROOT = os.path.join(TOP_DIR, 'media')
MEDIA_URL = '/media/'

# for catalog
FIXTURE_ROOT = os.path.join(TOP_DIR, 'fixtures')

# Extended User Auth Model
AUTH_USER_MODEL = 'users.User'

SITE_ID = 1

# Django Email backend Settings.
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'tmp/email')

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
    'PAGE_SIZE': 20    # TODO: to-be-decided
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

# TODO: remove this
ES_HOST = 'elasticsearch'
ES_PORT = 9200


# for cors
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    "localhost:4200",
]


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
GOOGLE_MAP_API_KEY = 'AIzaSyDDbkqc3aU4LvKFU_78HgGoJMqY_5e-t1s' # TODO: remove this
