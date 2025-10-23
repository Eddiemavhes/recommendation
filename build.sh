#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Python version:"
python --version

echo "Current working directory:"
pwd

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Database URL (censored):"
echo ${DATABASE_URL:0:20}...

echo "Collecting static files..."
export DJANGO_SETTINGS_MODULE=job_matcher.production
echo "Creating staticfiles directory..."
mkdir -p staticfiles
python manage.py collectstatic --no-input -v 2

echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
python manage.py migrate --plan
python manage.py migrate