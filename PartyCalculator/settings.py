"""
Django settings for PartyCalculator project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import dj_database_url
from decouple import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '82ud!#rl#%@3_^p9!l&m2zy#l9=!32op3s0oxs=gk(a%ru4wx8'

PROTOCOL = 'http://'
HOST = 'localhost:8000'
WEBSITE_URL = PROTOCOL + HOST

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
  'partycalculator.herokuapp.com',
  'localhost',
  '127.0.0.1'
]


# Application definition

INSTALLED_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',

  'social_django',

  'party_calculator',
  'authModule',
]

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',

  'whitenoise.middleware.WhiteNoiseMiddleware',
  'social_django.middleware.SocialAuthExceptionMiddleware',
]

AUTHENTICATION_BACKENDS = (
  'social_core.backends.google.GoogleOAuth2',
  'social_core.backends.github.GithubOAuth2',
  'social_core.backends.twitter.TwitterOAuth',
  'social_core.backends.facebook.FacebookOAuth2',

  'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'PartyCalculator.urls'

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

        'social_django.context_processors.backends',
        'social_django.context_processors.login_redirect',
     ],
    },
  },
]

WSGI_APPLICATION = 'PartyCalculator.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
  # 'default': dj_database_url.config(
  #   default=config('DATABASE_URL')
  # )
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'HOST': 'localhost',
    'NAME': 'PartyCalculator',
    'PORT': 5432,
    'USER': 'postgres',
    'PASSWORD': 'admin',
    'DATABASE': 'PartyCalculator'
  }
  # 'default': {
  #     'ENGINE': 'django.db.backends.postgresql',
  #     'NAME': 'postgres',
  #     'USER': 'postgres',
  #     'HOST': 'db',
  #     'PORT': 5432,
  # }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
  {
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
  },
  {    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
  },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_ROOT = os.path.join('static')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
# STATICFILES_DIRS = (
#     os.path.join('static'),
# )
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'


# REDIS related settings
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_BROKER_URL = BROKER_URL
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'


# EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Django social OAuth app
SOCIAL_AUTH_USER_MODEL = "authModule.Profile"
SOCIAL_AUTH_REVOKE_TOKENS_ON_DISCONNECT = True
SOCIAL_AUTH_LOGIN_ERROR_URL = '/settings/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False


SOCIAL_AUTH_GITHUB_KEY = os.environ.get('SOCIAL_AUTH_GITHUB_KEY', None)
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get('SOCIAL_AUTH_GITHUB_SECRET', None)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', None)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', None)

SOCIAL_AUTH_PIPELINE = (
  'social_core.pipeline.social_auth.social_details',
  'social_core.pipeline.social_auth.social_uid',
  'social_core.pipeline.social_auth.social_user',
  # 'social_core.pipeline.user.get_username',
  'social_core.pipeline.user.create_user',
  'social_core.pipeline.social_auth.associate_user',
  'social_core.pipeline.social_auth.load_extra_data',
  'social_core.pipeline.user.user_details',
  'social_core.pipeline.social_auth.associate_by_email',
)


# Google reCAPTCHA
GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get('GOOGLE_RECAPTCHA_SITE_KEY', None)
GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get('GOOGLE_RECAPTCHA_SECRET_KEY', None)