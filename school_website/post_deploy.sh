#!/bin/bash

# Run migrations
python manage.py migrate

# Load initial data
python manage.py loaddata fixtures/initial_data.json

# Collect static files
python manage.py collectstatic --noinput 