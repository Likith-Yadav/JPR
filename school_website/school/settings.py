# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'school',  # add your app name here
]

# Add login URL
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
] 