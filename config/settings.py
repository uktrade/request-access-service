import os
import dj_database_url
import environ
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (os.getenv('SECRET_KEY'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if (os.getenv('DEBUG') == 'true') else False


ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'govuk_template_base',
    'govuk_forms',
    'ras_app_template',
    'ras_app',
    'authbroker_client',
    'user',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ras_app.middleware.AdminIpRestrictionMiddleware',
    'core.middleware.ProtectAllViewsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'govuk_template_base.context_processors.govuk_template_base',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config()
}

AUTHENTICATION_BACKENDS = [
    'authbroker_client.backends.AuthbrokerBackend',
]

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

LANGUAGE_CODE = 'en-uk'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'user.User'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

GOVUK_SERVICE_SETTINGS = {
    'name': 'DIT Request Access Service',
    'phase': 'alpha',
    'header_link_view_name': 'home_page',
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

GOV_NOTIFY_API_KEY = os.getenv('GOV_NOTIFY_API_KEY')
EMAIL_UUID = os.getenv('EMAIL_UUID')
EMAIL_REQUESTOR_UUID = os.getenv('EMAIL_REQUESTOR_UUID')
EMAIL_ACTIVATE_UUID = os.getenv('EMAIL_ACTIVATE_UUID')
EMAIL_COMPLETED_UUID = os.getenv('EMAIL_COMPLETED_UUID')
EMAIL_OFFBOARD_UUID = os.getenv('EMAIL_OFFBOARD_UUID')
EMAIL_ENDUSER_UUID = os.getenv('EMAIL_ENDUSER_UUID')
EMAIL_TEST_SMOKE = os.getenv('EMAIL_TEST_SMOKE', False)
EMAIL_TEST_NOTIFY_ADDRESS = os.getenv('EMAIL_TEST_NOTIFY_ADDRESS', '')
EMAIL_TEST_ADDRESS = os.getenv('EMAIL_TEST_ADDRESS', '')
LOGIN_REDIRECT_URL = 'login-redirect'
LOGIN_URL = '/auth/login/'
AUTHBROKER_URL = os.getenv("AUTHBROKER_URL")
AUTHBROKER_CLIENT_ID = os.getenv("AUTHBROKER_CLIENT_ID")
AUTHBROKER_CLIENT_SECRET = os.getenv("AUTHBROKER_CLIENT_SECRET")
AUTHBROKER_SCOPES = "read write"
RESTRICT_ADMIN = env.bool("RESTRICT_ADMIN", True)
ALLOWED_ADMIN_IPS = env.list("ALLOWED_ADMIN_IPS")
IP_PROTECT_PATH = "/home/"
DOMAIN_NAME = os.getenv("DOMAIN_NAME")
SSO_INTROS_TOKEN = os.getenv("SSO_INTROS_TOKEN")
SERVICES = os.getenv("SERVICES")
TEAMS = os.getenv("TEAMS")
GIT_TAG = os.getenv("GIT_TAG")
