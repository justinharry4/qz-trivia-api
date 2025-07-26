import os
import dj_database_url
from .common import *


DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = ["qz-trivia-api.onrender.com"]

CORS_ALLOWED_ORIGINS = []

DATABASES = {
    "default": dj_database_url.config()
}