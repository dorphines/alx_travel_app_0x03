#!/usr/bin/env bash
# exit on error
set -o errexit

# Navigate to the Django project directory
cd alx_travel_app

echo "Applying database migrations..."
python manage.py migrate

echo "Pre-deployment tasks completed."
