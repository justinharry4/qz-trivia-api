import dj_database_url
from dotenv import load_dotenv

from .common import *

load_dotenv()

DEBUG = True

SECRET_KEY = "django-insecure-wj(a@$0s!+^-^2k6f$j355s_98$_!28v#b-ynrwzcqyemj7adu"

ALLOWED_HOSTS = []

INTERNAL_IPS = ["127.0.0.1"]

CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

# Local SQLite Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Local MySQL Database

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "qz",
#         "USER": "root",
#         "PASSWORD": "Svenburg@7",
#         "HOST": "127.0.0.1",
#     }
# }


# Remote Postgres Database

# DATABASES = {
#     "default": dj_database_url.config()
# }