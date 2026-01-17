#!/bin/bash

# Navigate to the Django project directory
cd alx_travel_app

# Start Celery worker in the background
# Using '&' allows the script to continue to the next command
celery -A alx_travel_app worker -l info &

# Start Gunicorn in the foreground
# This keeps the container alive and serving web requests
gunicorn alx_travel_app.wsgi --bind 0.0.0.0:$PORT
