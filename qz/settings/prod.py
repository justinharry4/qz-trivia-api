import os
import dj_database_url
from .common import *


DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY")

ALLOWED_HOSTS = [os.environ.get("SITE_HOST_NAME")]

CORS_ALLOWED_ORIGINS = [os.environ.get("CLIENT_URL")]

DATABASES = {"default": dj_database_url.config()}
