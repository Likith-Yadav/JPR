"""
WSGI config for school_website project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if dotenv is available
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / '.env'
    load_dotenv(env_path)
except ImportError:
    # If dotenv is not available, continue without loading .env file
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_website.settings')

application = get_wsgi_application()
