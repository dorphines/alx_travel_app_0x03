#!/bin/bash

# Navigate to the directory containing manage.py
# The repo root contains 'alx_travel_app/' folder which contains 'manage.py'
cd alx_travel_app

# Run database migrations
echo "--- Running Migrations ---"
python manage.py migrate --no-input

# Start Celery worker in the background
echo "--- Starting Celery Worker ---"
celery -A alx_travel_app worker -l info &

# Start Gunicorn in the foreground
echo "--- Starting Gunicorn ---"
gunicorn alx_travel_app.wsgi --bind 0.0.0.0:$PORT

