"""
Django settings for listener project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load env variables from .env
from dotenv import load_dotenv
import os

load_dotenv(BASE_DIR / "../.env")

import dj_database_url

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-ngrb5dzqrhnr48a7fzl19a72pc##!)d#95h74)h7y7a39rq!x@",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "127.0.0.1 localhost").split(" ")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_extensions",
    "rest_framework",
    "authuser",
    "recordings",
]


AUTH_USER_MODEL = "authuser.User"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "server.wsgi.application"


# Database
# Use dj_database_url for url management.

import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=f'spatialite:///{BASE_DIR / "db.sqlite3"}'
    )
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

STATICFILES_DIRS = [
    # BASE_DIR / "static",
    "/usr/src/app/staticfiles/",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Where the system looks for new WAV files.
# NOTE: WAV files that not return detections are permanently deleted!
INGEST_WAV_FILE_DIRECTORY = os.environ.get(
    "INGEST_WAV_FILE_DIRECTORY",
    "/usr/audio/incoming",
)

# Where the system copies the WAV files IF AND ONLY IF detections are returned for the recording.
# NOTE: WAV files that not return detections are permanently deleted!
OUTPUT_WAV_FILE_DIRECTORY = os.environ.get(
    "OUTPUT_WAV_FILE_DIRECTORY",
    "/usr/audio/analyzed",
)

# If True, system will extract the detection and add it to the detection obj as an MP3 file.
DETECTION_EXTRACTION_ENABLED = os.environ.get(
    "DETECTION_EXTRACTION_ENABLED",
    True,
)
DETECTION_EXTRACTION_BITRATE = os.environ.get(
    "DETECTION_EXTRACTION_BITRATE",
    320,
)
DETECTION_CONFIDENCE_THRESHOLD = float(
    os.environ.get(
        "DETECTION_CONFIDENCE_THRESHOLD",
        0.7,
    )
)

DOMAIN = os.environ.get(
    "SITE_DOMAIN",
    "example.com",
)


FLICKR_BLACKLIST_IDS = os.environ.get("FLICKR_BLACKLIST_IDS", "").split(" ")
FLICKR_KEY = os.environ.get("FLICKR_KEY")
FLICKR_SECRET = os.environ.get("FLICKR_SECRET")
FLICKR_RESULTS_LIMIT_PER_SPECIES = 5


# Light-weight, only really for Flickr image urls.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "birds-cache",
    }
}

OPENWEATHERAPI_KEY = os.environ.get("OPENWEATHERAPI_KEY")

LONGITUDE = os.environ.get("LONGITUDE")
LATITUDE = os.environ.get("LATITUDE")
PLACE_NAME = os.environ.get("PLACE_NAME")
WEATHER_CACHE_SECONDS = 60 * 10

KIOSK_DETECTIONS_NOW_MINUTES = int(
    os.environ.get("KIOSK_DETECTIONS_NOW_MINUTES", 5)
)  # The number of minutes a detection will be considered a NOW! detections.
