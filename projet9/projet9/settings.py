# -*- coding: utf-8 -*-
import os
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# This is new:


PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(PROJECT_DIR)
APPS_DIR = os.path.realpath(os.path.join(ROOT_DIR, "oc-projet-9"))
sys.path.append(APPS_DIR)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "core",
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

INTERNAL_IPS = ("127.0.0.1:8000", "127.0.0.1")
ROOT_URLCONF = "projet9.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "core", "templates/core/"),
            os.path.join(
                os.path.join(BASE_DIR, "frontend", "templates/frontend/core/"),
                "authentication",
            ),
            os.path.join(BASE_DIR, "core", "templates/core/pannels"),
        ],
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


LOGIN_URL = "core.login_view"
LOGIN_REDIRECT_URL = "core.login_view"
LOGOUT_REDIRECT_URL = "core.login_view"

WSGI_APPLICATION = "projet9.wsgi.application"
ASGI_APPLICATION = "projet9.asgi.application"
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
}


"""
    SESSIONS
"""
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 18000  # 5 hours
# SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"

"""
    COOKIES POLICIES
"""
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

"""
    X FRAME
"""
X_FRAME_OPTIONS = "SAMEORIGIN"

"""
    NOSNIF : PERMIT TO WEBNAV TO GUESS WHAT KIND OF FILE YOU RUN.
"""
SECURE_CONTENT_TYPE_NOSNIFF = False


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR + "/db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


SECRET_KEY = (
    "django-insecure-k1-3qmw*duh-f_uhso9gugv$f6af0n4vq_c1mbc00(3g6i30(l"
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "core" + STATIC_URL),
]
STATIC_ROOT = os.path.join(BASE_DIR, "projet9" + STATIC_URL)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "core" + MEDIA_URL)


"""
    JSON FIXTURES
"""
FIXTURE_DIRS = [
    BASE_DIR + "/core/fixtures/user.json",
    BASE_DIR + "/core/fixtures/review.json",
    BASE_DIR + "/core/fixtures/userfollows.json",
    BASE_DIR + "/core/fixtures/ticket.json",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if __name__ == "__main__":
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet9.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    django.setup()
